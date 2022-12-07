from discord.ext import tasks, commands
import datetime
import os
import pickle
import random
import discord
from Goal import Goal
from utils import *

class DiscordBot(commands.Bot):
    activeGoals = {}

    def __init__(self, command_prefix, self_bot):
        super().__init__(command_prefix='!', intents=discord.Intents.all())


    # Make sure no active goals are beyond 24 hours
    @tasks.loop(seconds=5)
    async def checkGoals(self):
        # Iterate through all active goals and check if they are beyond 24 hours
        for authorID, time in self.activeGoals.items():
            if (datetime.datetime.utcnow() - time).total_seconds() > 0:
                # Goal is beyond 24 hours, remove it
                self.activeGoals.pop(authorID)
                log.info("Removing goal for " + authorID + " due to inactivity.")
                await self.get_user(int(authorID)).send("Your timer has been deleted due to inactivity. Make sure to use **!gstop** when using the timer.")
    
    async def on_ready(self):
        log.info(f'Logged in as {self.user}')

    async def on_message(self, message):
        log.info(f'Message received from {message.author}: {message.content}')
        # Don't respond to ourselves
        if message.author == self.user:
            return

        # Check if message is a command
        if message.content.startswith('!'):  
            is_private = True if isinstance(message.channel, discord.channel.DMChannel) else False
            await self.sendMessage(message, is_private)
        else:
            return
    
    async def sendMessage(self, message,is_private=False):
        response = await self.respond(message)
        if response != None:
            if is_private:
                await message.author.send(response)
            else:
                await message.channel.send(response)

    async def respond(self, message):
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

                goal = loadGoal(str(message.author.id))
                goal.addHours(datetime.datetime.utcnow(), hours)
                saveGoal(str(message.author.id), goal)
            except Exception as e:  
                log.error("Error loading goal: " + str(e))
                return "Error loading goal. Make sure you have the correct title."
            
            return str(hours) + " hours added to goal: " + goal.goalTitle

        # Display goal: !gg
        if pm[0] == "!gg":
            try:
                goal = loadGoal(str(message.author.id))
                goal.generatePlotImage()
                await message.channel.send(file=discord.File('Data/' + str(message.author.id) + '.png'))
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
                for filename in os.listdir('./Data/'):
                    if filename.endswith('.pickle'):
                        with open('./Data/' + filename, 'rb') as f:
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


        if pm[0] == "!gstart":
            self.activeGoals[str(message.author.id)] = datetime.datetime.utcnow()
            return "Goal started now. Use !gstop to stop goal."

        if pm[0] == "!gstop":
            if str(message.author.id) in self.activeGoals:
                hoursWorked = (datetime.datetime.utcnow() - self.activeGoals[str(message.author.id)]).total_seconds() / (60 * 60)

                try:
                    goal = loadGoal(str(message.author.id))
                    goal.addHours(datetime.datetime.utcnow(), hoursWorked)
                    saveGoal(str(message.author.id), goal)
                except Exception as e:
                    log.error("Error loading goal: " + str(e))
                    return "Error loading goal. Make sure you have the correct title."

                del self.activeGoals[str(message.author.id)]
                message = "Goal stopped. " + str(round(hoursWorked, 2)) + " hours added to goal: " + goal.goalTitle + "\n"
                message += goal.getStatusMessage()
                return message
            else:
                return "No active goal."

        
        # Get status of goal: !gs=
        if pm[0] == "!gs":
            try: 
                goal = loadGoal(str(message.author.id))
            except Exception as e:
                log.error("Error loading goal: " + str(e))
                return "Error loading goal. Make sure you have active goal."

            return goal.getStatusMessage()

        if pm[0] == "!gh" or pm[0] == "!help" or pm[0] == "!h":
            return open('help_message.txt', 'r').read()
        return None
