import numpy as np
import json
import random

utility = np.zeros(shape = (5 ,3 ,4 ,2,5)) 
policy = np.zeros(shape = (5 ,3 ,4 ,2,5), dtype=object) 

step_cost = -20
gamma = 0.999


sim_path = []
# center, n, s, w , e
position_key = {
    0 : "C",
    1 : "N",
    2 : "S" ,
    3 : "W" ,
    4 : "E"    
}

actions_position = {
    "C" : {
        "UP" : 1,
        "DOWN": 2,
        "LEFT" : 3,
        "RIGHT":4,
        "STAY":0,
        "SHOOT":0,
        "HIT":0,
    },

    "N" : {
        "DOWN" : 0,
        "STAY" : 1,
        "CRAFT" : 1
    },

    "S" : {
        "UP" : 0,
        "STAY" : 2,
        "GATHER" : 2
    },

    "W" : {

        "RIGHT" :0, 
        "SHOOT" :3,
        "STAY" : 3
    },
    "E" : {
        "LEFT" : 0,
        "SHOOT" : 4,
        "HIT" : 4,
        "STAY" : 4,
    }, 
}

Movement_actions = ["UP","DOWN","LEFT","RIGHT","STAY"]

policy = np.zeros(shape = (5 ,3 ,4 ,2,5), dtype=object) 


# start = [3,0,0,0,4]
start = [0, 2, 0, 1, 4]



def get_policy():
    global policy

    f = open('part_2_policy.json')
    data = json.load(f)
    policy = (np.array(data))


def Movement_Dormant(position, Newposition, material, arrow, health):

    state = np.zeros(shape= (4,5), dtype = object)
    state[0] = [Newposition,material,arrow,0,health]
    state[1] = [Newposition,material,arrow,1,health]

    if(position == 3 or position == 4):
        return random.choice(state[:2])
    
    state[2] = [4,material,arrow,0,health]
    state[3] = [4,material,arrow,1,health]
   
    return random.choice(state)

  

def SHOOT_Dormant (position,material,arrow,health):

    state = np.zeros(shape= (4,5), dtype = object)
    state[0] = [position,material,arrow - 1,0,max(0,health-1)]
    state[1] = [position,material,arrow - 1,1,max(0,health-1)]
    if(position == 3 or position == 4):
        return random.choice(state[:2])
    
    state[2] = [position,material,arrow - 1,0,health]
    state[3] = [position,material,arrow - 1,1,health]
   
    return random.choice(state)

  


def HIT_Dormant (position,material,arrow,health):

    state = np.zeros(shape= (6,5), dtype = object)
    state[0] = [position,material,arrow,0,max(0,health-2)]
    state[1] = [position,material,arrow,1,max(0,health-2)]
    
    if(position == 3 or position == 4):
        return random.choice(state[:2])

    state[2] = [position,material,arrow,0,health]
    state[3] = [position,material,arrow,1,health]
   
    return random.choice(state)
    

def CRAFT_Dormant (position,material,arrow,health):

    state = np.zeros(shape= (6,5), dtype = object)
    state[0] = [position,material - 1,min(arrow+1,3),0,health]
    state[1] = [position,material - 1,min(arrow+1,3),1,health]
    state[2] = [position,material - 1,min(arrow+2,3),0,health]
    state[3] = [position,material - 1,min(arrow+2,3),1,health]
    
    if(position == 3 or position == 4):
        return random.choice(state[:4])

    state[4] = [position,material - 1,3,0,health]
    state[5] = [position,material - 1,3,1,health]
    return random.choice(state)


def GATHER_Dormant (position,material,arrow,health):

    state = np.zeros(shape= (4,5), dtype = object)
    state[0] = [position,min(2,material+1),arrow,0,health]
    state[1] = [position,min(2,material+1),arrow,1,health]
    
    if(position == 3 or position == 4):
        return random.choice(state[:2])

    state[2] = [position,material,arrow,0,health]
    state[3] = [position,material,arrow,1,health]

    return random.choice(state)

 

def Movement_Ready(position,Newposition,material,arrow,health):

    state = np.zeros(shape= (4,5), dtype = object)
    state[0] = [Newposition,material,arrow,1,health]
    state[1] = [4,material,arrow,1,health]

    if position == 0 or position == 4:
        state[2] = [position,material,0,0,min(4,health+1)]
        return random.choice(state[:3])

    else:

        state[3] = [Newposition,material,arrow,0,health]
        state[4]= [4,material,arrow,0,health]
        return random.choice(state)


def SHOOT_Ready(position,material,arrow,health):

    state = np.zeros(shape= (4,5), dtype = object)
    state[0] = [position,material,arrow - 1,1,max(0,health-1)]
    state[1] = [position,material,arrow - 1,1,health]
    
    if position == 0 or position == 4:
        state[2] = [position,material,0,0,min(health+1,4)]
        return state[0]
        

    else :
        state[3] = [position,material,arrow - 1,0,max(0,health-1)]
        state[4]= [position,material,arrow - 1,0,health]
        return state[3]
    

def HIT_Ready(position,material,arrow,health):

    state = np.zeros(shape= (4,5), dtype = object)
    state[0] = [position,material,arrow,1,max(0,health-2)]
    state[1] = [position,material,arrow,1,health]
    
    if position == 0 or position == 4:
        state[2] = [position,material,0,0,min(4,health+1)]
        return random.choice(state[:3])
        

    else :
        state[3] = [position,material,arrow,0,max(0,health - 2)]
        state[4]= [position,material,arrow,0,health]
        return random.choice(state)

  

def CRAFT_Ready(position,material,arrow,health):

    state = np.zeros(shape= (6,5), dtype = object)
    state[0] = [position,material-1,min(arrow+1,3),1,health]
    state[1] = [position,material-1,min(arrow+2,3),1,health]
    state[2] = [position,material-1,3,1,health]
    
    if position == 0 or position == 4:
        state[3] = [position,material,0,0,min(4,health+1)]
        return random.choice(state[:4])
        

    else :
        state[3] = [position,material-1,min(arrow+1,3),0,health]
        state[4]= [position,material-1,min(arrow+2,3),0,health]
        state[5] = [position,material-1,3,0,health]
        return random.choice(state)



def GATHER_Ready(position,material,arrow,health):

    
    state = np.zeros(shape= (4,5), dtype = object)
    state[0] = [position,min(2,material+1),arrow,1,health]
    state[1] = [position,material,arrow,1,health]

    
    if position == 0 or position == 4:
        state[2] = [position,material,0,0,health]
        return random.choice(state[:3])
        

    else :
        state[3] = [position,min(2,material+1),arrow,0,health]
        state[4]= [position,material,arrow,0,health]
        return random.choice(state)




def Ready(action,position,Newposition,material,arrow,health):

    if action in Movement_actions:
        
        return Movement_Ready(position,Newposition,material,arrow,health)
    
    if action == "SHOOT":
        
        return SHOOT_Ready(position,material,arrow,health)
    
    if action == "HIT":
        
        return HIT_Ready(position,material,arrow,health)

    if action == "CRAFT":

        return CRAFT_Ready(position,material,arrow,health)
    
    if action == "GATHER":
        
        return GATHER_Ready(position,material,arrow,health)


def Dormant(action,position,Newposition,material,arrow,health):

    if action in Movement_actions:

        return Movement_Dormant(position,Newposition,material,arrow,health)
    
    if action == "SHOOT":
        
        return SHOOT_Dormant (position,material,arrow,health)
    
    if action == "HIT":
        
        return HIT_Dormant(position,material,arrow,health)

    if action == "CRAFT":
        
        return CRAFT_Dormant(position,material,arrow,health)
    
    if action == "GATHER":
        
        return GATHER_Dormant(position,material,arrow,health)
 


def Ready(action,position,Newposition,material,arrow,health):

    if action in Movement_actions:
        
        return Movement_Ready(position,Newposition,material,arrow,health)
    
    if action == "SHOOT":
        
        return SHOOT_Ready(position,material,arrow,health)
    
    if action == "HIT":
        
        return HIT_Ready(position,material,arrow,health)

    if action == "CRAFT":

        return CRAFT_Ready(position,material,arrow,health)
    
    if action == "GATHER":
        
        return GATHER_Ready(position,material,arrow,health)


def Dormant(action,position,Newposition,material,arrow,health):

    if action in Movement_actions:

        return Movement_Dormant(position,Newposition,material,arrow,health)
    
    if action == "SHOOT":
        
        return SHOOT_Dormant (position,material,arrow,health)
    
    if action == "HIT":
        
        return HIT_Dormant(position,material,arrow,health)

    if action == "CRAFT":
        
        return CRAFT_Dormant(position,material,arrow,health)
    
    if action == "GATHER":
        
        return GATHER_Dormant(position,material,arrow,health)

  

def MM_state(action,position,New_position,material,arrow,state,health) : 

    if state == 1 :
        return Ready(action,position,New_position,material,arrow,health)

    if state == 0 : 
        return Dormant(action,position,New_position,material,arrow,health)



def simulator():
    
    global start
    action = policy[start[0]][start[1]][start[2]][start[3]][start[4]]
    New_position = actions_position[position_key[start[0]]][action]
   

    state = start
    
    print('Start State is : ', end = '' )
    print(position_key[state[0]], state[1], state[2], state[3], state[4] * 25)
    print()
    print()

    # f.write('Initial state is : ' + str((position_key[state[0]], state[1], state[2], state[3], state[4] * 25)) + '\n')
    

    while(state[4]!= 0):
       

        #Best action from policy table
        action = policy[state[0]][state[1]][state[2]][state[3]][state[4]]

        #New Position based on that action
        New_position = actions_position[position_key[state[0]]][action]
        
        new_state = MM_state(action,state[0],New_position,state[1],state[2],state[3],state[4])

        print('Current State : ', end = '')
        print(position_key[state[0]], state[1], state[2], state[3], state[4] * 25, end = '')

        print('     Action : ' , action, end = '')

        print('     Next State : ', end = '')
        print(position_key[new_state[0]], new_state[1], new_state[2], new_state[3], new_state[4] * 25, end = '')
        print()
        print()
        
        # f.write(str((position_key[state[0]], state[1], state[2], state[3], state[4] * 25)) + '  :  ' + 'Action :  ' + str(action) + 
            # + str((position_key[new_state[0]], new_state[1], new_state[2], new_state[3], new_state[4] * 25)) + '\n')
        
        state = new_state

        
    # f.write('final terminal state is : ' + str((position_key[state[0]], state[1], state[2], state[3], state[4] * 25)) + '\n')


    print('Final State is : ', end = '' )
    print(position_key[state[0]], state[1], state[2], state[3], state[4] * 25)

get_policy()
simulator()