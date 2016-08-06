import time
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
# Hopf when delay between:  (.08 , .09)

# 
# # Components:
b1 = ExternalPopulation(bgfr, record=True)
i1 = InternalPopulation(tau_m=.05, v_min=0, v_max=1, dv=dv, update_method = 'gmres')
b1_i1 = Connection(b1, i1, nsyn_bg, weights=weight_bg)
i1_i1 = Connection(i1, i1, nsyn_recc, weights=weight_recc)
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


delay = .1



n = A0.shape[0]
N = 5
D=-cheb(N-1)*2/delay
tmp1 = np.kron(D[:N-1,:], np.eye(n))
tmp2 = np.hstack((A1,np.zeros((n,(N-2)*n)), A0))
tmp3 = spsp.csr_matrix(np.vstack((tmp1, tmp2)))

t0 = time.time()
w, v = spsp.linalg.eigs(tmp3, 1, return_eigenvectors=True, which='LR', ncv=100)
print time.time() - t0
print w
plt.plot(np.real(v))
plt.plot(np.imag(v))
plt.show()

# N = 5
# D=-cheb(N-1)*2/delay
# tmp1 = np.kron(D[:N-1,:], np.eye(n))
# tmp2 = np.hstack((A1,np.zeros((n,(N-2)*n)), A0))
# tmp3 = spsp.csr_matrix(np.vstack((tmp1, tmp2)))
# 
# t0 = time.time()
# w, v = spsp.linalg.eigs(tmp3, 1, return_eigenvectors=True, which='LR', ncv=100)
# print time.time() - t0
# print w
# plt.plot(np.real(v))
# plt.plot(np.imag(v))
# plt.show()


# for delay in [.1,.095,.09]:
#     
#     D=-cheb(N-1)*2/delay
#     tmp1 = np.kron(D[:N-1,:], np.eye(n))
#     tmp2 = np.hstack((A1,np.zeros((n,(N-2)*n)), A0))
#     tmp3 = spsp.csr_matrix(np.vstack((tmp1, tmp2)))
#     
#     t0 = time.time()
#     w, v = spsp.linalg.eigs(tmp3, 1, return_eigenvectors=True, sigma=w0 ncv=100, v0=v[:,0])
#     print time.time() - t0
#     print w






# w = spsp.linalg.eigs(M, 1000-2, return_eigenvectors=False)
# for wi in sorted(w):
#     print wi
# plt.plot(np.real(w), np.imag(w), '.')
# plt.show()

# for vi in v:
#     print vi
    
    
#     w = spsp.linalg.eigsh(tmp4, 3, return_eigenvectors=False, which='LA')
# w = spsp.linalg.eigs(tmp3, 3, return_eigenvectors=False, which='LR')
# w = [wi for wi in w if np.abs(wi)>1e-10]
# print w[-1]
# t0 = time.time()
# w, v = spsp.linalg.eigs(tmp3, 3, return_eigenvectors=True, which='LR')
# print time.time() - t0
# print w

# w = spsp.linalg.eigs(tmp3, 1, return_eigenvectors=False, which='LR', v0=v[:,0])
# print w
    

# sigma = -np.real(w[0])

# print 'started'
# t0 = time.time()
# w, v = spsp.linalg.eigs(tmp3, 1, return_eigenvectors=True, which='LM', ncv=100)
# print v.shape
# sigma = -np.real(w[0])
#  
# print time.time() - t0
# print sigma
#  
# w = spsp.linalg.eigs(tmp3, 3, return_eigenvectors=False, which='LM', ncv=100, sigma=sigma)
# print time.time() - t0
# print w

# for wi in sorted(w):
#     print wi
# plt.plot(np.real([1/(wi+-sigma)for wi in w]), np.imag(w), '.')
# print 'DONE'
# plt.show()


# 
# for wi in [wi for wi in w if np.abs(wi)>1e-10]:
#     print wi
    

    
# for wi in sorted(w):
#     print wi
# plt.plot(np.real(w), np.imag(w), '.')
# print 'DONE'
# plt.show()




# L = 33j
# for D in [.1]:#np.arange(0,.01,.001)[-1:]:
# 
# 
# 
#     def ff(guess):
#         M = A0+A1*np.exp(D*guess)     
#         w = sorted(spsp.linalg.eigs(M, 1000-2, return_eigenvectors=False), key=lambda x:np.real(x), reverse=False)
#         w = [wi for wi in w if np.abs(wi)>1e-5]
#         L = np.real(sorted(w)[-1])+np.abs(np.imag(sorted(w)[-1]))*1j
#         print D, L#, w
#         return L
#      
#     L = sopt.fixed_point(ff, L)


# for ii in range(10):
#     M = A0+A1
#     w = sorted(spsp.linalg.eigs(M, 10, return_eigenvectors=False), key=lambda x:np.real(x), reverse=False)
#     print w[-3:]

# for ii in range(20):
#     M = A0+A1*np.exp(D*(L))
#     w = spsp.linalg.eigs(M, 100, sigma=0, return_eigenvectors=False)
#     L = np.real(sorted(w)[-2])+np.abs(np.imag(sorted(w)[-2]))*1j
#     
#     print L
#     M = A0+A1*np.exp(D*(L))

# w = spsp.linalg.eigs(M, 100, sigma=0, return_eigenvectors=False)
# L = sorted(w)[-2]
# print L