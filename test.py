import numpy as np

utility = np.arange(600).reshape((5,4,3,2,5))

print(utility.shape())

# do you increase health when mm attacks me in nsw ?

# part 2 - task 2 - txt
# part 2 report
# part 2 simulator
# part 2 output

# part 3 get policy
# part 3 report
# part 3 output





# in order to save column wise A matrix


# # np.savetxt('output.txt', A)

#     A_fp = open("A_output.txt" , 'w')
#     # A = np.zeros((len(TRANSITION_TABLE) , len(R))) 
    
#     column_number = 0

#     for position in range(5):
#         for material in range(3):
#             for arrow in range(4):
#                 for state in range(2):
#                     for health in range(5):

#                         if health == 0:
#                             A_fp.write('COLUMN FOR STATE {} , {} , {} , {} , {} AND ACTION NONE\n'.format(position_key[position], material, arrow, state, health ))
#                             A_fp.write(str(A[: , column_number]))
#                             A_fp.write("\n\n")
#                             # print(column_number)
#                             column_number += 1
#                             continue

#                         for action,New_position in actions_position[position_key[position]].items():

#                             # not allowing invalid actions in A matrix
#                             if action == "SHOOT" and arrow == 0: continue
#                             if action == "CRAFT" and material == 0: continue

#                             A_fp.write('COLUMN FOR STATE {} , {} , {} , {} , {} AND ACTION {}\n'.format(position_key[position], material, arrow, state, health , action))
#                             A_fp.write(str(A[: , column_number]))
#                             A_fp.write("\n\n")
#                             # print(column_number)
#                             column_number += 1

#     A_fp.close()

