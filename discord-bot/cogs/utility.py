import discord
from discord.ext import commands
from discord import app_commands
import random, datetime

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
                message = [message async for message in sys_channel.history(limit=1)][0]
                if message and message.author == self.bot.user and message.embeds[0].title == "📞 参加通知":
                    if len(list(after.channel.members)) == 1:
                        e = discord.Embed(title = f"📞 参加通知", description = f"🔊 {member.mention} が {after.channel.mention} に入室しました！", color = 0x3377bb)
                        await sys_channel.send(embed=e)

                    else:
                        e = message.embeds[0]
                        e.description += f"\n🔊 {member.mention} が {after.channel.mention} に入室しました！ ｜ <t:{round(datetime.datetime.now().timestamp())}:R>"
                        await message.edit(embed=e)

                else:
                    e = discord.Embed(title = f"📞 参加通知", description = f"🔊 {member.mention} が {after.channel.mention} に入室しました！", color = 0x3377bb)
                    await sys_channel.send(embed=e)

async def setup(bot):
    await bot.add_cog(UtilityCog(bot))
