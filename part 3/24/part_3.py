import numpy as np
import cvxpy as cp
import json

states = np.zeros(shape = (5 ,3 ,4 ,2,5)) 

# center, n, s, w , e
position_key = {
    0 : "C",
    1 : "N",
    2 : "S" ,
    4 : "E",
    3 : "W" ,

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

# c - 672 actions
# n - 280 actions
# s - 312 actions
# e - 384 actions
# w - 288 actions

actions = 672 + 280 + 312 + 384 + 288

x = cp.Variable(shape=(actions,1), name="x")
r = []
index = np.arange(600).reshape((5,3,4,2,5))
A = np.zeros(shape = (600,1936))
A = np.zeros(shape = (600,1936))
alpha = np.zeros(shape = (600,1))

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

    
def SHOOT_Dormant (position,material,arrow,health,colIdx):

    global A 

    # center
    if(position == 0): HITprob = 0.5
    # east
    if(position == 4) : HITprob = 0.9
    # west
    if(position == 3): HITprob = 0.25
    
   
    #Curr Position : prob = 1
    ind = get_index(position, material, arrow,0, health)
    A[ind][colIdx] += 1
   
    #action success and monster D:
    idx = get_index(position, material, arrow -1, 0, max(0,health - 1))
    A[idx][colIdx] -= (HITprob * 0.8)

    #action success and monster R:
    idx = get_index(position, material, arrow -1, 1, max(0,health - 1))
    A[idx][colIdx] -= (HITprob * 0.2)

    #action fail and monster D:
    idx = get_index(position, material, arrow -1, 0, health)
    A[idx][colIdx] -= ((1 - HITprob) * 0.8)

    #action fail and monster R:
    idx = get_index(position, material, arrow -1, 1, health)
    A[idx][colIdx] -= ((1 - HITprob) * 0.2)


def HIT_Dormant (position,material,arrow,health,colIdx):
    
    global A 

    # center
    if(position == 0): HITprob = 0.1
    # east
    if(position == 4) : HITprob = 0.2

    #Curr Position : prob = 1
    ind = get_index(position, material, arrow,0, health)
    A[ind][colIdx] += 1

    #action success and monster D:
    ind = get_index(position, material, arrow,0,max(0,health-2))
    A[ind][colIdx] -= (HITprob * 0.8)

    #action success and monster R:
    ind = get_index(position, material, arrow,1, max(0,health-2))
    A[ind][colIdx] -= (HITprob * 0.2)
    
    #action fail and monster D:
    ind = get_index(position, material, arrow,0, health)
    A[ind][colIdx] -= ((1 - HITprob )* 0.8)
    
    #action fail and monster R:
    ind = get_index(position, material, arrow,1, health)
    A[ind][colIdx] -= ((1 - HITprob )* 0.2)

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


def SHOOT_Ready(position,material,arrow,health,colIdx):
    
    global A 

    # center
    if(position == 0): HITprob = 0.5
    # east
    if(position == 4) : HITprob = 0.9
    # west
    if(position == 3): HITprob = 0.25

    #Curret Position
    ind = get_index(position, material, arrow,1, health)
    A[ind][colIdx] += 1
    
    # MM doesnt attack, IJ success
    ind = get_index(position, material, arrow - 1,1, health - 1)
    A[ind][colIdx] -= (HITprob * 0.5)

    # MM doesnt attack, IJ fail
    ind = get_index(position, material, arrow - 1,1, health)
    A[ind][colIdx] -= ((1 -HITprob) * 0.5)

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
        A[ind][colIdx] -= (HITprob * 0.5)
        
        # MM attack, IJ fail
        ind = get_index(position, material,arrow - 1,0, health)
        A[ind][colIdx] -= ((1 -HITprob) * 0.5)


def HIT_Ready(position,material,arrow,health,colIdx):

    global A 

    # center
    if(position == 0): HITprob = 0.1
    # east
    if(position == 4) : HITprob = 0.2

    #Curret Position
    ind = get_index(position, material, arrow,1, health)
    A[ind][colIdx] += 1
    

    # MM doesnt attack, IJ success
    ind = get_index(position, material, arrow,1, max(0,health - 2))
    A[ind][colIdx] -= (HITprob * 0.5)

    
    # MM doesnt attack, IJ fail
    ind = get_index(position, material, arrow,1,health)
    A[ind][colIdx] -= ( (1 - HITprob) * 0.5)

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
        A[ind][colIdx] -= (HITprob * 0.5)

        #MM attack, IJ fail
        ind = get_index(position, material,arrow,0,health)
        A[ind][colIdx] -= ((1 - HITprob) * 0.5) 


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
    
    if action == "SHOOT":
        
        SHOOT_Ready(position,material,arrow,health,colIdx)
    
    if action == "HIT":
        
        HIT_Ready(position,material,arrow,health,colIdx)

    if action == "CRAFT":

        Craft_Ready(position,material,arrow,health,colIdx)
    
    if action == "GATHER":
        
        Gather_Ready(position,material,arrow,health,colIdx)


def Dormant(action,position,Newposition,material,arrow,health,colIdx):

    if action in Movement_actions:

        Movement_Dormant(position,Newposition,material,arrow,health,colIdx)
    
    if action == "SHOOT":
        
        SHOOT_Dormant (position,material,arrow,health,colIdx)
    
    if action == "HIT":
        
        HIT_Dormant(position,material,arrow,health,colIdx)

    if action == "CRAFT":
        
        Craft_Dormant(position,material,arrow,health,colIdx)
    
    if action == "GATHER":
        
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
    global alpha
    global actions_position
    global position_key
    # keeps track of index of action-state pairs that make UP columns of A
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
                            # print(colIdx)
                            colIdx += 1
                            continue

                        for action,New_position in actions_position[position_key[position]].items():
                            
                            # print(colIdx)
                            
                            # not allowing invalid actions in A matrix
                            if action == "SHOOT" and arrow == 0: continue
                            if action == "CRAFT" and material == 0: continue

                            MM_state(action,position,New_position,material,arrow,state,health,colIdx)

                            colIdx += 1
    
    


    # print("COLIDX GOES UP TILL THIS FOR PRINTING IN FILE " + str(column_number))
    #starting position   C,2,3,R,100
    start_idx = get_index(0,2,3,1,4)
    alpha[start_idx] = 1

    constraints = [ cp.matmul(A,x) == alpha, x>=0]
    
    objective = cp.Maximize(cp.matmul(r,x))

    problem = cp.Problem(objective, constraints)

    solution = problem.solve()
    print(solution)

    # print(x.value)

    return solution



def Get_policy():

    global x
    global actions_position
    global position_key
    global alpha

    policy = []
    colIdx = 0

    
    for position in range(5):
        for material in range(3):
            for arrow in range(4):
                for state in range(2):
                    for health in range(5):
                        
                        
                        text_state =""
                        if state == 0:text_state = "D"
                        else : text_state = "R"

                        if health == 0:
                            policy.append([(position_key[position], material, arrow, text_state, 25*health), "NONE"])
                            # print(colIdx)
                            colIdx += 1
                            continue
                        
                        val= -1000
                        best_action = ""
                        for action, Newposition in actions_position[position_key[position]].items():

                            # not allowing invalid actions in A matrix
                            if action == "SHOOT" and arrow == 0: continue
                            if action == "CRAFT" and material == 0: continue
                            

                            if(val < x[colIdx][0].value):
                                val = x[colIdx][0].value
                                best_action = action
                                
                            
                            colIdx += 1

                        policy.append([(position_key[position], material, arrow, text_state, 25*health), best_action])

    # print(policy)
    # print("COLIDX GOES UP TILL THIS FOR POLICY " + str(colIdx))
    # print(len(policy))

    return policy

def Create_JSONDict(solution,policy):
    
    global A
    global r
    global x
    global alpha 
    
    output = {

        "a" : A.tolist(),
        "r" : r,
        "alpha" : alpha.tolist(),
        "x" : x.value.tolist(),
        "policy" : policy,
        "objective" : solution
    }


    with open('./outputs/part_3_output.json', '+w') as file:
        json_string = json.dumps(output, indent = 1)
        file.write(json_string)

    # with open('test.json', '+w') as file:
    #     json.dump(position_key, file)
        

                     
solution = Linear_Programming()
policy = Get_policy()    
# Create_JSONDict(solution,policy) 

# checking json file is loadable
# submission_fp = open("part_3_output.json" , 'r')
# sub_data = json.load(submission_fp)
# submission_fp.close()
# print(sub_data.keys())

                    


                     

