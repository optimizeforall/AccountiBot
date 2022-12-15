from logger import log
import datetime
import matplotlib.pyplot as plt
import matplotlib as mpl



class Plot:
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

    def show_plot(self):
        self.create_plot()
        plt.show()

    # returns png image of plot
    def generate_plot_image(self):
        self.create_plot()
        plt.savefig('./data/'+str(self.author_ID)+'.png', dpi=300, bbox_inches='tight')
        plt.close()
