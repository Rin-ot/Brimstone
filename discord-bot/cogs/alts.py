from discord.ext import commands
from discord.commands import slash_command
import discord, requests

class AltManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name = f"")