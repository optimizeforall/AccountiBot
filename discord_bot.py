from discord.ext import tasks, commands
import datetime
import os
import pickle
import random
import discord
from goal import Goal
from utils import *

class DiscordBot(commands.Bot):
    activeGoals = {}

    def __init__(self, command_prefix, intents):
        super().__init__(command_prefix, intents=intents)

    # Start the task when the bot is ready
    async def on_ready(self):
        log.info(f'Logged in as {self.user}')


def runBot():
    client = DiscordBot(command_prefix='!', intents=discord.Intents.all())
    
    @client.command(name='g', help='Create goal: !g [goal title] [goal duration in days] [hours to work] ?[rest days]')
    async def create_goal(ctx): 
        parsed_message = ctx.message.content.split()
        author_ID = ctx.message.author.id
        author_name = ctx.message.author.name


        if not valid_format(parsed_message):
            await ctx.send("Invalid format. Use !g [goal title] [goal duration] [hour goal] [days off]")
            return
        
        goal_title = parsed_message[1]
        goal_duration = int(parsed_message[2])
        hour_goal = int(parsed_message[3])
        days_off = 0 if len(parsed_message) == 4 else int(parsed_message[4])

        if days_off >= goal_duration:
            await ctx.send("Days off must be less than goal duration.")
            return

        goal = Goal(goal_duration, hour_goal, goal_title, days_off=days_off, author_ID=author_ID, author_name=author_name)
        save_goal(str(author_ID), goal)

        await ctx.send(goal.get_init_message())
    
    @client.command(name='ga', help='!ga [time in hours / minutes]')
    async def add_time(ctx):
        parsed_message = ctx.message.content.split()
        author_ID = ctx.message.author.id
        author_name = ctx.message.author.name

        if not valid_format(parsed_message):
            await ctx.send("Invalid format. Use !ga [hours or minutes (h or m)]")
            return

        # Convert string 1h30m to hours
        if 'm' in parsed_message[1] and not 'h' in parsed_message[1]:
            hours = float(parsed_message[1].split('m')[0])/60
        elif 'h' in parsed_message[1] and not 'm' in parsed_message[1]:
            hours = float(parsed_message[1].split('h')[0])
        elif 'h' in parsed_message[1] and 'm' in parsed_message[1]:
            hours = float(parsed_message[1].split('h')[0]) + float(parsed_message[1].split('h')[1].split('m')[0])/60
        else:
            await ctx.send("Invalid time format. Example: 1h30m, 90m, 1h, 1.5h")
            return
        
        try:
            goal = load_goal(str(author_ID))
            goal.add_hours(datetime.datetime.utcnow(), hours)
            save_goal(str(author_ID), goal)
            
        except Exception as e:  
            log.error("Error loading goal: " + str(e))
            await ctx.send("Error loading goal. Make sure you have the correct title.")
            return
        
        await ctx.send(str(hours) + " hours added to goal: " + goal.goal_title)
        await ctx.send(goal.get_status_message())

    # Display goal chart: !gg
    @client.command(name='gg', help='!gg')
    async def display_goal(ctx):
        author_ID = ctx.message.author.id

        try:
            user_goal = load_goal(str(author_ID))
            user_goal.generate_plot_image()
            await ctx.send(file=discord.File('data/' + str(author_ID) + '.png'))
        except Exception as e:  
            log.error("Error loading goal: " + str(e))
            await ctx.send("Error loading goal. Make sure you have the correct title. And have added at least one entry.")

    # Delete goal: !gd [goal title]
    @client.command(name='gd', help='!gd')
    async def delete_goal(ctx):
        parsed_message = ctx.message.content.split()
        author_ID = ctx.message.author.id

        if not valid_format(parsed_message):
            await ctx.send("Invalid. To delete goal, use !gd [goal title].")
            return
        try:
            os.remove(str(author_ID) + '.pickle')
            await ctx.send("Goal deleted.")
            return
        except Exception as e:
            log.error("Error deleting goal: " + str(e))
            await ctx.send("Error deleting goal. Make sure you have the correct title.")

    # List all goals: !gl
    @client.command(name='gl', help='!gl')
    async def list_goals(ctx):
        parsed_message = ctx.message.content.split()

        try:
            goals = []
            for filename in os.listdir('./data/goals/'):
                if filename.endswith('.pickle'):
                    with open('./data/goals/' + filename, 'rb') as f:
                        goal = pickle.load(f)
                        goals.append(goal)
                        f.close()
        except Exception as e:
            log.error("Error loading goal: " + str(e))
            await ctx.send("Error loading goal.")
            return
            
        if len(goals) == 0:
            await ctx.send("No goals found.")
            return
        else:
            message = ""
            for goal in goals:
                hoursRemaining = goal.hourGoal - goal.totalHoursWorked
                message += goal.authorName + ": \"" + goal.goalTitle + "\", " + str(round(hoursRemaining, 2)) + " hours remaining, with " + str(goal.daysRemaining()) + " days left.\n"
            await ctx.send(message)

    # Start goal timer: !gstart
    @client.command(name='gstart', help='!gstart')
    async def start_goal(ctx):
            try:
                with open('./data/activegoals.pickle', 'rb') as f:
                    activeGoals = pickle.load(f)
                    f.close()
            except Exception as e:
                log.error("Error loading active goals: " + str(e))
                await ctx.send("Error loading active goals.")

            activeGoals[str(ctx.message.author.id)] = datetime.datetime.utcnow()
            
            # save active goal to file using pickle
            with open('./data/activegoals.pickle', 'wb') as f:
                pickle.dump(activeGoals, f)
                f.close()

            await ctx.send("Goal started now. Use!gstop to stop goal.")

    # Stop goal timer: !gstop
    @client.command(name='gstop', help='!gstop')
    async def stop_goal(ctx):
            author_ID = ctx.message.author.id

            try:
                with open('./data/activegoals.pickle', 'rb') as f:
                    activeGoals = pickle.load(f)
                    f.close()
            except Exception as e:
                log.error("Error loading active goals: " + str(e))
                await ctx.send("Error loading active goals.")
                return
            
            if str(author_ID) in activeGoals:
                hoursWorked = (datetime.datetime.utcnow() - activeGoals[str(author_ID)]).total_seconds() / (60 * 60)

                try:
                    goal = load_goal(str(author_ID))
                    goal.add_hours(datetime.datetime.utcnow(), hoursWorked)
                    save_goal(str(author_ID), goal)
                except Exception as e:
                    log.error("Error loading goal: " + str(e))
                    await ctx.send("Error loading goal.")
                    return

                del activeGoals[str(author_ID)]
                message = "Goal stopped. " + str(round(hoursWorked, 2)) + " hours added to goal: " + goal.goal_title + "\n"
                message += goal.get_status_message()
                await ctx.send(message)
                return
            else:
                await ctx.send("No active goal.")

    # Display active goals status: !gs
    @client.command(name='gs', help='!gs')
    async def display_active_goals(ctx):
        parsed_message = ctx.message.content.split()
        
        try: 
            goal = load_goal(str(ctx.message.author.id))
        except Exception as e:
            log.error("Error loading goal: " + str(e))
            await ctx.send("Error loading goal. Make sure you have active goal.")
            return

        await ctx.send(goal.get_status_message())

    # Display help: !gh
    @client.command(name='gh', help='!gh')
    async def display_help(ctx):
        parsed_message = ctx.message.content.split()

        if parsed_message[0] == "!gh" or parsed_message[0] == "!help" or parsed_message[0] == "!h":
             await ctx.send(open('./data/help_message.txt', 'r').read())

    client.run(str(os.environ['AccountiBotToken']))

