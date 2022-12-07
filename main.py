import os
import pickle
from Goal import Goal
import datetime
import random
from logger import log
from DiscordBot import DiscordBot as bot

def testGoal():

    goalDuration = 30
    hourGoal = 50
    goalTitle = 'Learn_Rust'
    daysOff = 0

    goal = Goal(goalDuration, hourGoal, goalTitle, daysOff)

    # Add random entries to goal
    for i in range(20):
        goal.addHours(datetime.datetime.utcnow() + datetime.timedelta(days=random.randint(0, goalDuration-1), hours=random.randint(0, 24)), random.uniform(.1, 5))
    
    try:
        with open(goalTitle + '.pickle', 'wb') as f:
            pickle.dump(goal, f)
            f.close()
    except Exception as e:
        log.error("Error saving goal: " + str(e))

    # goal.generatePlotImage()
    goal.showPlot()

if __name__ == '__main__':
    # testGoal()
    client = bot(command_prefix='!', self_bot=False)
    client.run(str(os.environ['AccountiBotToken']))
