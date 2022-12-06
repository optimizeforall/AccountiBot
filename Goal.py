from matplotlib import figure
from numpy import sort 
from logger import log
import datetime
import matplotlib.pyplot as plt
import matplotlib as mpl
import logging

class Goal:
    def __init__(self, goalDuration, hourGoal: float, goalTitle: str, daysOff=0, authorID=None, authorName=None):
        log.info(f'Creating new goal: {goalTitle}')
        self.goalDuration = goalDuration
        self.hourGoal = hourGoal
        self.goalTitle = goalTitle
        self.startDate = datetime.datetime.utcnow()
        self.endDate = self.startDate + datetime.timedelta(days=goalDuration)
        self.daysOff = daysOff
        self.hoursPerDay = hourGoal / (goalDuration - self.daysOff)
        self.timeWorked = [] # list of touples (time of entry, hoursWorked)
        self.succeeded = False
        self.totalHoursWorked = 0
        self.authorID = authorID
        self.authorName = authorName

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
            log.info(f'Adding {hours} hours for day {dayInGoal} / {self.goalDuration} for {self.goalTitle}.')
            self.timeWorked.append((time, hours)) # This isn't necessary, but I want to keep track of all entries for now
            self.totalHoursWorked += hours
            # Determine if goal is complete
            if self.succeeded == False and self.totalHoursWorked >= self.hourGoal:
                log.debug(f'Goal completed! Total hours worked: {self.totalHoursWorked}')
                self.succeeded = True
                log.info(f'Goal {self.goalTitle} succeeded!')

    def getInitMessage(self):
        """
        Your goal, beast_mode, will last 10 days, and require 30 hours of recorded work.
        It begins now, and ends Thur October 3rd, 2022 at 11:59 PM.
        This requires an average of 3hrs of work / day with 0 days off.
        If you fall behind in tracking, I'll get on you casez. 
        If you need help regarding using this bot, type !gh
        """

        # make trailing float on 3 digits long

        message = f'Your goal, *{self.goalTitle}*, will last **{self.goalDuration} days, and require {self.hourGoal} hours of recorded work**.\n'
        message += f'It begins now, and ends ***{self.endDate.strftime("%a %B %dth, %Y at %I:%M %p")}*** UTC.\n'
        message += f'This requires an average of **{round(self.hoursPerDay, 2)}hrs of work / day** with {self.daysOff} days off.\n'
        message += f'If you fall behind in tracking, *I\'ll get on you case. 💪* Good luck!\n'
        message += f'\nIf you need help regarding using this bot, type !gh'

        return message

    def showPlot(self):
        self.createPlot()
        plt.show()

    # returns png image of plot
    def generatePlotImage(self):
        self.createPlot()
        plt.savefig('./Data/'+str(self.authorID)+'.png', dpi=300, bbox_inches='tight')
        plt.close()

    def plotInit(self):
        font = {
        'weight' : 'bold',
        'size'   : 22}

        # make axis labels bigger
        mpl.rc('font', **font)
        mpl.rcParams['lines.linewidth'] = .5
        mpl.rcParams['lines.linestyle'] = '-'
        mpl.rcParams['axes.facecolor'] = 'gainsboro' # background color
        mpl.rcParams['toolbar'] = 'None' # Remove toolbar
        mpl.rcParams['figure.facecolor'] = 'gainsboro' # Remove white space around graph        
        # Add grid lines
        mpl.rcParams['axes.grid'] = True
        mpl.rcParams['grid.color'] = 'black'
        mpl.rcParams['grid.linewidth'] = 0.08
        # Display x and y axis and make color of text black
        mpl.rcParams['axes.edgecolor'] = 'black'
        mpl.rcParams['axes.labelcolor'] = 'black'
        mpl.rcParams['xtick.color'] = 'black'
        mpl.rcParams['ytick.color'] = 'black'
        # Show label 'hours' on y-axis, make label color black
        mpl.rcParams['ytick.labelsize'] = 10
        mpl.rcParams['ytick.labelcolor'] = 'black'
        mpl.rcParams['ytick.labelleft'] = True
        # Show label 'days' on x-axis, make label color black
        mpl.rcParams['xtick.labelsize'] = 10
        mpl.rcParams['xtick.labelcolor'] = 'black'
        mpl.rcParams['xtick.labelbottom'] = True

        # Remove ticks on x-axis
        mpl.rcParams['xtick.bottom'] = False
        mpl.rcParams['ytick.left'] = False

    def daysRemaining(self):
        return (self.endDate - datetime.datetime.utcnow()).days
    
    
    def createPlot(self):
        self.plotInit()
 
        # Curate x and y values
        x = [i[0].timestamp() for i in self.timeWorked]
        y = [i[1] for i in self.timeWorked] # create list of hours worked for each entry
        # Sort x and y values by x values
        x, y = zip(*sorted(zip(x, y)))
        # sum of each index up to current index 
        y = [sum(y[:i+1]) for i in range(len(y))] # e.g. [1, 2, 3, 4] -> [1, 3, 6, 10]
        log.debug(f'Sum of hours worked: {y[-1]}')
        # get current axis
        axis = plt.gca()
        # Set x axis length
        axis.set_xlim(0, self.goalDuration)
        # Scale x axis to be in days
        x = [((i - self.startDate.timestamp()) / (60*60*24)) for i in x]

        print('x: ', x)
        print('y: ', y)

        # If largest y value is greater than goal, set y axis to largest y value
        if y[-1] > self.hourGoal: 
            axis.set_ylim([0, y[-1]*1.1])
        else:
            axis.set_ylim([0, round(self.hourGoal * 1.1)])

        log.info(f'Generating plot for {self.goalTitle}')

        # Create figure
        plt.title(f'\'{self.goalTitle}\' Progress Chart ({self.authorName})', pad=10)
        plt.xlabel('Days')
        plt.ylabel('Hours')
        plt.gcf().set_size_inches(15, 10)

        # Plot data
        plt.plot(x, y, '-o', color='black',linewidth=1.5, markersize=5, markerfacecolor='black', markeredgewidth=1)

        # Draw goal line at goal, if goal is reached, draw line in green, else draw in red
        if y[-1] > self.hourGoal:
            plt.axhline(y=self.hourGoal, color='g', linestyle='-', linewidth=2, label=f'Goal {self.hourGoal}hrs (REACHED +{round(y[-1] - self.hourGoal, 2)}hrs)')
        else:
            plt.axhline(y=self.hourGoal, color='r', linestyle='-', linewidth=2, label=f'Goal {self.hourGoal}hrs ({round(self.hourGoal - y[-1], 2)}hrs left)')
        
        # Draw half-way line, if halfway is reached, draw line in green, else draw in red
        if y[-1] >= self.hourGoal / 2:
            plt.axhline(y=self.hourGoal / 2, color='green', linestyle=':', linewidth = 2, label=f'Halfway {int(round(self.hourGoal / 2, 2))}hrs (REACHED)')
        else:
            plt.axhline(y=self.hourGoal / 2, color='red', linestyle=':', linewidth = 2, label=f'Halfway {int(round(self.hourGoal / 2, 2))}hrs')

        # Legend, set color to grey, set location to upper left... 
        plt.legend(bbox_to_anchor=(.98, 0.02), loc='lower right', prop={'size': 10}, facecolor='white', edgecolor='black', framealpha=1)
        # plt.setp(plt.gca().get_legend().get_texts(), color='grey') # wierd hacky way to make legend text grey, idk why this works