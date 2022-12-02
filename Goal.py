import datetime
import io
import random 
import matplotlib.pyplot as plt
import matplotlib as mpl
import logging 
import CustomFormatter 

# Initiate logger with custom formatter
log = logging.getLogger('acountitbot')
log.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(CustomFormatter.CustomFormatter())
log.addHandler(ch)

class Goal:
    def __init__(self, goalDuration: float, hourGoal: float, goalTitle: str, daysOff=0):
        log.info(f'Creating new goal: {goalTitle}')

        self.goalDuration = goalDuration
        self.hourGoal = hourGoal
        self.goalTitle = goalTitle
        self.startDate = datetime.datetime.utcnow()
        self.endDate = self.startDate + datetime.timedelta(days=goalDuration)
        self.daysOff = daysOff
        self.hoursPerDay = hourGoal / (goalDuration - self.daysOff)
        self.timeWorked = [] # list of touples (time of entry, hoursWorked)
        self.timeWorkedPerDay = [0] * goalDuration # index is day in goal, value is hours worked,

    def addHours(self, time: datetime, hours: float):
        dayInGoal = (time - self.startDate).days
        startDateStr = self.startDate.strftime('%m/%d/%Y, %H:%M:%S')
        endDateStr = self.endDate.strftime('%m/%d/%Y, %H:%M:%S')
        entryDateStr = time.strftime('%m/%d/%Y, %H:%M:%S')

        # If dayInGoal outside goal range, print error and return
        if dayInGoal >= self.goalDuration or dayInGoal < 0:
            log.error(f'{entryDateStr} is outside of goal range: ({startDateStr}) - ({endDateStr})')
            return
        else:
            log.info(f'Adding {hours} hours for day {dayInGoal} / {self.goalDuration}.')
            self.timeWorked.append((time, hours)) # This isn't necessary, but I want to keep track of all entries for now
            self.timeWorkedPerDay[dayInGoal] += hours

    def getInitMessage(self):
        """
        Your goal, beast_mode, will last 10 days, and require 30 hours of recorded work.
        It begins now, and ends Thur October 3rd, 2022 at 11:59 PM.
        This requires an average of 3hrs of work / day with 0 days off.
        If you fall behind in tracking, I'll get on you case. 
        If you need help regarding using this bot, type !gh
        """

        message = f'Your goal, {self.goalTitle}, will last {self.goalDuration} days, and require {self.hourGoal} hours of recorded work.\n'
        message += f'It begins now, and ends {self.endDate.strftime("%a %B %dth, %Y at %I:%M %p")}.\n'
        message += f'This requires an average of {self.hoursPerDay}hrs of work / day with {self.daysOff} days off.\n'
        message += f'If you fall behind in tracking, I\'ll get on you case. Good luck!\n'
        message += f'If you need help regarding using this bot, type !gh'

        return message

    # Return graph of progress, x-axis is goalDuration in days, y-axis hours worked
    def displayProgressGraph(self):
        mpl.rcParams['lines.linewidth'] = .5
        mpl.rcParams['lines.linestyle'] = '-'
        mpl.rcParams['axes.facecolor'] = 'black' # background color
        mpl.rcParams['toolbar'] = 'None' # Remove toolbar
        mpl.rcParams['figure.facecolor'] = 'black' # Remove white space around graph        
        # Add grid lines
        mpl.rcParams['axes.grid'] = True
        mpl.rcParams['grid.color'] = 'grey'
        mpl.rcParams['grid.linewidth'] = 0.08
        # Display x and y axis and make color of text grey
        mpl.rcParams['axes.edgecolor'] = 'grey'
        mpl.rcParams['axes.labelcolor'] = 'grey'
        mpl.rcParams['xtick.color'] = 'grey'
        mpl.rcParams['ytick.color'] = 'grey'
        # Show label 'hours' on y-axis, make label color grey
        mpl.rcParams['ytick.labelsize'] = 8
        mpl.rcParams['ytick.labelcolor'] = 'grey'
        mpl.rcParams['ytick.labelleft'] = True
        # Show label 'days' on x-axis, make label color grey
        mpl.rcParams['xtick.labelsize'] = 8
        mpl.rcParams['xtick.labelcolor'] = 'grey'
        mpl.rcParams['xtick.labelbottom'] = True

        # Remove ticks on x-axis
        mpl.rcParams['xtick.bottom'] = False
        mpl.rcParams['ytick.left'] = False


        # Set x and y limits, x (days) starts at 1, y (hours)starts at 0
        ax = plt.gca()
        ax.set_xlim([1, self.goalDuration])
        ax.set_ylim([0, round(self.hourGoal * 1.3, -1)]) # self.hourGoal * 1.3 to give room to see goal line


        # Generate x and y values for graph
        x = [i for i in range(1, self.goalDuration + 1)]
        y = [sum(self.timeWorkedPerDay[:i+1]) for i in range(1, self.goalDuration + 1)]
        log.debug(f'\nx: {x}\ny: {y}')

        # Create graph
        log.info(f'Create graph for {self.goalTitle}')
        plt.scatter(x, y, label='Hours Worked')
        plt.xlabel('Days')
        plt.ylabel('Hours')

        # Make scatter plot of x and y values




        # Add title 
        plt.title(f'\"{self.goalTitle}\"', color='grey', pad=10)

        # draw line at goal
        plt.axhline(y=self.hourGoal, color='r', linestyle='-', label=f'Goal {self.hourGoal}hrs')

        # Create legend with label goalTitle
        plt.legend(bbox_to_anchor=(.01, .98), loc='upper left', prop={'size': 8}, facecolor='black', edgecolor='grey')
        # Add padding to legend 


        #make legend text color grey
        plt.setp(plt.gca().get_legend().get_texts(), color='grey') # wierd hacky way to make legend text grey, idk why this works
        # plt.savefig('plot.png')
        plt.show()

    



def testGoal(): 
    g = Goal(30, 90, "beast_mode")

    # Add 15 random entries to goal
    for i in range(20):
        g.addHours(datetime.datetime.utcnow() + datetime.timedelta(days=random.randint(0, 30), hours=random.randint(0, 24)), random.randint(0, 3))

    g.displayProgressGraph()
    # #create datetime object for 2 days from now
    # twoDaysFromNow = datetime.datetime.utcnow() + datetime.timedelta(days=2)
    # fiveDaysFromNow = datetime.datetime.utcnow() + datetime.timedelta(days=5)
    # sevenDaysFromNow = datetime.datetime.utcnow() + datetime.timedelta(days=7)
    # fortyDaysFromNow = datetime.datetime.utcnow() + datetime.timedelta(days=40) # error
    
    # g.addHours(datetime.datetime.utcnow(), 1)
    # g.addHours(datetime.datetime.utcnow(), 1)
    # g.addHours(datetime.datetime.utcnow(), 1)

    # g.addHours(twoDaysFromNow, 1.0)
    # g.addHours(twoDaysFromNow, 1.)
    # g.addHours(fiveDaysFromNow, 2.2)
    
    # g.addHours(sevenDaysFromNow, 3.0)
    # g.addHours(fortyDaysFromNow, 4) # error


    # print(g.getInitMessage())
    # print(g.timeWorkedPerDay)

if __name__ == "__main__":
    testGoal()