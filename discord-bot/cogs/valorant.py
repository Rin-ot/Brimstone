import discord
from discord.ext import commands
from discord import app_commands
import random

class ValorantCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="teams", description="Split people in your VC into teams")
    async def teams(self, interaction: discord.Interaction, num_teams: int = 2):
        if not interaction.user.voice:
            await interaction.response.send_message("VCに入ってください。")
            return
            
        members = [m for m in interaction.user.voice.channel.members if not m.bot]
        if not members:
            await interaction.response.send_message("VCに誰もいません。")
            return
            
        random.shuffle(members)
        teams = {i: [] for i in range(num_teams)}
        
        for idx, m in enumerate(members):
            teams[idx % num_teams].append(m.display_name)
            
        embed = discord.Embed(title="チーム分け結果", color=discord.Color.blue())
        for i, t in teams.items():
            embed.add_field(name=f"チーム {i+1}", value="\n".join(t) if t else "なし", inline=False)
            
        await interaction.response.send_message(embed=embed)
        
    @app_commands.command(name="lfg", description="募集を作成します")
    async def lfg(self, interaction: discord.Interaction, title: str, needed: int):
        embed = discord.Embed(title=f"募集: {title}", description=f"必要な人数: {needed}人", color=discord.Color.green())
        await interaction.response.send_message(embed=embed)
        msg = await interaction.original_response()
        await msg.add_reaction("✋")

async def setup(bot):
    await bot.add_cog(ValorantCog(bot))
