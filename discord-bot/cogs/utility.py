import discord
from discord.ext import commands
from discord import app_commands
import random

class UtilityCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="roll", description="ダイスを振ります")
    async def roll(self, interaction: discord.Interaction, dice: str = "1d100"):
        try:
            rolls, limit = map(int, dice.split('d'))
            result = [random.randint(1, limit) for _ in range(rolls)]
            await interaction.response.send_message(f"🎲 結果: {sum(result)} (内訳: {result})")
        except:
            await interaction.response.send_message("形式エラーです。例: 1d100")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.bot: return
        if not before.channel and after.channel:
            sys_channel = member.guild.system_channel
            if sys_channel:
                await sys_channel.send(f"🔊 {member.display_name} が {after.channel.name} に入室しました！")
                
async def setup(bot):
    await bot.add_cog(UtilityCog(bot))
