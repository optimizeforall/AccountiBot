from logger import log
import pickle

def saveGoal(goalTitle, goal):
    try:
        with open('./Data/' + goalTitle + '.pickle', 'wb') as f:
            pickle.dump(goal, f)
            log.info('Saved goal: ' + goalTitle + '.pickle')
            f.close()
    except Exception as e:
        log.error("Error saving goal: " + str(e))

def goodFormat(pm):
    # !g [goal title] [goal duration in days] [hours to work] ?[rest days]
    if pm[0] == "!g":
        if len(pm) != 5 and len(pm) != 4:
            return False
        if not pm[2].isdigit() or not pm[3].isdigit():
            return False
        elif len(pm) == 5 and not pm[4].isdigit():
            return False

    # !ga [time in hours / minutes]
    if pm[0] == "!ga":
        if len(pm) != 2:
            return False
        # Must follow format 1h30m, 90m, 1h, 1.5h
        if not 'm' in pm[1] and not 'h' in pm[1]:
            return False
        
    # !gg
    if pm[0] == "!gg":
        if len(pm) != 2:
            return False
    return True