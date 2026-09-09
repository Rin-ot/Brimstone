import os

BASE_DIR = r"C:\Users\user\Documents\GitHub\Brimstone\discord-bot"

def create_file(path, content):
    full_path = os.path.join(BASE_DIR, path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

docker_compose = """
version: '3.8'

services:
  bot:
    build: .
    container_name: discord_bot
    restart: always
    volumes:
      - ./data:/app/data
    env_file:
      - .env
    depends_on:
      - lavalink

  lavalink:
    image: fredboat/lavalink:master
    container_name: lavalink
    restart: always
    ports:
      - "2333:2333"
    environment:
      - SERVER_PORT=2333
      - LAVALINK_SERVER_PASSWORD=youshallnotpass
"""

dockerfile = """
FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y ffmpeg gcc libffi-dev \\
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
"""

requirements = """
discord.py[voice]>=2.3.2
wavelink>=2.6.4
python-dotenv>=1.0.0
"""

main_py = """
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.members = True

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py') and not filename.startswith('__'):
                await self.load_extension(f'cogs.{filename[:-3]}')
        await self.tree.sync()

bot = MyBot()

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

if __name__ == "__main__":
    bot.run(os.getenv("DISCORD_TOKEN"))
"""

music_cog = """
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
"""

valorant_cog = """
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
            embed.add_field(name=f"チーム {i+1}", value="\\n".join(t) if t else "なし", inline=False)
            
        await interaction.response.send_message(embed=embed)
        
    @app_commands.command(name="lfg", description="募集を作成します")
    async def lfg(self, interaction: discord.Interaction, title: str, needed: int):
        embed = discord.Embed(title=f"募集: {title}", description=f"必要な人数: {needed}人", color=discord.Color.green())
        await interaction.response.send_message(embed=embed)
        msg = await interaction.original_response()
        await msg.add_reaction("✋")

async def setup(bot):
    await bot.add_cog(ValorantCog(bot))
"""

utility_cog = """
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
"""

env_example = """
DISCORD_TOKEN=your_token_here
"""

create_file("docker-compose.yml", docker_compose)
create_file("Dockerfile", dockerfile)
create_file("requirements.txt", requirements)
create_file("main.py", main_py)
create_file("cogs/__init__.py", "")
create_file("cogs/music.py", music_cog)
create_file("cogs/valorant.py", valorant_cog)
create_file("cogs/utility.py", utility_cog)
create_file(".env.example", env_example)

print("Scaffolding complete.")
