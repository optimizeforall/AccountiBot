from matplotlib import figure
from numpy import sort 
from logger import log
import datetime
import matplotlib.pyplot as plt
import matplotlib as mpl
import logging
from utils import *

class Goal:
    def __init__(self, goal_duration, hour_goal: float, goal_title: str, days_off=0, author_ID=None, author_name=None):
        log.info(f'Creating new goal: {goal_title}')
        self.goal_duration = goal_duration
        self.hour_goal = hour_goal
        self.goal_title = goal_title
        self.start_date = datetime.datetime.utcnow()
        self.end_date = self.start_date + datetime.timedelta(days=goal_duration)
        self.days_off = days_off
        self.hours_per_day = hour_goal / (goal_duration - self.days_off)
        self.time_worked = [] # list of touples (time_of_entry, hours_worked, commit_message, intention)
        self.succeeded = False
        self.total_hours_worked = 0
        self.author_ID = author_ID
        self.author_name = author_name

    def add_hours(self, time: datetime, hours: float, chunk_comment=None, chunk_intention=None):
        day_in_goal = (time - self.start_date).days
        start_date_str = self.start_date.strftime('%m/%d/%Y, %H:%M:%S')
        end_date_str = self.end_date.strftime('%m/%d/%Y, %H:%M:%S')
        entry_date_str = time.strftime('%m/%d/%Y, %H:%M:%S')

        # if day_in_goal is outside of goal range, print error and return
        # else, add hours to total_hours_worked
        if day_in_goal >= self.goal_duration or day_in_goal < 0:
            log.error(f'{entry_date_str} is outside of goal range: ({start_date_str}) - ({end_date_str})')
            return
        else:
            log.info(f'Adding {hours} hours for day {day_in_goal} / {self.goal_duration} for {self.goal_title}.')
            self.time_worked.append((time, hours, chunk_comment, chunk_intention)) # This isn't necessary, but I want to keep track of all entries for now
            self.total_hours_worked += hours
            # Determine if goal is complete
            if self.succeeded == False and self.total_hours_worked >= self.hour_goal:
                log.debug(f'Goal completed! Total hours worked: {self.total_hours_worked}')
                self.succeeded = True
                log.info(f'Goal {self.goal_title} succeeded!')


    def get_log(self):
        message = f'Here are all the time entries for {self.goal_title}:\n'

        # use enumerate to get index of entry
        for i, entry in enumerate(self.time_worked):
            hours = entry[1]
            minutes = round((hours - int(hours)) * 60)
            hours = int(hours)
            
            # Display log message if it exists
            log_message = f'- {entry[2]}'  if entry[2] != None else ''
            intention = f'(Intention: {entry[3]})' if entry[3] != None else ''

            message += f' {i+1}. {hours}:{minutes:02d} {log_message} {intention}\n'
        return message


    def get_status_message(self):
        """
        Your goal, beast_mode, is 50% complete. You've worked 15 hours out of 30.
        You have 15 days left to complete this goal with 0 days off.
        You must work 1.0 hours per day to complete this goal on time.
        """

        message = f'Your goal, *{self.goal_title}*, is **{round(self.total_hours_worked / self.hour_goal * 100, 2)}%** complete. You\'ve totaled **{round(self.total_hours_worked, 2)}hrs**, with **{round(self.hour_goal - self.total_hours_worked, 2)}hrs** remaining.\n'
        message += f'You have **{self.goal_duration - (datetime.datetime.utcnow() - self.start_date).days} days** left to complete this goal with {self.days_off} days off.\n'
        print(self.total_hours_worked, self.hour_goal, self.goal_duration, self.days_off)
        message += f'You must work **{round((self.hour_goal - self.total_hours_worked) / (self.end_date - datetime.datetime.utcnow()).days, 2)} hours per day** to complete this goal on time.\n'

        return message
        
    def get_init_message(self):
        """
        Your goal, beast_mode, will last 10 days, and require 30 hours of recorded work.
        It begins now, and ends Thur October 3rd, 2022 at 11:59 PM.
        This requires an average of 3hrs of work / day with 0 days off.
        If you fall behind in tracking, I'll get on you casez. 
        If you need help regarding using this bot, type !gh
        """

        # make trailing float on 3 digits long

        message = f'Your goal, *{self.goal_title}*, will last **{self.goal_duration} days, and require {self.hour_goal} hours of recorded work**.\n'
        message += f'It begins now, and ends ***{self.end_date.strftime("%a %B %dth, %Y at %I:%M %p")}*** UTC.\n'
        message += f'This requires an average of **{round(self.hours_per_day, 2)}hrs of work / day** with {self.days_off} days off.\n'
        message += f'If you fall behind in tracking, *I\'ll get on you case. 💪* Good luck!\n'
        message += f'\nIf you need help regarding using this bot, type !gh'

        return message

    def show_plot(self):
        self.create_plot()
        plt.show()

    # returns png image of plot
    def generate_plot_image(self):
        self.create_plot()
        plt.savefig('./data/'+str(self.author_ID)+'.png', dpi=300, bbox_inches='tight')
        plt.close()

    def initialize_plot(self):
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

    def days_remaining(self):
        return (self.end_date - datetime.datetime.utcnow()).days
    
    def create_plot(self):
        log.info(f'Attempting to generate plot for {self.goal_title}')
        self.initialize_plot()
 
        # Curate x and y values
        x = [i[0].timestamp() for i in self.time_worked]
        y = [i[1] for i in self.time_worked] # create list of hours worked for each entry
        # Sort x and y values by x values
        x, y = zip(*sorted(zip(x, y)))
        # sum of each index up to current index 
        y = [sum(y[:i+1]) for i in range(len(y))] # e.g. [1, 2, 3, 4] -> [1, 3, 6, 10]
        log.debug(f'Sum of hours worked: {y[-1]}')
        # get current axis
        axis = plt.gca()
        # Set x axis length
        axis.set_xlim(0, self.goal_duration)
        # Scale x axis to be in days
        x = [((i - self.start_date.timestamp()) / (60*60*24)) for i in x]

        # If largest y value is greater than goal, set y axis to largest y value
        if y[-1] > self.hour_goal: 
            axis.set_ylim([0, y[-1]*1.1])
        else:
            axis.set_ylim([0, round(self.hour_goal * 1.1)])


        # Create figure
        plt.title(f'{self.goal_title} Progress Chart ({self.author_name})', pad=10)
        plt.xlabel('Days')
        plt.ylabel('Hours')
        plt.gcf().set_size_inches(15, 10)

        # Plot data
        plt.plot(x, y, '-o', color='black',linewidth=1.5, markersize=5, markerfacecolor='black', markeredgewidth=1)

        # Draw goal line at goal, if goal is reached, draw line in green, else draw in red
        if y[-1] > self.hour_goal:
            plt.axhline(y=self.hour_goal, color='g', linestyle='-', linewidth=2, label=f'Goal {self.hour_goal}hrs (REACHED +{round(y[-1] - self.hour_goal, 2)}hrs)')
        else:
            plt.axhline(y=self.hour_goal, color='r', linestyle='-', linewidth=2, label=f'Goal {self.hour_goal}hrs ({round(self.hour_goal - y[-1], 2)}hrs left)')
        
        # Draw half-way line, if halfway is reached, draw line in green, else draw in red
        if y[-1] >= self.hour_goal / 2:
            plt.axhline(y=self.hour_goal / 2, color='green', linestyle=':', linewidth = 2, label=f'Halfway {int(round(self.hour_goal / 2, 2))}hrs (REACHED)')
        else:
            plt.axhline(y=self.hour_goal / 2, color='red', linestyle=':', linewidth = 2, label=f'Halfway {int(round(self.hour_goal / 2, 2))}hrs')

        # Legend, set color to grey, set location to upper left... 
        plt.legend(bbox_to_anchor=(.98, 0.02), loc='lower right', prop={'size': 10}, facecolor='white', edgecolor='black', framealpha=1)
        # plt.setp(plt.gca().get_legend().get_texts(), color='grey') # wierd hacky way to make legend text grey, idk why this works