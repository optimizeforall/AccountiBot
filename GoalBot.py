import datetime
import random 
import matplotlib.pyplot as plt
import matplotlib as mpl
import logging
from Goal import Goal

from numpy import sort 
import CustomFormatter 

# Initiate logger with custom formatter
log = logging.getLogger('acountitbot')
log.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(CustomFormatter.CustomFormatter())
log.addHandler(ch)

def testGoal():
    g = Goal(30, 90, "Learning Dart")

    # Add random entries to goal
    for i in range(50):
        g.addHours(datetime.datetime.utcnow() + datetime.timedelta(days=random.randint(0, 30), hours=random.randint(0, 24)), random.uniform(.1, 5))

    g.showPlot()
    g.savePlot('./Media/plot.png')

if __name__ == "__main__":
    testGoal()