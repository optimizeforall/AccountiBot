import datetime
import os
import pickle
import random
import discord
from Goal import Goal
from utils import *

def runBot():
    # Enable intent.messages
    intents = discord.Intents.all()
    client = discord.Client(intents=intents)

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

async def respond(message):
    # Parse the message
    pm = message.content.split(' ')

    # Create goal: !g [goal title] [goal duration in days] [hours to work] ?[rest days]
    if pm[0] == "!g":
        if not goodFormat(pm):
            return "Invalid format. Use !g [goal title] [goal duration] [hour goal] [days off]"
        
        goalTitle = pm[1]
        goalDuration = int(pm[2])
        hourGoal = int(pm[3])
        daysOff = 0 if len(pm) == 4 else int(pm[4])

        if daysOff >= goalDuration:
            return "Days off must be less than goal duration."

        goal = Goal(goalDuration, hourGoal, goalTitle, daysOff=daysOff, authorID=message.author.id, authorName=message.author.name)
        saveGoal(str(message.author.id), goal)

        return goal.getInitMessage()
    
    # Add hours to goal: !ga [time in hours / minutes]
    if pm[0] == "!ga":
        if not goodFormat(pm):
            return "Invalid format. Use !ga [hours or minutes (h or m)]"

        # Convert string 1h30m to hours
        if 'm' in pm[1] and not 'h' in pm[1]:
            hours = float(pm[1].split('m')[0])/60
        elif 'h' in pm[1] and not 'm' in pm[1]:
            hours = float(pm[1].split('h')[0])
        elif 'h' in pm[1] and 'm' in pm[1]:
            hours = float(pm[1].split('h')[0]) + float(pm[1].split('h')[1].split('m')[0])/60
        else:
            return "Invalid time format. Example: 1h30m, 90m, 1h, 1.5h"

        try:
            with open(str(message.author.id) + '.pickle', 'rb') as f:
                log.info('Loading: ' + str(message.author.id) + '.pickle')
                goal = pickle.load(f)
                goal.addHours(datetime.datetime.utcnow(), hours)
                goalTitle = goal.goalTitle
                saveGoal(str(message.author.id), goal)
                f.close()
        except Exception as e:  
            log.error("Error loading goal: " + str(e))
            return "Error loading goal. Make sure you have the correct title."
        
        return str(hours) + " hours added to goal: " + goalTitle

    # Display goal: !gg
    if pm[0] == "!gg":
        try:
            with open(str(message.author.id) + '.pickle', 'rb') as f:
                log.info('Loading: ' + str(message.author.id) + '.pickle')
                goal = pickle.load(f)
                goal.generatePlotImage()
                
                await message.channel.send(file=discord.File('Data/' + str(message.author.id) + '.png'))
                f.close()
        except Exception as e:  
            log.error("Error loading goal: " + str(e))
            return "Error loading goal. Make sure you have the correct title. And have added at least one entry."

    # Delete goal !gd [goal title]
    if pm[0] == "!gd":
        if not goodFormat(pm):
            return "Invalid. To delete goal, use !gd [goal title]."
        try:
            os.remove(str(message.author.id) + '.pickle')
            return "Goal deleted."
        except Exception as e:
            log.error("Error deleting goal: " + str(e))
            return "Error deleting goal. Make sure you have the correct title."

    # List all active goals with user name and hours left: !gl
    if pm[0] == "!gl":
        try:
            goals = []
            for filename in os.listdir('.'):
                if filename.endswith('.pickle'):
                    with open(filename, 'rb') as f:
                        goal = pickle.load(f)
                        goals.append(goal)
                        f.close()
        except Exception as e:
            log.error("Error loading goal: " + str(e))
            return "Error loading goal."
            
        if len(goals) == 0:
            return "No goals found."
        else:
            message = ""
            for goal in goals:
                hoursRemaining = goal.hourGoal - goal.totalHoursWorked
                message += goal.authorName + ": \"" + goal.goalTitle + "\", " + str(round(hoursRemaining, 2)) + " hours remaining, with " + str(goal.daysRemaining()) + " days left.\n"
            return message

    if pm[0] == "!gh" or pm[0] == "!help" or pm[0] == "!h":
        return open('help_message.txt', 'r').read()
    return None
