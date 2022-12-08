import os
from discord.ext import commands 
import discord

class DiscordBot(commands.Bot):  # make sure the DiscordBot class inherits from commands.Bot
    def __init__(self, command_prefix):
        super().__init__(command_prefix, intents=discord.Intents.all())  # initialize the base Bot class

    async def on_ready(self):
        print(self.commands)

client = DiscordBot(command_prefix='$')

@client.command()  # define the hello command using the @command decorator
async def hello(ctx):  # the command function must take a "ctx" argument
    await ctx.send("Hello, world!")  # use the "ctx" argument to send a message

client.run(str(os.environ['AccountiBotToken']))