from discord.ext import tasks, commands
import datetime
import os
import pickle
import random
import discord
from goal import Goal
from utils import *

# Create bot object
class DiscordBot(commands.Bot):
    activeGoals = {}

    # Initialize bot with command prefix and intents
    def __init__(self, command_prefix, intents):
        super().__init__(command_prefix, intents=intents)

    # When bot is ready, log in console
    async def on_ready(self):
        log.info(f'Logged in as {self.user}')

# Contains all bot commands
def run_bot():
    # Create bot object with all intents
    client = DiscordBot(command_prefix='!', intents=discord.Intents.all())

    # Create goal
    @client.command(name='g', help='!ga [goal title] [goal duration in days] [hours to work] ?[rest days]')
    async def create_goal(ctx):
        command_args = ctx.message.content.split()
        author_ID = ctx.message.author.id
        author_name = ctx.message.author.name

        # If bad format, return
        if not valid_format(command_args):
            await ctx.send("Invalid format. Use !g [goal title] [goal duration] [hour goal] [days off]")
            return

        # Create variables from parsed message
        goal_title = command_args[1]
        goal_duration = int(command_args[2])
        hour_goal = int(command_args[3])
        days_off = 0 if len(command_args) == 4 else int(command_args[4])

        # If days off is greater than goal duration, input invalid, return
        if days_off >= goal_duration:
            await ctx.send("Days off must be less than goal duration.")
            return

        # Crete goal object and save to file with author ID as file name
        goal = Goal(goal_duration, hour_goal, goal_title,
                    days_off=days_off, author_ID=author_ID, author_name=author_name)
        save_goal(str(author_ID), goal)

        # Send user initializtion message
        await ctx.send(goal.get_init_message())

    # Add hours 
    @client.command(name='ga', help='!ga [time in hours / minutes]')
    async def add_time(ctx):
        command_args = ctx.message.content.split()
        author_ID = ctx.message.author.id
        author_name = ctx.message.author.name

        if not valid_format(command_args):
            await ctx.send("Invalid format. Use !ga [hours or minutes (h or m)]")
            return

        # Convert string 1h30m to hours
        if 'm' in command_args[1] and not 'h' in command_args[1]:
            hours = float(command_args[1].split('m')[0])/60
        elif 'h' in command_args[1] and not 'm' in command_args[1]:
            hours = float(command_args[1].split('h')[0])
        elif 'h' in command_args[1] and 'm' in command_args[1]:
            hours = float(command_args[1].split(
                'h')[0]) + float(command_args[1].split('h')[1].split('m')[0])/60
        else:
            await ctx.send("Invalid time format. Example: 1h30m, 90m, 1h, 1.5h")
            return

        # Load goal from file and add hours
        try:
            goal = load_goal(str(author_ID))
            goal.add_hours(datetime.datetime.utcnow(), hours)
            save_goal(str(author_ID), goal)
        except Exception as e:
            log.error("Error loading goal: " + str(e))
            await ctx.send("Error loading goal. Make sure you have the correct title. And have added at least one entry.")
            return

        await ctx.send(str(hours) + " hours added to goal: " + goal.goal_title)
        await ctx.send(goal.get_status_message())

    # Display progress chart
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

    # Delete goal
    @client.command(name='gd', help='!gd')
    async def delete_goal(ctx):
        command_args = ctx.message.content.split()
        author_ID = ctx.message.author.id

        if not valid_format(command_args):
            await ctx.send("Invalid. To delete goal, use !gd [goal title].")
            return
        try:
            os.remove(str(author_ID) + '.pickle')
            await ctx.send("Goal deleted.")
            return
        except Exception as e:
            log.error("Error deleting goal: " + str(e))
            await ctx.send("Error deleting goal. Make sure you have the correct title.")

    # List all active goals on server
    @client.command(name='gl', help='!gl')
    async def list_goals(ctx):
        command_args = ctx.message.content.split()

        goals = []
        try: 
            for filename in os.listdir('/home/julien/Programming/Projects/AccountiBot/data/goals'):
                print(filename)
                if filename.endswith('.pickle'):
                    with open('data/goals/' + filename, 'rb') as f:
                        goal = pickle.load(f)
                        goals.append(goal)
        except Exception as e:
            log.error("Error listing goals: " + str(e))
            await int.response.send_message("Error listing goals.")
            return
            
        if len(goals) == 0:
            await ctx.send("No goals found.")
            return
        else:
            message = ""
            for goal in goals:
                hoursRemaining = goal.hourGoal - goal.totalHoursWorked
                message += (
                    f"{goal.author_name}: \"{goal.goal_title}\", "
                    f"{round(hoursRemaining, 2)} hours remaining, with "
                    f"{goal.days_remaining()} days left.\n")
                await ctx.send(message)

    # Start goal timer
    @client.command(name='gstart', help='!gstart')
    async def start_goal(ctx):
        try:
            with open('./data/activegoals.pickle', 'rb') as f:
                activeGoals = pickle.load(f)
        except Exception as e:
            log.error("Error loading active goals: " + str(e))
            await ctx.send("Error loading active goals.")

        activeGoals[str(ctx.message.author.id)] = datetime.datetime.utcnow()

        # save active goal to file using pickle
        with open('./data/activegoals.pickle', 'wb') as f:
            pickle.dump(activeGoals, f)

        await ctx.send("Goal started now. Use !gstop to stop goal.")

    # Stop goal timer: !gstop
    @client.command(name='gstop', help='!gstop')
    async def stop_goal(ctx):
        author_ID = ctx.message.author.id

        try:
            with open('./data/activegoals.pickle', 'rb') as f:
                active_goals = pickle.load(f)
        except Exception as e:
            log.error("Error loading active goals: " + str(e))
            await ctx.send("Error loading active goals.")
            return

        if str(author_ID) in active_goals:
            hoursWorked = (datetime.datetime.utcnow(
            ) - active_goals[str(author_ID)]).total_seconds() / (60 * 60)

            try:
                goal = load_goal(str(author_ID))
                goal.add_hours(datetime.datetime.utcnow(), hoursWorked)
                save_goal(str(author_ID), goal)
            except Exception as e:
                log.error("Error loading goal: " + str(e))
                await ctx.send("Error loading goal.")
                return

            del active_goals[str(author_ID)]
            message = f"Goal stopped. {round(hoursWorked, 2)} hours added to goal: {goal.goal_title}\n"
            message += goal.get_status_message()
            await ctx.send(message)
            return
        else:
            await ctx.send("No active goal.")

    # Display active goals status: !gs
    @client.command(name='gs', help='!gs')
    async def display_active_goals(ctx):
        command_args = ctx.message.content.split()

        try:
            goal = load_goal(str(ctx.message.author.id))
        except Exception as e:
            log.error("Error loading goal: " + str(e))
            await ctx.send("Error loading goal. Make sure you have active goal.")
            return

        await ctx.send(goal.get_status_message())

    # Display help: !gh
    @client.command(name='gh', help='!gh, !help')
    async def display_help(ctx):
        command_args = ctx.message.content.split()

        if command_args[0] == "!gh" or command_args[0] == "!help" or command_args[0] == "!h":
            await ctx.send(open('./data/help_message.txt', 'r').read())

    client.run(str(os.environ['AccountiBotToken']))
