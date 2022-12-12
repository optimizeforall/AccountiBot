import datetime
import pickle
import re
import discord
import discord.ext
import os
from goal import Goal
from logger import log
from utils import *

<<<<<<< HEAD

def run_bot():
    class aclient(discord.Client):
        def __init__(self):
            super().__init__(intents=discord.Intents.all())
            self.synced = False

        async def on_ready(self):
            print(f'{self.user} has connected to Discord!')
            if not self.synced:
                await tree.sync(guild=discord.Object(id=1014983443756613672))
                # self.synced = True

    client = aclient()
    tree = discord.app_commands.CommandTree(client)

    @tree.command(name="ping", description="Ping the ping")
    async def slashing_commanding(int: discord.Interaction):
        await int.response.send_message("pongy")
=======
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
>>>>>>> deffa15 (Clean up)

    # Create goal
    @tree.command(name="newgoal", description="Create a new goal! Warning: will override old goal.", guild=discord.Object(id=1014983443756613672))
    async def create_goal(int: discord.Interaction, goal_title: str, goal_days: int, goal_hours: int, days_off: int = 0):
        # Create variables from parsed message
<<<<<<< HEAD
        author_ID = int.user.id
        author_name = int.user.name
=======
        goal_title = command_args[1]
        goal_duration = int(command_args[2])
        hour_goal = int(command_args[3])
        days_off = 0 if len(command_args) == 4 else int(command_args[4])
>>>>>>> deffa15 (Clean up)

        # If days off is greater than goal duration, input invalid, return
        if days_off >= goal_days:
            await int.response.send_message("Days off must be less than goal duration.")
            return
        # check if hours is greater than 24*goal_days
        elif goal_hours > 24*goal_days:
            await int.response.send_message("Hours must be less than 24* days ;)")
            return

        # Crete goal object and save to file with author ID as file name
<<<<<<< HEAD
        goal = Goal(goal_days, goal_hours, goal_title,
=======
        goal = Goal(goal_duration, hour_goal, goal_title,
>>>>>>> deffa15 (Clean up)
                    days_off=days_off, author_ID=author_ID, author_name=author_name)
        save_goal(str(author_ID), goal)

        # Send user initializtion message
        await int.response.send_message(goal.get_init_message())

<<<<<<< HEAD
    # Add hours
    @tree.command(name='addtime', description='Add hours to goal: 1h30, 90m, 1.5h', guild=discord.Object(id=1014983443756613672))
    async def add_time(int: discord.Interaction, hours: str, minutes: str):

        author_ID = int.user.id        
        time_in_hours = float(hours) + float(minutes)/60

=======
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

>>>>>>> deffa15 (Clean up)
        # Load goal from file and add hours
        try:
            goal = load_goal(str(author_ID))
            goal.add_hours(datetime.datetime.utcnow(), time_in_hours)
            save_goal(str(author_ID), goal)
        except Exception as e:
            log.error("Error loading goal: " + str(e))
            await int.response.send_message("Error loading goal. Make sure you have the correct title. And have added at least one entry.")
            return
<<<<<<< HEAD

        message = str(round(time_in_hours, 2)) + " hours added to goal: " + \
            goal.goal_title + "\n"
        message += goal.get_status_message()
        await int.response.send_message(message)

    # Display progress chart
    @tree.command(name='progresschart', description='Display progress chart', guild=discord.Object(id=1014983443756613672))
    async def display_goal(int: discord.Interaction):
        author_ID = int.user.id
=======

        await ctx.send(str(hours) + " hours added to goal: " + goal.goal_title)
        await ctx.send(goal.get_status_message())

    # Display progress chart
    @client.command(name='gg', help='!gg')
    async def display_goal(ctx):
        author_ID = ctx.message.author.id
>>>>>>> deffa15 (Clean up)

        try:
            user_goal = load_goal(str(author_ID))
            user_goal.generate_plot_image()
<<<<<<< HEAD
            await int.response.send_message(file=discord.File('data/' + str(author_ID) + '.png'))
=======
            await ctx.send(file=discord.File('data/' + str(author_ID) + '.png'))
>>>>>>> deffa15 (Clean up)
        except Exception as e:
            log.error("Error loading goal: " + str(e))
            await int.response.send_message("Error loading goal. Make sure you have the correct title. And have added at least one entry.")

    # Delete goal
<<<<<<< HEAD
    @tree.command(name='deletegoal', description='Delete goal', guild=discord.Object(id=1014983443756613672))
    async def delete_goal(int: discord.Interaction):
        author_ID = int.user.id

=======
    @client.command(name='gd', help='!gd')
    async def delete_goal(ctx):
        command_args = ctx.message.content.split()
        author_ID = ctx.message.author.id

        if not valid_format(command_args):
            await ctx.send("Invalid. To delete goal, use !gd [goal title].")
            return
>>>>>>> deffa15 (Clean up)
        try:
            os.remove('data/goals/' + str(author_ID) + '.pickle')
            await int.response.send_message("Goal deleted.")
            return
        except Exception as e:
            log.error("Error deleting goal: " + str(e))
            await int.response.send_message("Error deleting goal. Make sure you have the correct title.")

    # List all active goals on server
<<<<<<< HEAD
    @tree.command(name='listgoals', description='List all active goals', guild=discord.Object(id=1014983443756613672))
    async def list_goals(int: discord.Interaction):
=======
    @client.command(name='gl', help='!gl')
    async def list_goals(ctx):
        command_args = ctx.message.content.split()

>>>>>>> deffa15 (Clean up)
        goals = []
        for filename in os.listdir('./data/goals/'):
            if filename.endswith('.pickle'):
                with open('./data/goals/' + filename, 'rb') as f:
                    goal = pickle.load(f)
                    goals.append(goal)

        if len(goals) == 0:
            await int.response.send_message("No goals found.")
            return
        else:
            message = ""
            for goal in goals:
<<<<<<< HEAD
                hours_remaining = goal.hour_goal - goal.total_hours_worked
                message += (
                    f"{goal.author_name}: \"{goal.goal_title}\", "
                    f"{round(hours_remaining, 2)} hours remaining, with "
                    f"{goal.days_remaining()} days left.\n")
                await int.response.send_message(message)

    # Start goal timer
    @tree.command(name='start', description='Start goal timer', guild=discord.Object(id=1014983443756613672))
    async def start_goal(int: discord.Interaction):
        try:
            with open('./data/activegoals.pickle', 'rb') as f:
                activeGoals = pickle.load(f)
=======
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
>>>>>>> deffa15 (Clean up)
        except Exception as e:
            log.error("Error loading active goals: " + str(e))
            await int.response.send_message("Error loading active goals.")

        activeGoals[str(int.user.id)] = datetime.datetime.utcnow()

        # save active goal to file using pickle
        with open('./data/activegoals.pickle', 'wb') as f:
            pickle.dump(activeGoals, f)

        await int.response.send_message("Goal started now. Use /gstop to stop goal.")

    # Stop goal timer:
    @tree.command(name='stop', description='Stop goal timer', guild=discord.Object(id=1014983443756613672))
    async def stop_goal(int: discord.Interaction):
        author_ID = int.user.id

        try:
            with open('./data/activegoals.pickle', 'rb') as f:
                active_goals = pickle.load(f)
        except Exception as e:
            log.error("Error loading active goals: " + str(e))
            await int.response.send_message("Error loading active goals.")
            return

        if str(author_ID) in active_goals:
            hoursWorked = (datetime.datetime.utcnow(
            ) - active_goals[str(author_ID)]).total_seconds() / (60 * 60)

<<<<<<< HEAD
            try:
                goal = load_goal(str(author_ID))
                goal.add_hours(datetime.datetime.utcnow(), hoursWorked)
                save_goal(str(author_ID), goal)
            except Exception as e:
                log.error("Error loading goal: " + str(e))
                await int.response.send_message("Error loading goal.")
                return

            del active_goals[str(author_ID)]
            message = f"Goal stopped. {round(hoursWorked, 2)} hours added to goal: {goal.goal_title}\n"
            message += goal.get_status_message()
            await int.response.send_message(message)
            return
        else:
            await int.response.send_message("No active goal.")

    # Display active goals status
    @tree.command(name='status', description='Display active goals status', guild=discord.Object(id=1014983443756613672))
    async def display_active_goals(int: discord.Interaction):
        try:
            goal = load_goal(str(int.user.id))
        except Exception as e:
            log.error("Error loading goal: " + str(e))
            await int.response.send_message("Error loading goal. Make sure you have active goal.")
            return

        await int.response.send_message(goal.get_status_message())

    # Display help
    @tree.command(name='help', description='Display help', guild=discord.Object(id=1014983443756613672))
    async def display_help(int: discord.Interaction):
        await int.response.send_message(open('./data/help_message.txt', 'r').read(), ephemeral=True)
=======
    # Display help: !gh
    @client.command(name='gh', help='!gh, !help')
    async def display_help(ctx):
        command_args = ctx.message.content.split()

        if command_args[0] == "!gh" or command_args[0] == "!help" or command_args[0] == "!h":
            await ctx.send(open('./data/help_message.txt', 'r').read())
>>>>>>> deffa15 (Clean up)

    client.run(str(os.environ['AccountiBotToken']))
