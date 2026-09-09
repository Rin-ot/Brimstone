import discord
from discord.ext import commands
from discord import app_commands
import random
from typing import List

class TeamPanel(discord.ui.View):
    def __init__(self, num_teams: int, interaction: discord.Interaction):
        super().__init__(timeout=None)
        self.num_teams = num_teams
        self.original_interaction = interaction
        self.teams = {i: [] for i in range(num_teams)}
        
        # チーム参加ボタンを動的に追加
        for i in range(num_teams):
            btn = discord.ui.Button(label=f"チーム {i+1} に参加", style=discord.ButtonStyle.primary, custom_id=f"join_team_{i}")
            btn.callback = self.make_join_callback(i)
            self.add_item(btn)
            
        # ランダム振り分けボタン
        random_btn = discord.ui.Button(label="ランダムチーム分け", style=discord.ButtonStyle.success, custom_id="random_split")
        random_btn.callback = self.random_split_callback
        self.add_item(random_btn)

    def make_join_callback(self, team_index: int):
        async def callback(interaction: discord.Interaction):
            user_name = interaction.user.display_name
            
            # 全チームからユーザーを一旦削除
            for t in self.teams.values():
                if user_name in t:
                    t.remove(user_name)
                    
            # 指定されたチームに追加
            self.teams[team_index].append(user_name)
            await self.update_panel(interaction)
        return callback

    async def random_split_callback(self, interaction: discord.Interaction):
        if not interaction.user.voice:
            await interaction.response.send_message("VCに入っていないためランダム振り分けの対象を取得できません。", ephemeral=True)
            return
            
        members = [m.display_name for m in interaction.user.voice.channel.members if not m.bot]
        if not members:
            await interaction.response.send_message("VCに誰もいません。", ephemeral=True)
            return
            
        random.shuffle(members)
        self.teams = {i: [] for i in range(self.num_teams)}
        
        for idx, m in enumerate(members):
            self.teams[idx % self.num_teams].append(m)
            
        await self.update_panel(interaction)

    async def update_panel(self, interaction: discord.Interaction):
        embed = discord.Embed(title="チーム分けパネル", description="ボタンを押してチームに参加するか、ランダム振り分けを行ってください。", color=discord.Color.blue())
        for i in range(self.num_teams):
            members_str = "\\n".join(self.teams[i]) if self.teams[i] else "なし"
            embed.add_field(name=f"チーム {i+1}", value=members_str, inline=False)
            
        await interaction.response.edit_message(embed=embed, view=self)


class ValorantCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="teams", description="チーム分けパネルを表示します")
    @app_commands.describe(num_teams="作成するチームの数（最大4）")
    async def teams(self, interaction: discord.Interaction, num_teams: int = 2):
        if num_teams < 2 or num_teams > 4:
            await interaction.response.send_message("チーム数は2から4の間で指定してください。", ephemeral=True)
            return
            
        embed = discord.Embed(title="チーム分けパネル", description="ボタンを押してチームに参加するか、ランダム振り分けを行ってください。", color=discord.Color.blue())
        for i in range(num_teams):
            embed.add_field(name=f"チーム {i+1}", value="なし", inline=False)
            
        view = TeamPanel(num_teams, interaction)
        await interaction.response.send_message(embed=embed, view=view)
        
    async def lfg_title_autocomplete(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
        presets = [
            "VALORANT コンペティティブ",
            "VALORANT アンレート",
            "VALORANT カスタム",
            "Apex Legends ランク",
            "Apex Legends カジュアル",
            "OW2 クイック",
            "OW2 ライバルプレイ",
            "雑談・その他"
        ]
        return [
            app_commands.Choice(name=preset, value=preset)
            for preset in presets if current.lower() in preset.lower()
        ][:25]

    @app_commands.command(name="lfg", description="募集を作成します")
    @app_commands.autocomplete(title=lfg_title_autocomplete)
    async def lfg(self, interaction: discord.Interaction, title: str, needed: int):
        embed = discord.Embed(title=f"募集: {title}", description=f"必要な人数: {needed}人", color=discord.Color.green())
        await interaction.response.send_message(embed=embed)
        msg = await interaction.original_response()
        await msg.add_reaction("✋")

async def setup(bot):
    await bot.add_cog(ValorantCog(bot))
