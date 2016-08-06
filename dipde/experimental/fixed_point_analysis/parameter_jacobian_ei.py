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
import scipy.linalg as spla
import scipy.sparse as spsp
import scipy.io as sio
import numpy.matlib as npm
import sys
import time
np.set_printoptions(linewidth=200, formatter={'float':'{:10.5f}'.format})

dv = .001
we = .1
wi = -.1
bgfr, nsyn_bg, nsyn_00, nsyn_01, nsyn_10, nsyn_11, delay = 40, 5, 5, 5, 2, 20, .035  # .035 stable,, .035 unstable

# bgfr, nsyn_bg, nsyn_00, nsyn_01, nsyn_10, nsyn_11, delay = np.array([bgfr, nsyn_bg, nsyn_00, nsyn_01, nsyn_10, nsyn_11, delay]) + .5*np.array([  -0.00025,   -0.00198,    0.00455,    0.00470,   -0.00160,   -0.00145,    0.00361]) 
# bgfr, nsyn_bg, nsyn_00, nsyn_01, nsyn_10, nsyn_11, delay = np.array([bgfr, nsyn_bg, nsyn_00, nsyn_01, nsyn_10, nsyn_11, delay]) + 1.*np.array([  -0.00001,   -0.00009,    0.00024,    0.00022,    0.00002,   -0.00005,    0.00000])
bgfr, nsyn_bg, nsyn_00, nsyn_01, nsyn_10, nsyn_11, delay = np.array([bgfr, nsyn_bg, nsyn_00, nsyn_01, nsyn_10, nsyn_11, delay]) + .5*np.array([   0.00002,    0.00018,    0.28188,   -0.29071,   -0.09889,    0.09314,   -0.00031])
# 
# # Components:
# b0 = ExternalPopulation(bgfr, record=True)
# i0 = InternalPopulation(tau_m=.05, v_min=0, v_max=1, dv=dv, update_method = 'gmres')
# i1 = InternalPopulation(tau_m=.05, v_min=0, v_max=1, dv=dv, update_method = 'gmres')
# b0_i0 = Connection(b0, i0, nsyn_bg, weights=we, delays=0.0)
# b0_i1 = Connection(b0, i1, nsyn_bg, weights=we, delays=0.0)
# i0_i0 = Connection(i0, i0, nsyn_00, weights=we, delays=0.0)
# i0_i1 = Connection(i0, i1, nsyn_01, weights=we, delays=0.0)
# i1_i0 = Connection(i1, i0, nsyn_10, weights=wi, delays=0.0)
# i1_i1 = Connection(i1, i1, nsyn_11, weights=wi, delays=delay)
# connection_list = [b0_i0, b0_i1, i0_i0, i0_i1, i1_i0, i1_i1]
# def chirp_fcn(n):
#     print n.t, n.population_list[1].curr_firing_rate, n.population_list[2].curr_firing_rate
# network = Network([b0, i0, i1], connection_list, update_callback=chirp_fcn)
# network.run(tf=5, dt=.0001)
#     
# fig = plt.figure()
# ax0 = fig.add_subplot(2, 1, 1)
# i0.plot(ax=ax0)
# ax1 = fig.add_subplot(2, 1, 2)
# i1.plot(ax=ax1)
#     
# plt.show()
#   
# sys.exit()

def get_matrices():
 
    dv = .001
    nsyn_bg = 1
    bgfr = 200
    we = .1
    wi = -.1
    nsyn_00, nsyn_01, nsyn_10, nsyn_11 = 5, 5, 2, 20
    
    # Components:
    b0 = ExternalPopulation(bgfr, record=True)
    i0 = InternalPopulation(tau_m=.05, v_min=0, v_max=1, dv=dv, update_method = 'gmres')
    i1 = InternalPopulation(tau_m=.05, v_min=0, v_max=1, dv=dv, update_method = 'gmres')
    b0_i0 = Connection(b0, i0, nsyn_bg, weights=we, delays=0.0)
    b0_i1 = Connection(b0, i1, nsyn_bg, weights=we, delays=0.0)
    i0_i0 = Connection(i0, i0, nsyn_00, weights=we, delays=0.0)
    i0_i1 = Connection(i0, i1, nsyn_01, weights=we, delays=0.0)
    i1_i0 = Connection(i1, i0, nsyn_10, weights=wi, delays=0.0)
    i1_i1 = Connection(i1, i1, nsyn_11, weights=wi, delays=0.0)
    
    L = get_leak_matrix(i1)
    Se, te = get_connection_flux_matrices(b0_i0)
    Si, _ = get_connection_flux_matrices(i1_i0)
    
    return L, Se, Si, te

L, Se, Si, te = get_matrices()

def steady_state_function(x, bgfr, nsyn_bg, nsyn_00, nsyn_01, nsyn_10, nsyn_11, delay):
    
    # Unpack:
    f0, f1 = x
     
    # Population 0:
    A = L + (nsyn_bg*bgfr+nsyn_00*f0)*Se + nsyn_10*f1*Si     
    A[0,:] = 1       
    b = np.zeros(A.shape[0])
    b[0]=1
    f0_new = np.dot(npla.solve(A,b), (bgfr*nsyn_bg+nsyn_00*f0)*te)
    
    # Population 1:
    A = L + (nsyn_bg*bgfr+nsyn_01*f0)*Se + nsyn_11*f1*Si     
    A[0,:] = 1       
    b = np.zeros(A.shape[0])
    b[0]=1
    f1_new = np.dot(npla.solve(A,b), (bgfr*nsyn_bg+nsyn_01*f0)*te)
    
    return np.array([f0_new, f1_new])


# Compute steady state:
f0_ss, f1_ss = sopt.fixed_point(steady_state_function, np.array([14,9]), args=(bgfr, nsyn_bg, nsyn_00, nsyn_01, nsyn_10, nsyn_11, delay))

# Compute initial guesses for eigenvector and eigenvalue:
# # Components:
b1 = ExternalPopulation(bgfr, record=True)
i1 = InternalPopulation(tau_m=.05, v_min=0, v_max=1, dv=dv, update_method = 'gmres')
b1_i1 = Connection(b1, i1, nsyn_bg, weights=we, delays=0.0)
i1_i1 = Connection(i1, i1, 0, weights=wi, delays=0.0)
 
def cheb(N):
    x = np.cos(np.pi*np.arange(N+1)/N)
    c = np.array([2] + [1]*(N-1) + [2])*np.array([(-1)**ii for ii in range(N+1)])
    X = npm.repmat(x,1,N+1).reshape(N+1,N+1).T
    dX = X-X.T
    D = (np.outer(c,1./c))/(dX+(np.eye(N+1)))#      % off-diagonal entries
    return D - np.diag(np.sum(D, axis=1))#, x#;                 % diagonal entries
 
leak_matrix = get_leak_matrix(i1, sparse=False)
synaptic_matrix_bg, threshold_vector_bg = get_connection_flux_matrices(b1_i1, sparse=False)
synaptic_matrix_recc, _ = get_connection_flux_matrices(i1_i1, sparse=False)
A = L + (nsyn_bg*bgfr+nsyn_01*f0_ss)*Se + nsyn_11*f1_ss*Si     
A[0,:] = 1       
b = np.zeros(A.shape[0])
b[0]=1
p_star = npla.solve(A,b)
A0 = leak_matrix + (nsyn_bg*bgfr+nsyn_01*f0_ss)*synaptic_matrix_bg + nsyn_11*(nsyn_bg*bgfr+nsyn_01*f0_ss)*np.dot(p_star,threshold_vector_bg)*synaptic_matrix_recc
A1 = (nsyn_bg*bgfr+nsyn_01*f0_ss)*nsyn_11*np.outer(synaptic_matrix_recc.dot(p_star), threshold_vector_bg)
n = A0.shape[0]
N=6
D=-cheb(N-1)*2/delay
tmp1 = np.kron(D[:N-1,:], np.eye(n))
tmp2 = np.hstack((A1,np.zeros((n,(N-2)*n)), A0))
tmp3 = spsp.csr_matrix(np.vstack((tmp1, tmp2)))
t0 = time.time()
w, v = spsp.linalg.eigs(tmp3, 5, return_eigenvectors=True, which='LR', ncv=150)
print delay, time.time() - t0
w_list = [(wi, vi) for wi, vi in zip(w,v.T) if np.abs(wi) > 1e-8]
eig_list_sorted = sorted(w_list, key=lambda x:np.real(x[0]), reverse=True)
w_crit, v_crit = eig_list_sorted[0]

print f0_ss, f1_ss, w_crit
sys.exit()

# w_crit = [w_crit]
# w_v_dict = {}
# for curr_delay in np.arange(.04, .02, -.001):
#     w_crit, v_crit = spsp.linalg.eigs(tmp3, 1, return_eigenvectors=True, sigma=w_crit[0], ncv=150, v0=v_crit)
#     D=-cheb(N-1)*2/curr_delay
#     tmp1 = np.kron(D[:N-1,:], np.eye(n))
#     tmp2 = np.hstack((A1,np.zeros((n,(N-2)*n)), A0))
#     tmp3 = spsp.csr_matrix(np.vstack((tmp1, tmp2)))
#     print curr_delay, w_crit
#     w_v_dict[curr_delay] = w_crit, v_crit
# w_d_list = [(w, d) for d, (w, v) in w_v_dict.items()]
# w_min, d_min = sorted(w_d_list, key=lambda x:np.abs(np.real(x[0])))[0]
# w_IC, v_IC = w_v_dict[d_min]
# # print d_min, delay
# np.testing.assert_almost_equal(d_min, delay)
# print

def get_ev(x):
    
    bgfr, nsyn_bg, nsyn_00, nsyn_01, nsyn_10, nsyn_11, delay = x
    f0_ss_internal, f1_ss_internal = sopt.fixed_point(steady_state_function, np.array([f0_ss, f1_ss]), args=x)
    A = L + (nsyn_bg*bgfr+nsyn_01*f0_ss_internal)*Se + nsyn_11*f1_ss_internal*Si     
    A[0,:] = 1       
    b = np.zeros(A.shape[0])
    b[0]=1
    p_star_internal = npla.solve(A,b)
    A0 = leak_matrix + (nsyn_bg*bgfr+nsyn_01*f0_ss_internal)*synaptic_matrix_bg + nsyn_11*(nsyn_bg*bgfr+nsyn_01*f0_ss_internal)*np.dot(p_star_internal,threshold_vector_bg)*synaptic_matrix_recc
    A1 = (nsyn_bg*bgfr+nsyn_01*f0_ss_internal)*nsyn_11*np.outer(synaptic_matrix_recc.dot(p_star_internal), threshold_vector_bg)
    n = A0.shape[0]
    N=6
    D=-cheb(N-1)*2/delay
    tmp1 = np.kron(D[:N-1,:], np.eye(n))
    tmp2 = np.hstack((A1,np.zeros((n,(N-2)*n)), A0))
    tmp3 = spsp.csr_matrix(np.vstack((tmp1, tmp2)))
    t0 = time.time()
    w = spsp.linalg.eigs(tmp3, 5, return_eigenvectors=False, which='LR', ncv=150)
    w_nonzero = [wi for wi in w if np.abs(wi) > 1e-8]
    w_crit = sorted(w_nonzero, key=lambda x:np.real(x))[-1]
    print delay, time.time() - t0, w_crit
    return w_crit
    
#     w_crit = spsp.linalg.eigs(tmp3, 20, return_eigenvectors=False, sigma=w_IC[0], ncv=150, v0=v_IC[:,0])
#     print w_crit





# JACOBIAN COMPUTATION WITH NULLSPACE:
def get_jacobian(xk, nk):
     
    epsilon = 1.*xk/100
     
    def f(x, ii):
        if ii in [0,1]:
            return  sopt.fixed_point(steady_state_function, np.array([f0_ss, f1_ss]), args=x)[ii]
        elif ii == 2:
            return np.real(get_ev(x))
        elif ii == 3:
            return np.imag(get_ev(x))
        else: 
            raise Exception 
            
    jacobian_list = []
    for ii in range(nk):
        jacobian_list.append( sopt.approx_fprime(xk, f, epsilon, ii))
         
    return np.array(jacobian_list)


J = get_jacobian(np.array([bgfr, nsyn_bg, nsyn_00, nsyn_01, nsyn_10, nsyn_11, delay]), 4)

np.save('J.npy', J)

print J
print

U, s, Vt = spla.svd(J)
gtz = (s>0).sum()
ltz = len(s)-gtz
S_inv = np.diag(1./s[:gtz])
Vt_tilde = Vt[:gtz,:] 
P = Vt_tilde.T.dot(S_inv).dot(U[:gtz,:gtz].T)
for p in P.T:
    print p
    
    
    
    
    
    
    
    
    
# leak_matrix = get_leak_matrix(i1, sparse=False)
# synaptic_matrix_bg, threshold_vector_bg = get_connection_flux_matrices(b1_i1, sparse=False)
# synaptic_matrix_recc, _ = get_connection_flux_matrices(i1_i1, sparse=False)
# A = L + (nsyn_bg*bgfr+nsyn_01*f0_ss)*Se + nsyn_11*f1_ss*Si     
# A[0,:] = 1       
# b = np.zeros(A.shape[0])
# b[0]=1
# p_star = npla.solve(A,b)
# A0 = leak_matrix + (nsyn_bg*bgfr+nsyn_01*f0_ss)*synaptic_matrix_bg + nsyn_11*(nsyn_bg*bgfr+nsyn_01*f0_ss)*np.dot(p_star,threshold_vector_bg)*synaptic_matrix_recc
# A1 = (nsyn_bg*bgfr+nsyn_01*f0_ss)*nsyn_11*np.outer(synaptic_matrix_recc.dot(p_star), threshold_vector_bg)
# n = A0.shape[0]
# N=6
# D=-cheb(N-1)*2/delay
# tmp1 = np.kron(D[:N-1,:], np.eye(n))
# tmp2 = np.hstack((A1,np.zeros((n,(N-2)*n)), A0))
# tmp3 = spsp.csr_matrix(np.vstack((tmp1, tmp2)))
# t0 = time.time()
# w, v = spsp.linalg.eigs(tmp3, 5, return_eigenvectors=True, which='LR', ncv=150)
# print w
# print delay, time.time() - t0
# w_list = [(wi, vi) for wi, vi in zip(w,v.T) if np.abs(wi) > 1e-8]
# eig_list_sorted = sorted(w_list, key=lambda x:np.real(x[0]), reverse=True)
# w_crit, v_crit = eig_list_sorted[0]
# print w_crit
# print v_crit
    
    
    
    
    
    
    
    
    
    
    
# plt.plot(np.real(w), np.imag(w), '.')
# print 'DONE'
# plt.show()



# print 

# # sys.exit()
# 
# def chirp_fcn(n):
#     pass
# #     print n.t, n.population_list[1].curr_firing_rate, n.population_list[2].curr_firing_rate
# network = Network([b0, i0, i1], connection_list, update_callback=chirp_fcn)
# network.run(tf=.2, dt=.0001)
# 
# fig = plt.figure()
# ax0 = fig.add_subplot(2, 1, 1)
# i0.plot(ax=ax0)
# ax1 = fig.add_subplot(2, 1, 2)
# i1.plot(ax=ax1)
# 
# plt.show()