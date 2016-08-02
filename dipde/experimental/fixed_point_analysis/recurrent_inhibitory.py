import warnings
import scipy.stats as sps
import matplotlib.pyplot as plt
from dipde.internals.internalpopulation import InternalPopulation
from dipde.internals.connection import Connection 
from dipde.internals.network import Network
from dipde.internals.externalpopulation import ExternalPopulation
from dipde.interfaces.access_matrices import get_leak_matrix, get_connection_flux_matrices
import numpy as np
import numpy.linalg as npla
import logging
logging.disable(logging.CRITICAL)
import scipy.optimize as sopt
import scipy.sparse as spsp
import scipy.io as sio
import numpy.matlib as npm


def cheb(N):
    
    x = np.cos(np.pi*np.arange(N+1)/N)
    c = np.array([2] + [1]*(N-1) + [2])*np.array([(-1)**ii for ii in range(N+1)])

    X = npm.repmat(x,1,N+1).reshape(N+1,N+1).T
    dX = X-X.T

    D = (np.outer(c,1./c))/(dX+(np.eye(N+1)))#      % off-diagonal entries
    return D - np.diag(np.sum(D, axis=1))#, x#;                 % diagonal entries










# def get_infinitesimal_perturbation(t0, sigma, amplitude):
#     rv = sps.norm(t0, sigma)
#     return lambda t: rv.pdf(t)*sigma*np.sqrt(2*np.pi)*amplitude
# 
dv = .001
nsyn_bg = 1
bgfr = 200
weight_bg = .1
weight_recc = -.1
nsyn_recc = 20
delay = .09  # (.08 , .09)
# 
# 
# # Components:
b1 = ExternalPopulation(bgfr, record=True)
i1 = InternalPopulation(tau_m=.05, v_min=0, v_max=1, dv=dv, update_method = 'gmres')
b1_i1 = Connection(b1, i1, nsyn_bg, weights=weight_bg, delays=0.0)
i1_i1 = Connection(i1, i1, nsyn_recc, weights=weight_recc, delays=delay)
# def chirp_fcn(n):
#     print n.t, n.population_list[1].curr_firing_rate
# network = Network([b1, i1], [b1_i1, i1_i1], update_callback=chirp_fcn)
# network.run(tf=20, dt=.0001)
# i1.plot()
# plt.show()
# 
# 
# 
# # Get matrices:
leak_matrix = get_leak_matrix(i1, sparse=False)
synaptic_matrix_bg, threshold_vector_bg = get_connection_flux_matrices(b1_i1, sparse=False)
synaptic_matrix_recc, _ = get_connection_flux_matrices(i1_i1, sparse=False)










# 
def f(ss_fr_guess):
       
    A = leak_matrix + (nsyn_bg*bgfr)*synaptic_matrix_bg + (nsyn_recc*ss_fr_guess)*synaptic_matrix_recc
 
    A[0,:] = 1
       
    b = np.zeros(A.shape[0])
    b[0]=1
        
    # Solve for steady state:
    try:
        p_star = npla.solve(A,b)
    except npla.linalg.LinAlgError:
           
        p_star = spsp.linalg.spsolve(A,b)
           
      
    # Steady state firing rate
    return np.dot(p_star, bgfr*nsyn_bg*threshold_vector_bg) 
    
    
ss_fr = sopt.fixed_point(f, 5)
 
# print ss_fr
 
# sys.exit()
 
A = leak_matrix + (nsyn_bg*bgfr)*synaptic_matrix_bg + (nsyn_recc*ss_fr)*synaptic_matrix_recc
A[0,:] = 1
   
b = np.zeros(A.shape[0])
b[0]=1
p_star = spsp.linalg.spsolve(A,b)


A0 = leak_matrix + nsyn_bg*bgfr*synaptic_matrix_bg + nsyn_recc*nsyn_bg*bgfr*np.dot(p_star,threshold_vector_bg)*synaptic_matrix_recc
A1 = nsyn_bg*nsyn_recc*bgfr*np.outer(synaptic_matrix_recc.dot(p_star), threshold_vector_bg)

n = A0.shape[0]

N=10
D=-cheb(N-1)*2/delay

tmp1 = np.kron(D[:N-1,:], np.eye(n))
tmp2 = np.hstack((A1,np.zeros((n,(N-2)*n)), A0))
tmp3 = spsp.csr_matrix(np.vstack((tmp1, tmp2)))

w = spsp.linalg.eigs(tmp3, 100, sigma=0, return_eigenvectors=False)
for wi in sorted(w):
    print wi
plt.plot(np.real(w), np.imag(w), '.')
print 'DONE'
plt.show()



# print tmp2.shape

# npla.eig(np.vstack)





# 
# i_tmp = InternalPopulation(tau_m=.05, v_min=0, v_max=1, dv=dv, update_method = 'gmres')
# network = Network([i_tmp], [])
# network.dt = 1.
# network.t0 = 1.
# network.ti = 1.
# i_tmp.initialize()
# i_tmp
# 
# p_ss = (i_tmp.edges.tolist(), p_star)
# 
# 
# # # Components:
# b1 = ExternalPopulation(bgfr, record=True)
# i1 = InternalPopulation(tau_m=.05, v_min=0, v_max=1, dv=dv, update_method = 'gmres', p0=p_ss, initial_firing_rate=ss_fr)
# b1_i1 = Connection(b1, i1, nsyn_bg, weights=weight_bg, delays=0.0)
# i1_i1 = Connection(i1, i1, nsyn_recc, weights=weight_recc, delays=delay)
# def chirp_fcn(n):
#     print n.t, n.population_list[1].curr_firing_rate
# network = Network([b1, i1], [b1_i1, i1_i1], update_callback=chirp_fcn)
# network.run(tf=1, dt=.0001)
# i1.plot()
# plt.show()

# 
# A = leak_matrix + (nsyn_bg*bgfr+nsyn_recc*ss_fr)*synaptic_matrix
# A[0,:] = 1
# b = np.zeros(A.shape[0])
# b[0]=1
# p_star = spsp.linalg.spsolve(A,b)
# 
# 
# alpha = np.dot(p_star, threshold_vector)
# 
# f0 = synaptic_matrix.dot(p_star)
# f1 = threshold_vector/((1-nsyn_recc*alpha)**2)
# 
# M = np.outer(f0,f1)
# 
# J = spsp.csc_matrix(leak_matrix + 
#                     bgfr*synaptic_matrix+
#                     nsyn_recc*bgfr*alpha/(1-nsyn_recc*alpha)*synaptic_matrix+
#                     nsyn_recc*bgfr*M)
# 
# w = spsp.linalg.eigs(J, 100, sigma=0, return_eigenvectors=False)
# for wi in sorted(w):
#     print wi
# plt.plot(np.real(w), np.imag(w), '.')
# print 'DONE'
# plt.show()
  
# print type(A)
#   

# A = spsp.csc_matrix(leak_matrix + 600.0*synaptic_matrix)
# w, _ = spsp.linalg.eigs(A, 10, sigma=0)
#  
# eigval_list = []
# for ii, wi in enumerate(sorted(w, reverse=True)):
#     print ii, wi, 
#     try:
#         w_new, vl_new = spsp.linalg.eigs(A, 1, sigma=wi, OPpart='i')
#     except ValueError:
#         w_new, vl_new = spsp.linalg.eigs(A, 1, sigma=wi)
#      
#     print w_new, npla.norm(A.dot(vl_new[:,0])-(w_new[0])*vl_new[:,0])
    
#     if npla.norm(A.dot(vl_new[:,0])-(w_new[0])*vl_new[:,0]) < 1e-10:
#         eigval_list.append(w_new[0])
#     else:
#         raise Exception
#      
# print sorted(eigval_list)

#     print w_new
 
#     print 
#     for delta in [0,1j,2j]:
#         print npla.norm(A.dot(vi)-(wi+delta)*vi)
     
# print sorted(w, reverse=True, key=lambda wi:np.real(wi))








# # # Compute steady state initial condition:
# A = spsp.csc_matrix(leak_matrix + (nsyn_bg*bgfr+nsyn_recc*ss_fr)*synaptic_matrix)
# A[0,:] = 1
#   
# b = np.zeros(A.shape[0])
# b[0]=1
# # 
# # # p_star = spsp.linalg.spsolve(A,b)
# #  
# # 
# # 
# p0 = spsp.linalg.spsolve(A,b)
# # 
# # # print p0
# # 
# f0 = np.dot(p0, (bgfr*nsyn_bg+nsyn_recc*ss_fr)*threshold_vector)
# # f0 = 0
# # 
# # # sys.exit()
# # 
# # Get grid: 
# i_tmp = InternalPopulation(tau_m=.05, v_min=0, v_max=1, dv=dv, update_method = 'gmres')
# network = Network([i_tmp], [])
# network.dt = 1.
# network.t0 = 1.
# network.ti = 1.
# i_tmp.initialize()
#  
#  
# b1 = ExternalPopulation(bgfr, record=False)
# i1 = InternalPopulation(tau_m=.05, v_min=0, v_max=1, dv=dv, update_method = 'gmres', p0=(i_tmp.edges.tolist(), p0), initial_firing_rate=f0)
# b1_i1 = Connection(b1, i1, nsyn_bg, weights=weight, delays=0.0)
# i1_i1 = Connection(i1, i1, nsyn_recc, weights=weight, delays=0.0)
# 
# be  = ExternalPopulation(get_infinitesimal_perturbation(.1,.0005,.001), record=False)
# be_i1 = Connection(be, i1, 1, weights=weight, delays=0.0)
# 
# 
# def chirp_fcn(n):
#     print n.t, ss_fr, n.population_list[1].curr_firing_rate
# network = Network([b1, i1, be], [b1_i1, i1_i1, be_i1], update_callback=chirp_fcn)
# network.run(tf=5, dt=.0001)
# i1.plot()
# plt.show()


# def chirp(n):
#     print n.t
#  
# network = Network([b1, i1], [b1_i1, i1_i1], update_callback=chirp)
# network.run(tf=5, dt=.0001)
#   
# ss_fr = i1.firing_rate_record[-1]
#   
# # print ss_fr
# i1.plot()
# plt.show()

# import pickle
# pickle.dump({'pv':i1.pv, 'edges':i1.edges[:-1]}, open('steady_state.p', 'w'))

# print i1.pv.shape
# print i1.edges.shape


# 
# 
# A = leak_matrix + (100+nsyn_recc*ss_fr)*synaptic_matrix
# A[0,:] = 1
# b = np.zeros(A.shape[0])
# b[0]=1
#  
# # Solve for steady state:
# p_star = npla.solve(A,b)
#  
# # Steady state firing rate
# print np.dot(p_star, (bgfr*nsyn_bg+nsyn_recc*ss_fr)*threshold_vector)
# 
# w, vl = npla.eig(A)
# 
# print sorted(np.real(w), reverse=True)













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

# print 'start'
# 
# # print np.where(A.todense() != 0)
# A_I, A_J = np.where(A.todense() != 0)
# A_val = A[A_I, A_J]
# A_shape = A.shape
# sio.savemat('tmp.mat',{'A_I':A_I, 'A_J':A_J, 'A_val':A_val, 'A_shape':A_shape})
# print 'done'

# b1 = ExternalPopulation(600, record=True)
# i1 = InternalPopulation(tau_m=.05, v_min=0, v_max=1, dv=dv, update_method = 'gmres')
# b1_i1 = Connection(b1, i1, 1, weights=weight, delays=0.0)
# def chirp_fcn(n):
#     print n.t
# network = Network([b1, i1], [b1_i1], update_callback=chirp_fcn)
# network.run(tf=.5, dt=.0001)
# i1.plot()
# plt.show()