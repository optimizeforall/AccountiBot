import os
import pickle
from goal import Goal
import datetime
import random
import discord
from logger import log
import discord_bot

def testGoal():

    goalDuration = 30
    hourGoal = 50
    goalTitle = 'Learn_Rust'
    daysOff = 0

    goal = Goal(goalDuration, hourGoal, goalTitle, daysOff)

    # Add random entries to goal
    for i in range(20):
        goal.add_hours(datetime.datetime.utcnow() + datetime.timedelta(days=random.randint(0, goalDuration-1), hours=random.randint(0, 24)), random.uniform(.1, 5))
    
    try:
        with open(goalTitle + '.pickle', 'wb') as f:
            pickle.dump(goal, f)
            f.close()
    except Exception as e:
        log.error("Error saving goal: " + str(e))

    # goal.generatePlotImage()
    goal.show_plot()

def main():


    discord_bot.runBot()

    # DiscordBot(command_prefix='!', intents=discord.Intents.all())
    

if __name__ == '__main__':
    main()
    # testGoal()