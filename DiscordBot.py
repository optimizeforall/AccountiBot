import os
import random
from logger import log
import discord
from Goal import Goal 


def runBot():
    # Enable intent.messages
    intents = discord.Intents.all()
    client = discord.Client(intents=intents)

    discord.Intents.messages = True

    @client.event
    async def on_ready():
        log.info(f'Logged in as {client.user}')

    @client.event
    async def on_message(message):
        log.info(f'Message received from {message.author}: {message.content}')
        # Don't respond to ourselves
        if message.author == client.user:
            return
        
        await sendMessage(message)
    # import token from system environment
    client.run(os.environ['AccountiBotToken'])


async def sendMessage(message,is_private=False):
    response = await respond(message)
    if response != None:
        if is_private:
            await message.author.send(response)
        else:
            await message.channel.send(response)

# send image
async def sendImage(message):
    await message.channel.send(file=discord.File('Media/plot.png'))

async def respond(message):
    # Parse the message
    pm = message.content.split(' ')

    if pm[0] == "!g":
        if goalFormat(pm):
            goal = Goal(int(pm[1]), float(pm[2]), pm[3], int(pm[4]))
            return goal.getInitMessage()
        else:
            return "Invalid format. Use !g [goal duration] [hour goal] [goal title] [days off]"
        
    if pm[0] == "!gg":
        await sendImage(message)


    if pm[0] == "!gr":
        return f'Ha, you rolled my secret dice: ({str(random.randint(1, 6))}, {str(random.randint(1, 6))})'
    
    if pm[0] == "!gh" or pm[0] == "!help" or pm[0] == "!h":
        return open('help_message.txt', 'r').read()
    
    return None

def goalFormat(pm):
    print(pm)
    if len(pm) != 5:
        return False
    
    if not pm[1].isdigit() or not pm[2].isdigit() or not pm[4].isdigit():
        return False
    
    return True