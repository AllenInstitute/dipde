from dipde.internals.internalpopulation import InternalPopulation
from dipde.internals.connection import Connection 
from dipde.interfaces.access_matrices import get_leak_matrix, get_connection_flux_matrices
import numpy as np
import numpy.linalg as npla
import logging
logging.disable(logging.CRITICAL)


# Components:
i1 = InternalPopulation(tau_m=.02, v_min=0, v_max=.02, dv=.001)
c1 = Connection(None, i1, 1, weights=.005)

# Get matrices:
leak_matrix = get_leak_matrix(i1)
synaptic_matrix, threshold_vector = get_connection_flux_matrices(c1)

A = leak_matrix + 100*synaptic_matrix
A[0,:] = 1
b = np.zeros(A.shape[0])
b[0]=1

# Solve for steady state:
p_star = npla.solve(A,b)

# Steady state firing rate
print np.dot(p_star, 100*threshold_vector)















# A2 = leak_matrix + 100./(1-np.dot(p_star, threshold_vector))*synaptic_matrix
# w, vl = npla.eig(A2)
# 
# # print w[np.argmin(np.abs(w))]
# # print np.dot(A2, vl[:,np.argmin(np.abs(w))])
# # print np.dot(A2, p_star)
# 
# for x, y in zip(vl[:,np.argmin(np.abs(w))]/vl[:,np.argmin(np.abs(w))].sum(), p_star):
#     print x, y
# print 


# print w[np.argmin(np.abs(w))]
# 
# # print b
# # print vl[np.argmin(np.abs(w))]
# print np.dot(p_star, vl[np.argmin(np.abs(w))])
# 
# # 
# print np.dot(p_star, (100+6.41481426)*threshold_vector)
# 
# p_star2 = p_star.copy()
# tmp = p_star2[1:3].sum()
# 
# p_star2[1:3] = 0
# 
# p_star2[4] += tmp
# 
# print np.dot(p_star, (100+6.41481426)*threshold_vector)


# def chirp_dot_product(int_pop):
#     
#     M = leak_matrix + (100./(1-np.dot(int_pop.pv, threshold_vector)))*synaptic_matrix
#     M[0,:]=1
# #     print 100.*np.dot(int_pop.pv, threshold_vector)/(1-np.dot(int_pop.pv, threshold_vector))
# #     print sorted(np.abs(npla.eigvals(M)))
# 
# #     b = np.zeros(M.shape[0])
# #     b[0]=1
# #     p_star = npla.solve(A,b)
# #     print np.dot(p_star, threshold_vector)
#     
# #     curr_determinant = npla.det(M)    
# #     LHS = np.dot(M, int_pop.pv)
# #     print curr_determinant, np.sum(np.abs(LHS)), np.sum(np.abs(int_pop.pv))
# #     print curr_determinant, np.sum(np.abs(np.dot(leak_matrix + (100./(1-np.dot(int_pop.pv, threshold_vector)))*synaptic_matrix,int_pop.pv)))
# #     print 100.*np.dot(int_pop.pv, threshold_vector)/(1-np.dot(int_pop.pv, threshold_vector)), int_pop.curr_firing_rate
# #     print npla.det(leak_matrix + 100./(1-np.dot(int_pop.pv, threshold_vector))*synaptic_matrix)
# #     print np.dot(int_pop.pv, threshold_vector)
# 
# b1 = ExternalPopulation(100, record=True)
# i1 = InternalPopulation(tau_m=.02, v_min=0, v_max=.02, dv=dv, update_callback=chirp_dot_product)
# b1_i1 = Connection(b1, i1, 1, weights=.005, delays=0.0)
# i1_i1 = Connection(i1, i1, 1, weights=.005, delays=0.0)
# network = Network([b1, i1], [b1_i1, i1_i1])
# network.run(tf=.05, dt=.0001)
# 
# # print np.dot(i1.pv, threshold_vector)
# # print (100./(1-np.dot(i1.pv, threshold_vector)))
# # leak_matrix + (100./(1-np.dot(i1.pv, threshold_vector)))*synaptic_matrix
# # print np.sum(np.abs(np.dot(leak_matrix + (100./(1-np.dot(i1.pv, threshold_vector)))*synaptic_matrix,i1.pv)))
# 
# # print i1.firing_rate_record[-1]
# # 
# # print np.dot(i1.pv, (100+3.5723)*threshold_vector)
# 
# # print np.dot(i1.pv, threshold_vector)
# # 
# # print npla.det(leak_matrix + 100.*(1-np.dot(i1.pv, threshold_vector))*synaptic_matrix)
# 
# for x, y in zip( threshold_vector, i1.pv):
#     print x, y
