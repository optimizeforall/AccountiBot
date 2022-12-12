from logger import log
import pickle

# Load goal object from file usizng pickle
def load_goal(authorID): 
    with open('./data/goals/' + str(authorID) + '.pickle', 'rb') as f:
        log.info('Loading: ' + str(authorID) + '.pickle')
        goal = pickle.load(f)
    return goal
    
# Save goal object to file using pickle
def save_goal(goalTitle, goal):
    try:
        with open('./data/goals/' + goalTitle + '.pickle', 'wb') as f:
            pickle.dump(goal, f)
            log.info('Saved goal: ' + goalTitle + '.pickle')
    except Exception as e:
        log.error("Error saving goal: " + str(e))