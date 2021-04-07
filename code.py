import numpy as np

utility = np.zeros(shape = (5 ,3 ,4 ,2,5)) 
policy = np.zeros(shape = (5 ,3 ,4 ,2,5), dtype=object) 

step_cost = -20
gamma = 0.999

# center, n, s, w , e
position_key = {
    0 : "Center",
    1 : "North",
    2 : "South" ,
    3 : "West" ,
    4 : "East"    
}

actions_position = {
    "Center" : {
        "Up" : 1,
        "Down": 2,
        "Left" : 3,
        "Right":4,
        "Stay":0,
        "Shoot":0,
        "Hit":0,
    },

    "North" : {
        "Down" : 0,
        "Stay" : 1,
        "Craft" : 1
    },

    "South" : {
        "Up" : 0,
        "Stay" : 2,
        "Gather" : 2
    },

    "West" : {

        "Right" :0, 
        "Shoot" :3,
        "Stay" : 3
    },
    "East" : {
        "Left" : 0,
        "Shoot" : 4,
        "Hit" : 4,
        "Stay" : 4,
    }, 
}

Movement_actions = ["Up","Down","Left","Right","Stay"]

def Movement_Dormant(position, Newposition, material, arrow, health):

    prob = 0.85
    if position == 3 or position == 4: prob = 1.0

    value = 0
    #action success and monster D:
    value += prob * 0.8 * ( step_cost + gamma * (utility[Newposition][material][arrow][0][health]))
    #action success and monster R:
    value += prob * 0.2 * ( step_cost + gamma * (utility[Newposition][material][arrow][1][health]))

    #action fail and monster D:
    value += (1-prob) * 0.8 * ( step_cost + gamma * (utility[4][material][arrow][0][health]))
    #action fail and monster R:
    value += (1-prob) * 0.2 * ( step_cost + gamma * (utility[4][material][arrow][1][health]))

    return value

def Shoot_Dormant (position,material,arrow,health):

    # center
    if(position == 0): hitprob = 0.5
    # east
    if(position == 4) : hitprob = 0.9
    # west
    if(position == 3): hitprob = 0.25

    #action success and Monster R
    value = 0

    # reward +50 when monster gets health 0
    reward = 0
    if(max(0,health-1) == 0): reward = 50

    #action success and monster D:
    value += hitprob * 0.8 * ( step_cost + reward + gamma * (utility[position][material][arrow - 1][0][max(0,health-1)]))
    #action success and monster R:
    value += hitprob * 0.2 * ( step_cost + reward + gamma * (utility[position][material][arrow - 1][1][max(0,health-1)]))
    #action fail and monster D:
    value += (1 - hitprob) * 0.8 * ( step_cost + gamma * (utility[position][material][arrow - 1][0][health]))
    #action fail and monster R:
    value += (1 - hitprob) * 0.2 * ( step_cost + gamma * (utility[position][material][arrow - 1][1][health]))

    return value


def Hit_Dormant (position,material,arrow,health):

    # center
    if(position == 0): hitprob = 0.1
    # east
    if(position == 4) : hitprob = 0.2

    value = 0

    # reward +50 when monster gets health 0
    reward = 0
    if(max(0,health-2) == 0): reward = 50

    #action success and monster D:
    value += hitprob * 0.8 * ( step_cost + reward + gamma * (utility[position][material][arrow][0][max(0,health-2)]))
    #action success and monster R:
    value += hitprob * 0.2 * ( step_cost + reward + gamma * (utility[position][material][arrow][1][max(0,health-2)]))
    #action fail and monster D:
    value += (1-hitprob) * 0.8 * ( step_cost + gamma * (utility[position][material][arrow][0][health]))
    #action fail and monster R:
    value += (1-hitprob) * 0.2 * ( step_cost + gamma * (utility[position][material][arrow][1][health]))

    return value

def Craft_Dormant (position,material,arrow,health):

    value = 0

    #build 1 arrow and monster D:
    value += 0.5 * 0.8 * ( step_cost + gamma * (utility[position][material - 1][min(arrow+1,3)][0][health]))
    #build 1 and monster R:
    value += 0.5 * 0.2 * ( step_cost + gamma * (utility[position][material - 1][min(arrow+1,3)][1][health]))
    
    #build 2 arrow and monster D:
    value += 0.35 * 0.8 * ( step_cost + gamma * (utility[position][material - 1][min(arrow+2,3)][0][health]))
    #build 2 and monster R:
    value += 0.35 * 0.2 * ( step_cost + gamma * (utility[position][material - 1][min(arrow+2,3)][1][health]))
    
    #build 3 arrow and monster D:
    value += 0.15 * 0.8 * ( step_cost + gamma * (utility[position][material - 1][3][0][health]))
    #build 3 and monster R:
    value += 0.15 * 0.2 * ( step_cost + gamma * (utility[position][material - 1][3][1][health]))

    return value


def Gather_Dormant (position,material,arrow,health):

    value = 0
    #action success and monster D:
    value += 0.75 * 0.8 * ( step_cost + gamma * (utility[position][min(2,material+1)][arrow][0][health]))
    #action success and monster R:
    value += 0.75 * 0.2 * ( step_cost + gamma * (utility[position][min(2,material+1)][arrow][1][health]))
    #action fail and monster D:
    value += 0.25 * 0.8 * ( step_cost + gamma * (utility[position][material][arrow][0][health]))
    #action fail and monster R:
    value += 0.25 * 0.2 * ( step_cost + gamma * (utility[position][material][arrow][1][health]))

    return value

def Movement_Ready(position,Newposition,material,arrow,health):

    prob = 0.85
    if position == 3 or position == 4: prob = 1.0

    value = 0

    # MM doesnt attack, IJ success
    value += prob * 0.5 * ( step_cost + gamma * (utility[Newposition][material][arrow][1][health]))
    # MM doesnt attack, IJ failed
    value += (1-prob) * 0.5 * ( step_cost + gamma * (utility[4][material][arrow][1][health]))

    # if IJ is in center or east
    if(position == 0 or position == 4):

        #MM attack, IJ always fail moves to East, -40 reward
        value += 0.5 * ( step_cost - 40 + gamma * (utility[position][material][0][0][min(4,health+1)]))

    else:
        #MM attack, IJ succeeded
        value += prob * 0.5 * ( step_cost + gamma * (utility[Newposition][material][arrow][0][health]))

        #MM attack, IJ fail
        value += (1-prob) * 0.5 * ( step_cost + gamma * (utility[4][material][arrow][0][health]))

    return value

def Shoot_Ready(position,material,arrow,health):

    # center
    if(position == 0): hitprob = 0.5
    # east
    if(position == 4) : hitprob = 0.9
    # west
    if(position == 3): hitprob = 0.25

    #action success and Monster R
    value = 0

    # reward +50 when monster gets health 0
    reward = 0
    if(max(0,health-1) == 0): reward = 50

    # MM doesnt attack, IJ success
    value += hitprob * 0.5 * ( step_cost + reward + gamma * (utility[position][material][arrow - 1][1][max(0,health-1)]))
    # MM doesnt attack, IJ fail
    value += (1 - hitprob) * 0.5 * ( step_cost + gamma * (utility[position][material][arrow - 1][1][health]))


    # if IJ is in center or east
    if(position == 0 or position == 4):

        #MM attack, IJ always fail, -40 reward
        value += 0.5 * ( step_cost - 40 + gamma * (utility[position][material][0][0][min(health+1,4)]))

    # MM cant do damage
    # If IJ is in N S W 
    else:

        # MM attack, IJ success
        value += hitprob * 0.5 * ( step_cost + reward + gamma * (utility[position][material][arrow - 1][0][max(0,health-1)]))
        # MM attack, IJ fail
        value += (1 - hitprob) * 0.5 * ( step_cost + gamma * (utility[position][material][arrow - 1][0][health]))

    return value

def Hit_Ready(position,material,arrow,health):

    # center
    if(position == 0): hitprob = 0.1
    # east
    if(position == 4) : hitprob = 0.2

    value = 0

    # reward +50 when monster gets health 0
    reward = 0
    if(max(0,health-2) == 0): reward = 50

    # MM doesnt attack, IJ success
    value += hitprob * 0.5 * ( step_cost + reward + gamma * (utility[position][material][arrow][1][max(0,health-2)]))
    # MM doesnt attack, IJ fail
    value += (1-hitprob) * 0.5 * ( step_cost + gamma * (utility[position][material][arrow][1][health]))

    # if IJ is in center or east
    if(position == 0 or position == 4):

        #MM attack, IJ always fail, -40 reward
        value += 0.5 * ( step_cost - 40 + gamma * (utility[position][material][0][0][min(4,health+1)]))

    # MM cant do damage
    # If IJ is in N S W 
    else:
        #MM attack, IJ succeeded
        value += hitprob * 0.5 * ( step_cost + reward + gamma * (utility[position][material][arrow][0][max(0,health - 2)]))

        #MM attack, IJ fail
        value += (1-hitprob) * 0.5 * ( step_cost + gamma * (utility[position][material][arrow][0][health]))

    return value

def Craft_Ready(position,material,arrow,health):

    value = 0

    # MM doesnt attack, IJ gets 1 arrow
    value += 0.5 * 0.5 * ( step_cost + gamma * (utility[position][material-1][min(arrow+1,3)][1][health]))
    # MM doesnt attack, IJ gets 2 arrow
    value += 0.5 * 0.35 * ( step_cost + gamma * (utility[position][material-1][min(arrow+2,3)][1][health]))
    # MM doesnt attack, IJ gets 3 arrow
    value += 0.5 * 0.15 * ( step_cost + gamma * (utility[position][material-1][3][1][health]))

    # if IJ is in center or east
    if(position == 0 or position == 4):

        #MM attack, IJ always fail, -40 reward
        value += 0.5 * ( step_cost - 40 + gamma * (utility[position][material][0][0][min(4,health+1)]))

    # MM cant do damage
    else: 
        # MM attack, IJ gets 1 arrow
        value += 0.5 * 0.5 * ( step_cost + gamma * (utility[position][material-1][min(arrow+1,3)][0][health]))
        # MM attack, IJ gets 2 arrow
        value += 0.5 * 0.35 * ( step_cost + gamma * (utility[position][material-1][min(arrow+2,3)][0][health]))
        # MM attack, IJ gets 2 arrow
        value += 0.5 * 0.15 * ( step_cost + gamma * (utility[position][material-1][3][0][health]))

    return value

def Gather_Ready(position,material,arrow,health):

    value = 0
    # MM doesnt attack, IJ success
    value += 0.75 * 0.5 * ( step_cost + gamma * (utility[position][min(2,material+1)][arrow][1][health]))
    # MM doesnt attack, IJ failed
    value += 0.25 * 0.5 * ( step_cost + gamma * (utility[position][material][arrow][1][health]))

    # if IJ is in center or east
    if(position == 0 or position == 4):

        #MM attack, IJ always fail, -40 reward
        value += 0.5 * ( step_cost - 40 + gamma * (utility[position][material][0][0][health]))

    else:
        #MM attack, IJ succeeded
        value += 0.75 * 0.5 * ( step_cost + gamma * (utility[position][min(2,material+1)][arrow][0][health]))

        #MM attack, IJ fail
        value += 0.25 * 0.5 * ( step_cost + gamma * (utility[position][material][arrow][0][health]))

    return value



def Ready(action,position,Newposition,material,arrow,health):

    if action in Movement_actions:
        
        return Movement_Ready(position,Newposition,material,arrow,health)
    
    if action == "Shoot":
        
        return Shoot_Ready(position,material,arrow,health)
    
    if action == "Hit":
        
        return Hit_Ready(position,material,arrow,health)

    if action == "Craft":

        return Craft_Ready(position,material,arrow,health)
    
    if action == "Gather":
        
        return Gather_Ready(position,material,arrow,health)


def Dormant(action,position,Newposition,material,arrow,health):

    if action in Movement_actions:

        return Movement_Dormant(position,Newposition,material,arrow,health)
    
    if action == "Shoot":
        
        return Shoot_Dormant (position,material,arrow,health)
    
    if action == "Hit":
        
        return Hit_Dormant(position,material,arrow,health)

    if action == "Craft":
        
        return Craft_Dormant(position,material,arrow,health)
    
    if action == "Gather":
        
        return Gather_Dormant(position,material,arrow,health)
    
def MM_state(action,position,New_position,material,arrow,state,health) : 

    if state == 1 :
        return Ready(action,position,New_position,material,arrow,health)

    if state == 0 : 
        return Dormant(action,position,New_position,material,arrow,health)


def Value_Iteration(delta):
    
    global utility

    max_diff = 0.002
    
    iteration = 0
    ok = 0

    while(1):
        max_diff = 0

        iteration+=1
        if ok == 1 : 
            ok = 2
        # print("iteration #" + str(iteration))

        new_utility = np.zeros(shape = (5 ,3 ,4 ,2,5)) 

        for material in range(3):
            for arrow in range(4):
                for state in range(2):

                    for position in range(5):

                        for health in range(5):
                            if health == 0:
                                policy[position][material][arrow][state][health] = "None"
                                continue

                            # i am at a state
                            maxStateValue = -10000000
                            
                            # all actions at this state
                            for action,New_position in actions_position[position_key[position]].items():
                                
                                # state value for a particular action

                                if (material == 0 and action == "Craft"): continue
                                if (arrow == 0 and action == "Shoot"): continue


                                state_value = MM_state(action,position,New_position,material,arrow,state,health)
                               
                                # print(state_value)
                                # print(position,material,arrow,state,health,action,state_value)

                                if(maxStateValue < state_value):
                                    maxStateValue = max(maxStateValue, state_value)
                                    policy[position][material][arrow][state][health] = action

                            new_utility[position][material][arrow][state][health] = maxStateValue
                            # print("max state value: " + str(maxStateValue))

                            prev_value = utility[position][material][arrow][state][health]
                            
                            max_diff = max(max_diff, abs(prev_value - maxStateValue))
        
        # print("maxdiff " + str(max_diff))               
        
        # for next iteration
        utility = np.copy(new_utility)
        # if iteration < 2 : print(utility)
        
        if(max_diff < delta) and ok == 0:
            print("condition met")
            ok = 1

        if ok == 2:break

Value_Iteration(0.001)
print("ran successfully")
# print(policy)


A_fp = open("VI_output.txt" , 'w')


for position in range(5):
    for material in range(3):
        for arrow in range(4):
            for state in range(2):
                for health in range(5):

                        A_fp.write('{} , {} , {} , {} , {} : {}\n'.format(position_key[position], material, arrow, state, health , policy[position][material][arrow][state][health]))
            
                       

A_fp.close()






                            