from Goal import Goal
import datetime
import random 


def testGoal():

    goalDuration = 10
    hourGoal = 50
    goalTitle = 'Learning Rust'
    daysOff = 0

    goal = Goal(goalDuration, hourGoal, goalTitle, daysOff)

    # Add random entries to goal
    for i in range(20):
        goal.addHours(datetime.datetime.utcnow() + datetime.timedelta(days=random.randint(0, goalDuration-1), hours=random.randint(0, 24)), random.uniform(.1, 5))

    goal.showPlot()
    goal.savePlot('./Media/plot.png')
    print("Done")


if __name__ == '__main__':
    testGoal()