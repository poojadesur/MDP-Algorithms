import numpy as np
import cvxpy as cp
import os

states = np.zeros(shape = (5 ,3 ,4 ,2,5)) 

# center, n, s, w , e
position_key = {
    0 : "Center",
    1 : "North",
    2 : "South" ,
    4 : "East",
    3 : "West" ,

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

# c - 672 actions
# n - 280 actions
# s - 312 actions
# e - 384 actions
# w - 288 actions

actions = 672 + 280 + 312 + 384 + 288

print(actions)

x = cp.Variable(shape=(actions,1), name="x")
r = []
index = np.arange(600).reshape((5,3,4,2,5))
A = np.zeros(shape = (600,1936))

def get_index(position, material, arrow,state, health ):
    
    global index
    return (index[position][material][arrow][state][health])


def Movement_Dormant(position, Newposition, material, arrow, health, colIdx):

    global A 
    
    prob = 0.85
    if position == 3 or position == 4: prob = 1.0

    #Curr Position : prob = 1
    ind = get_index(position, material, arrow,0, health)
    A[ind][colIdx] += 1

    #action success and monster D:
    idx = get_index(Newposition,material,arrow,0,health)
    A[idx][colIdx] -= (prob * 0.8)

    #action success and monster R:
    idx = get_index(Newposition,material,arrow,1,health)
    A[idx][colIdx] -= (prob * 0.2)

    #action fail and monster D:
    idx = get_index(4,material,arrow,0,health)
    A[idx][colIdx] -= ((1-prob) * 0.8)

    #action fail and monster R:
    idx = get_index(4,material,arrow,1,health)
    A[idx][colIdx] -= ((1 - prob) * 0.2)

    
def Shoot_Dormant (position,material,arrow,health,colIdx):

    global A 

    # center
    if(position == 0): hitprob = 0.5
    # east
    if(position == 4) : hitprob = 0.9
    # west
    if(position == 3): hitprob = 0.25
    
   
    #Curr Position : prob = 1
    ind = get_index(position, material, arrow,0, health)
    A[ind][colIdx] += 1
   
    #action success and monster D:
    idx = get_index(position, material, arrow -1, 0, max(0,health - 1))
    A[idx][colIdx] -= (hitprob * 0.8)

    #action success and monster R:
    idx = get_index(position, material, arrow -1, 1, max(0,health - 1))
    A[idx][colIdx] -= (hitprob * 0.2)

    #action fail and monster D:
    idx = get_index(position, material, arrow -1, 0, health)
    A[idx][colIdx] -= ((1 - hitprob) * 0.8)

    #action fail and monster R:
    idx = get_index(position, material, arrow -1, 1, health)
    A[idx][colIdx] -= ((1 - hitprob) * 0.2)


def Hit_Dormant (position,material,arrow,health,colIdx):
    
    global A 

    # center
    if(position == 0): hitprob = 0.1
    # east
    if(position == 4) : hitprob = 0.2

    #Curr Position : prob = 1
    ind = get_index(position, material, arrow,0, health)
    A[ind][colIdx] += 1

    #action success and monster D:
    ind = get_index(position, material, arrow,0,max(0,health-2))
    A[ind][colIdx] -= (hitprob * 0.8)

    #action success and monster R:
    ind = get_index(position, material, arrow,1, max(0,health-2))
    A[ind][colIdx] -= (hitprob * 0.2)
    
    #action fail and monster D:
    ind = get_index(position, material, arrow,0, health)
    A[ind][colIdx] -= ((1 - hitprob )* 0.8)
    
    #action fail and monster R:
    ind = get_index(position, material, arrow,1, health)
    A[ind][colIdx] -= ((1 - hitprob )* 0.2)


def Craft_Dormant (position,material,arrow,health,colIdx):

    global A 

    #Curr Position : prob = 1
    ind = get_index(position, material, arrow,0, health)
    A[ind][colIdx] += 1

    #build 1 arrow and monster D:
    idx = get_index(position,material-1,min(arrow+1,3),0,health)
    A[idx][colIdx] -= (0.5 * 0.8)

    #build 1 and monster R:
    idx = get_index(position,material-1,min(arrow+1,3),1,health)
    A[idx][colIdx] -= (0.5 * 0.2)

    #build 2 arrow and monster D:
    idx = get_index(position,material-1,min(arrow+2,3),0,health)
    A[idx][colIdx] -= (0.35 * 0.8)

    # build 2 and monster R:
    idx = get_index(position,material-1,min(arrow+2,3),1,health)
    A[idx][colIdx] -= (0.35 * 0.2)

    #build 3 arrow and monster D:
    idx = get_index(position,material-1,3,0,health)
    A[idx][colIdx] -= (0.15 * 0.8)

    #build 3 and monster R:
    idx = get_index(position,material-1,3,1,health)
    A[idx][colIdx] -= (0.15 * 0.2)


def Gather_Dormant (position,material,arrow,health,colIdx):

    global A 

    #Curr Position : prob = 1
    ind = get_index(position, material, arrow, 0, health)
    A[ind][colIdx] += 1

    #action success and monster D:
    idx = get_index(position,min(2,material+1),arrow,0,health)
    A[idx][colIdx] -= (0.75 * 0.8)

    #action success and monster R:
    idx = get_index(position,min(2,material+1),arrow,1,health)
    A[idx][colIdx] -= (0.75 * 0.2)

    #action fail and monster D:
    idx = get_index(position,material,arrow,0,health)
    A[idx][colIdx] -= (0.25 * 0.8)

    #action fail and monster R:
    idx = get_index(position,material,arrow,1,health)
    A[idx][colIdx] -= (0.25 * 0.2)


def Movement_Ready(position,Newposition,material,arrow,health,colIdx):

    global A 

    #Curr Position : prob = 1
    ind = get_index(position, material, arrow,1, health)
    A[ind][colIdx] += 1

    prob = 0.85
    if position == 3 or position == 4: prob = 1.0

    # MM doesnt attack, IJ success
    ind = get_index(Newposition, material, arrow,1, health)
    A[ind][colIdx] -= prob*0.5

    # MM doesnt attack, IJ failed
    ind = get_index(4, material, arrow, 1, health)
    A[ind][colIdx] -= (1-prob)*0.5

    # if IJ is in center or east
    if(position == 0 or position == 4):
        #MM attack, IJ always fail moves to East, -40 reward
        ind = get_index(position, material, 0, 0, min(4,health+1))
        A[ind][colIdx] -= 0.5

    else:
        #MM attack, IJ succeeded
        ind = get_index(Newposition, material, arrow, 0, health)
        A[ind][colIdx] -= prob * 0.5

        #MM attack, IJ fail
        ind = get_index(4, material, arrow, 0, health)
        A[ind][colIdx] -= (1-prob) * 0.5


def Shoot_Ready(position,material,arrow,health,colIdx):
    
    global A 

    # center
    if(position == 0): hitprob = 0.5
    # east
    if(position == 4) : hitprob = 0.9
    # west
    if(position == 3): hitprob = 0.25

    #Curret Position
    ind = get_index(position, material, arrow,1, health)
    A[ind][colIdx] += 1
    
    # MM doesnt attack, IJ success
    ind = get_index(position, material, arrow - 1,1, health - 1)
    A[ind][colIdx] -= (hitprob * 0.5)

    # MM doesnt attack, IJ fail
    ind = get_index(position, material, arrow - 1,1, health)
    A[ind][colIdx] -= ((1 -hitprob) * 0.5)

    # if IJ is in center or east
    if(position == 0 or position == 4):

        #MM attack, IJ always fail
        ind = get_index(position, material,0,0, min(health+1,4))
        A[ind][colIdx] -= (0.5)

    # MM cant do damage
    # If IJ is in N S W 
    else:

        # MM attack, IJ success
        ind = get_index(position, material,arrow - 1,0, max(0,health-1))
        A[ind][colIdx] -= (hitprob * 0.5)
        
        # MM attack, IJ fail
        ind = get_index(position, material,arrow - 1,0, health)
        A[ind][colIdx] -= ((1 -hitprob) * 0.5)


def Hit_Ready(position,material,arrow,health,colIdx):

    global A 

    # center
    if(position == 0): hitprob = 0.1
    # east
    if(position == 4) : hitprob = 0.2

    #Curret Position
    ind = get_index(position, material, arrow,1, health)
    A[ind][colIdx] += 1
    

    # MM doesnt attack, IJ success
    ind = get_index(position, material, arrow,1, max(0,health - 2))
    A[ind][colIdx] -= (hitprob * 0.5)

    
    # MM doesnt attack, IJ fail
    ind = get_index(position, material, arrow,1,health)
    A[ind][colIdx] -= ( (1 - hitprob) * 0.5)

    # if IJ is in center or east
    if(position == 0 or position == 4):

        #MM attack, IJ always fail, -40 reward
        ind = get_index(position, material,0,0,min(4,health+1))
        A[ind][colIdx] -= (0.5)

    # MM cant do damage
    # If IJ is in N S W 
    else:
        #MM attack, IJ succeeded
        ind = get_index(position, material,arrow,0,max(0,health-2))
        A[ind][colIdx] -= (hitprob * 0.5)

        #MM attack, IJ fail
        ind = get_index(position, material,arrow,0,health)
        A[ind][colIdx] -= ((1 - hitprob) * 0.5) 


def Craft_Ready(position,material,arrow,health,colIdx):

    global A 
    
    #Current Position
    ind = get_index(position, material, arrow,1, health)
    A[ind][colIdx] += 1

    # MM doesnt attack, IJ gets 1 arrow
    ind = get_index(position, material-1, min(arrow+1,3), 1, health)
    A[ind][colIdx] -= 0.5 * 0.5

    # MM doesnt attack, IJ gets 2 arrow
    ind = get_index(position, material-1, min(arrow+2,3), 1, health)
    A[ind][colIdx] -= 0.5 * 0.35

    # MM doesnt attack, IJ gets 3 arrow
    ind = get_index(position, material-1, 3, 1, health)
    A[ind][colIdx] -= 0.5 * 0.15

    # if IJ is in center or east
    if(position == 0 or position == 4):
        #MM attack, IJ always fail
        ind = get_index(position, material, 0, 0, min(4,health+1))
        A[ind][colIdx] -= 0.5

    # MM cant do damage
    else: 
        # MM attack, IJ gets 1 arrow
        ind = get_index(position, material-1, min(arrow+1,3), 0, health)
        A[ind][colIdx] -= 0.5 * 0.5

        # MM attack, IJ gets 2 arrow
        ind = get_index(position, material-1, min(arrow+2,3), 0, health)
        A[ind][colIdx] -= 0.5 * 0.35

        # MM attack, IJ gets 2 arrow
        ind = get_index(position, material-1, 3, 0, health)
        A[ind][colIdx] -= 0.5 * 0.15

def Gather_Ready(position,material,arrow,health,colIdx):

    global A 

    #Current Position
    ind = get_index(position, material, arrow,1, health)
    A[ind][colIdx] += 1

    # MM doesnt attack, IJ success
    ind = get_index(position, min(2,material+1), arrow, 1, health)
    A[ind][colIdx] -= 0.75 * 0.5

    # MM doesnt attack, IJ failed
    ind = get_index(position, material , arrow, 1, health)
    A[ind][colIdx] -= 0.25 * 0.5

    # if IJ is in center or east
    if(position == 0 or position == 4):

        #MM attack, IJ always fail, -40 reward  
        ind = get_index(position, material , 0 , 0, min(4,health+1))
        A[ind][colIdx] -= 0.5

    else:
        #MM attack, IJ succeeded
        ind = get_index(position, min(2,material+1) , arrow , 0, health)
        A[ind][colIdx] -= 0.75 * 0.5

        #MM attack, IJ fail
        ind = get_index(position, material , arrow , 0, health)
        A[ind][colIdx] -= 0.25 * 0.5


def Ready(action,position,Newposition,material,arrow,health,colIdx):

    if action in Movement_actions:
        
        Movement_Ready(position,Newposition,material,arrow,health,colIdx)
    
    if action == "Shoot":
        
        Shoot_Ready(position,material,arrow,health,colIdx)
    
    if action == "Hit":
        
        Hit_Ready(position,material,arrow,health,colIdx)

    if action == "Craft":

        Craft_Ready(position,material,arrow,health,colIdx)
    
    if action == "Gather":
        
        Gather_Ready(position,material,arrow,health,colIdx)


def Dormant(action,position,Newposition,material,arrow,health,colIdx):

    if action in Movement_actions:

        Movement_Dormant(position,Newposition,material,arrow,health,colIdx)
    
    if action == "Shoot":
        
        Shoot_Dormant (position,material,arrow,health,colIdx)
    
    if action == "Hit":
        
        Hit_Dormant(position,material,arrow,health,colIdx)

    if action == "Craft":
        
        Craft_Dormant(position,material,arrow,health,colIdx)
    
    if action == "Gather":
        
        Gather_Dormant(position,material,arrow,health,colIdx)


# reward vector and A appended
def MM_state(action,position,New_position,material,arrow,state,health,colIdx) : 
   
    global A
    global r
      
    if state == 1 :
        Ready(action,position,New_position,material,arrow,health,colIdx)
        if (position == 0 or position == 4): r.append(-40)
        else : r.append(-20)


    if state == 0 : 
        Dormant(action,position,New_position,material,arrow,health,colIdx)
        r.append(-20)

def Linear_Programming():

    global r
    global A
    global index
    global x
    # keeps track of index of action-state pairs that make up columns of A
    colIdx = 0

    for position in range(5):
        for material in range(3):
            for arrow in range(4):
                for state in range(2):
                    for health in range(5):

                        # reward always zero when Health zero - terminal state
                        if health == 0: 

                            r.append(0)
                            idx = index[position][material][arrow][state][health]
                            A[idx][colIdx] = 1
                            print(colIdx)
                            colIdx += 1
                            continue

                        for action,New_position in actions_position[position_key[position]].items():
                            
                            print(colIdx)
                            
                            # not allowing invalid actions in A matrix
                            if action == "Shoot" and arrow == 0: continue
                            if action == "Craft" and material == 0: continue

                            MM_state(action,position,New_position,material,arrow,state,health,colIdx)

                            colIdx += 1
    
    # np.savetxt('output.txt', A)

    A_fp = open("A_output.txt" , 'w')
    # A = np.zeros((len(TRANSITION_TABLE) , len(R))) 
    
    column_number = 0

    for position in range(5):
        for material in range(3):
            for arrow in range(4):
                for state in range(2):
                    for health in range(5):

                        if health == 0:
                            A_fp.write('COLUMN FOR STATE {} , {} , {} , {} , {} AND ACTION NONE\n'.format(position_key[position], material, arrow, state, health ))
                            A_fp.write(str(A[: , column_number]))
                            A_fp.write("\n\n")
                            # print(column_number)
                            column_number += 1
                            continue

                        for action,New_position in actions_position[position_key[position]].items():

                            # not allowing invalid actions in A matrix
                            if action == "Shoot" and arrow == 0: continue
                            if action == "Craft" and material == 0: continue

                            A_fp.write('COLUMN FOR STATE {} , {} , {} , {} , {} AND ACTION {}\n'.format(position_key[position], material, arrow, state, health , action))
                            A_fp.write(str(A[: , column_number]))
                            A_fp.write("\n\n")
                            # print(column_number)
                            column_number += 1

    A_fp.close()

    #starting position   C,2,3,R,100
    start_idx = get_index(0,2,3,1,4)
    alpha = np.zeros(shape = (600,1))
    alpha[start_idx] = 1

    constraints = [ cp.matmul(A,x) == alpha, x>=0]
    
    objective = cp.Maximize(cp.matmul(r,x))

    problem = cp.Problem(objective, constraints)

    solution = problem.solve()
    print(solution)

    print(x.value)

    Get_policy()

    # print(r)
    # print(A)

def Tupple_create(position, material, arrow, state, health):
    
    five_tuple = ()

    return 


def Get_policy():

    policy = []
    
    
    
    for position in range(5):
        for material in range(3):
            for arrow in range(4):
                for state in range(2):
                    for health in range(5):

                        if health == 0:
                            policy.append([position, material, arrow, health])
                            idx = index[position][material][arrow][state][health]
                            A[idx][colIdx] = 1
                            print(colIdx)
                            colIdx += 1
                            continue

                        for action,New_position in actions_position[position_key[position]].items():

                            # not allowing invalid actions in A matrix
                            if action == "Shoot" and arrow == 0: continue
                            if action == "Craft" and material == 0: continue

                            A_fp.write('COLUMN FOR STATE {} , {} , {} , {} , {} AND ACTION {}\n'.format(position_key[position], material, arrow, state, health , action))
                            A_fp.write(str(A[: , column_number]))
                            A_fp.write("\n\n")
                            # print(column_number)
                            column_number += 1


Linear_Programming()
Get_policy()                            

                    


                     

