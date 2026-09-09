import discord
from discord.ext import commands
import wavelink
import os

class MusicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        await self.connect_nodes()

    async def connect_nodes(self):
        await self.bot.wait_until_ready()
        node = wavelink.Node(
            uri="http://lavalink:2333",
            password="youshallnotpass"
        )
        await wavelink.NodePool.connect(client=self.bot, nodes=[node])

    @discord.app_commands.command(name="play", description="Play a song")
    async def play(self, interaction: discord.Interaction, search: str):
        if not interaction.user.voice:
            await interaction.response.send_message("You must be in a voice channel.")
            return

        vc: wavelink.Player = interaction.guild.voice_client
        if not vc:
            vc = await interaction.user.voice.channel.connect(cls=wavelink.Player)

        tracks = await wavelink.YouTubeTrack.search(search)
        if not tracks:
            await interaction.response.send_message("No tracks found.")
            return

        track = tracks[0]
        await vc.play(track)
        await interaction.response.send_message(f"Playing: {track.title}")

async def setup(bot):
    await bot.add_cog(MusicCog(bot))
