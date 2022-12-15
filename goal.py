from matplotlib import figure
from numpy import sort 
from logger import log
import datetime
import matplotlib.pyplot as plt
import matplotlib as mpl
from utils import *
import plot

class Goal(plot.Plot):
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

        days_worked = ((datetime.datetime.utcnow() - self.start_date).total_seconds() / (60*60*24)) - self.days_off
        days_left = round(self.goal_duration - (days_worked) - self.days_off, 2) # 86400 seconds in a day
        hours_per_day = round((self.hour_goal - self.total_hours_worked) / days_left, 2)
        percent_complete = round(self.total_hours_worked / self.hour_goal * 100, 2)
        hours_left = round(self.hour_goal - self.total_hours_worked, 2)

        message = f'Your goal, *{self.goal_title}*, is **{percent_complete}%** complete. You\'ve totaled **{round(self.total_hours_worked, 2)}hrs**, with **{hours_left}hrs** remaining.\n'
        message += f'You have **{days_left} days** left to complete this goal with {self.days_off} days off.\n'
        message += f'You must work **{hours_per_day} hours per day** to complete this goal on time.\n'

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

    def days_remaining(self):
        return (self.end_date - datetime.datetime.utcnow()).days
    