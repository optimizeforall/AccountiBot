import datetime
import pickle
import re
import discord
import discord.ext
import os
from goal import Goal
from logger import log
from utils import *


def run_bot():
    class aclient(discord.Client):
        def __init__(self):
            super().__init__(intents=discord.Intents.all())
            self.synced = False

        async def on_ready(self):
            log.info(f'{self.user} has connected to Discord!')
            if not self.synced:
                await tree.sync(guild=discord.Object(id=guild_id))
                # self.synced = True

    client = aclient()
    tree = discord.app_commands.CommandTree(client)
    guild_id = 1014983443756613672;

    @tree.command(name="ping", description="Ping the ping")
    async def slashing_commanding(int: discord.Interaction):
        await int.response.send_message("pongy")

    # Create goal
    @tree.command(name="newgoal", description="Create a new goal! Warning: will override old goal.", guild=discord.Object(id=guild_id))
    async def create_goal(int: discord.Interaction, goal_title: str, goal_days: int, goal_hours: int, days_off: int = 0):
        # Create variables from parsed message
        author_ID = int.user.id
        author_name = int.user.name

        # If days off is greater than goal duration, input invalid, return
        if days_off >= goal_days:
            await int.response.send_message("Days off must be less than goal duration.")
            return
        # check if hours is greater than 24*goal_days
        elif goal_hours > 24*goal_days:
            await int.response.send_message("Hours must be less than 24* days ;)")
            return

        # Crete goal object and save to file with author ID as file name
        goal = Goal(goal_days, goal_hours, goal_title,
                    days_off=days_off, author_ID=author_ID, author_name=author_name)
        save_goal(str(author_ID), goal)

        # Send user initializtion message
        log.info("New goal created: " + goal_title)
        await int.response.send_message(goal.get_init_message())

    # Add hours
    @tree.command(name='addtime', description='Add hours to goal: 1h30, 90m, 1.5h', guild=discord.Object(id=guild_id))
    async def add_time(int: discord.Interaction, hours: str, minutes: str, comment: str = None):

        author_ID = int.user.id
        time_in_hours = float(hours) + float(minutes)/60

        # Load goal from file and add hours
        try:
            goal = load_goal(str(author_ID))
            goal.add_hours(datetime.datetime.utcnow(), time_in_hours, comment)
            save_goal(str(author_ID), goal)
        except Exception as e:
            log.error("Error loading goal: " + str(e))
            await int.response.send_message("Error loading goal. Make sure you have the correct title. And have added at least one entry.")
            return

        message = str(round(time_in_hours, 2)) + " hours added to goal: " + \
            goal.goal_title + "\n"
        message += goal.get_status_message()

        log.info(f'{time_in_hours}hrs added to goal: {goal.goal_title}')
        await int.response.send_message(message)

    # Display log of hours worked on goal
    @tree.command(name='log', description='Display log of hours worked on goal', guild=discord.Object(id=guild_id))
    async def display_log(int: discord.Interaction):
        author_ID = int.user.id

        try:
            goal = load_goal(str(author_ID))
            await int.response.send_message(goal.get_log(), ephemeral=True)
        except Exception as e:
            log.error("Error loading goal: " + str(e))
            await int.response.send_message("Error loading goal. Make sure you have the correct title. And have added at least one entry.")

    # Display progress chart

    @tree.command(name='progresschart', description='Display progress chart', guild=discord.Object(id=guild_id))
    async def display_goal(int: discord.Interaction):
        author_ID = int.user.id

        try:
            goal = load_goal(str(author_ID))
            goal.generate_plot_image()
            log.info("Goal chart generated: " + goal.goal_title)
            await int.channel.send(file=discord.File('data/' + str(author_ID) + '.png'))
        except Exception as e:
            log.error("Error loading goal: " + str(e))
            await int.response.send_message("Error loading goal. Make sure you have the correct title. And have added at least one entry.")

    # Delete goal
    @tree.command(name='deletegoal', description='Delete goal', guild=discord.Object(id=guild_id))
    async def delete_goal(int: discord.Interaction):
        author_ID = int.user.id

        try:
            os.remove('data/goals/' + str(author_ID) + '.pickle')
            log.info("Goal deleted: " + str(author_ID) + '.pickle')
            await int.response.send_message('Goal deleted.')
            return
        except Exception as e:
            log.error("Error deleting goal: " + str(e))
            await int.response.send_message("Error deleting goal. Make sure you have the correct title.")

    # List all active goals on server
    @tree.command(name='listgoals', description='List all active goals', guild=discord.Object(id=guild_id))
    async def list_goals(int: discord.Interaction):
        goals = []
        try:
            for filename in os.listdir('/homez/julien/Programming/Projects/AccountiBot/data/goals'):
                if filename.endswith('.pickle'):
                    with open('data/goals/' + filename, 'rb') as f:
                        goal = pickle.load(f)
                        goals.append(goal)
        except Exception as e:
            log.error("Error listing goals: " + str(e))
            await int.response.send_message("Error listing goals.")
            return

        if len(goals) == 0:
            await int.response.send_message("No goals found.")
            return
        else:
            message = ""
            for goal in goals:
                hours_remaining = goal.hour_goal - goal.total_hours_worked
                message += (
                    f"{goal.author_name}: \"{goal.goal_title}\", "
                    f"{round(hours_remaining, 2)} hours remaining, with "
                    f"{goal.days_remaining()} days left.\n")
                await int.response.send_message(message)

    # Start goal timer
    @tree.command(name='start', description='Start goal timer', guild=discord.Object(id=guild_id))
    async def start_goal(int: discord.Interaction):
        
        # check if activegoal file exists
        if not os.path.exists('./data/activegoals.pickle'):
            activeGoals = {}
        else:
            try:
                with open('./data/activegoals.pickle', 'rb') as f:
                    activeGoals = pickle.load(f)
            except Exception as e:
                log.error("Error loading active goals: " + str(e))
                await int.response.send_message("Error loading active goals.")

        activeGoals[str(int.user.id)] = datetime.datetime.utcnow()

        # save active goal to file using pickle
        with open('./data/activegoals.pickle', 'wb') as f:
            pickle.dump(activeGoals, f)

        log.info(f'Starting goal for user: {int.user.name}')
        await int.response.send_message("Goal started now. Use /gstop to stop goal.")

    # Stop goal timer:
    @tree.command(name='stop', description='Stop goal timer', guild=discord.Object(id=guild_id))
    async def stop_goal(int: discord.Interaction, comment: str = None):
        author_ID = int.user.id

        try:
            with open('./data/activegoals.pickle', 'rb') as f:
                active_goals = pickle.load(f)
        except Exception as e:
            log.error("Error loading active goals: " + str(e))
            await int.response.send_message("Error loading active goals.")
            return

        if str(author_ID) in active_goals:
            hour_worked = (datetime.datetime.utcnow() - active_goals[str(author_ID)]).total_seconds() / (60 * 60)

            try:
                goal = load_goal(str(author_ID))
                goal.add_hours(datetime.datetime.utcnow(), hour_worked, comment)
                save_goal(str(author_ID), goal)
            except Exception as e:
                log.error("Error loading goal: " + str(e))
                await int.response.send_message("Error loading goal.")
                return

            del active_goals[str(author_ID)]
            message = f"Goal stopped. {round(hour_worked, 2)} hours added to goal: {goal.goal_title}\n"
            message += goal.get_status_message()
            await int.response.send_message(message)
            log.info(f'Goal stopped for user {int.user.name}, hours worked = {round(hour_worked, 2)} hours.')
            return
        else:   
            await int.response.send_message("No active goal.")

    # Display active goals status
    @tree.command(name='status', description='Display active goals status', guild=discord.Object(id=guild_id))
    async def display_active_goals(int: discord.Interaction):
        try:
            goal = load_goal(str(int.user.id))
        except Exception as e:
            log.error("Error loading goal: " + str(e))
            await int.response.send_message("Error loading goal. Make sure you have active goal.")
            return

        log.info(f'Printing status for user {int.user.name}')
        await int.response.send_message(goal.get_status_message())

    # Display help
    @tree.command(name='help', description='Display help', guild=discord.Object(id=guild_id))
    async def display_help(int: discord.Interaction):
        log.info(f'Printing help for user {int.user.name}')
        await int.response.send_message(open('./data/help_message.txt', 'r').read(), ephemeral=True)

    client.run(str(os.environ['AccountiBotToken']))
