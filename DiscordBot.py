import datetime
import os
import pickle
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

        # Check if message is a command
        if message.content.startswith('!'):
            
            is_private = True if isinstance(message.channel, discord.channel.DMChannel) else False
            await sendMessage(message, is_private)
        else:
            return
        
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

    # Create goal
    if pm[0] == "!g":
        if goalFormat(pm):
            goalTitle = pm[1]
            goalDuration = int(pm[2])
            hourGoal = int(pm[3])
            daysOff = 0 if len(pm) == 4 else int(pm[4])

            goal = Goal(goalDuration, hourGoal, goalTitle, daysOff)
            saveGoal(goalTitle, goal)

            return goal.getInitMessage()
        else:
            return "Invalid format. Use !g [goal title] [goal duration] [hour goal] [days off]"
    
    # Add hours to goal
    if pm[0] == "!ga":
        if len(pm) != 3:
            return "Invalid format. Use !ga [goal title] [hours] [date]"

        # Convert string 1h30m to hours
        if 'm' in pm[2] and not 'h' in pm[2]:
            hours = float(pm[2].split('m')[0])/60
        elif 'h' in pm[2] and not 'm' in pm[2]:
            hours = float(pm[2].split('h')[0])
        elif 'h' in pm[2] and 'm' in pm[2]:
            hours = float(pm[2].split('h')[0]) + float(pm[2].split('h')[1].split('m')[0])/60
        else:
            return "Invalid time format. Example: 1h30m, 90m, 1h, 1.5h"

        try:
            with open(pm[1] + '.pickle', 'rb') as f:
                log.info('Loading: ' + pm[1] + '.pickle')
                goal = pickle.load(f)
                goal.addHours(datetime.datetime.utcnow(), hours)
                saveGoal(pm[1], goal)
                f.close()
        except Exception as e:  
            log.error("Error loading goal: " + str(e))
            return "Error loading goal. Make sure you have the correct title."
        
        return str(hours) + " hours added to " + pm[1] + "."

    # Display goal
    if pm[0] == "!gg":
        if len(pm) != 2:
            return "Invalid format. Use !gg [goal title]"

        try:
            with open(pm[1] + '.pickle', 'rb') as f:
                log.info('Loading: ' + pm[1] + '.pickle')
                goal = pickle.load(f)
                goal.generatePlotImage()
                
                await message.channel.send(file=discord.File('Media/' + pm[1] + '.png'))
                f.close()
        except Exception as e:  
            log.error("Error loading goal: " + str(e))
            return "Error loading goal. Make sure you have the correct title."
    

    if pm[0] == "!gh" or pm[0] == "!help" or pm[0] == "!h":
        return open('help_message.txt', 'r').read()
    
    return None

def saveGoal(goalTitle, goal):
    try:
        with open(goalTitle + '.pickle', 'wb') as f:
            pickle.dump(goal, f)
            log.info('Saved goal: ' + goalTitle + '.pickle')
            f.close()
    except Exception as e:
        log.error("Error saving goal: " + str(e))

def goalFormat(pm):
    print(pm)

    if len(pm) != 5 and len(pm) != 4:
        return False
    
    if not pm[1].isdigit() or not pm[2].isdigit():
        return False
    
    return True