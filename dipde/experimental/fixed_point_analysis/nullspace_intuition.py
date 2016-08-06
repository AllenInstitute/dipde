import scipy.linalg as spla
import numpy as np
np.set_printoptions(linewidth=200, formatter={'float':'{:10.5f}'.format})

J = np.load('J.npy')
print 'Jacobian:'
print J
print

U, s, Vt = spla.svd(J)
gtz = (s>0).sum()
ltz = len(s)-gtz
S_inv = np.diag(1./s[:gtz])
Vt_tilde = Vt[:gtz,:] 
P = Vt_tilde.T.dot(S_inv).dot(U[:gtz,:gtz].T) # Columns are cardinal perturbation vector
print 'Canonical perturbation vectors:'
for p in P.T:
    print p, J.dot(p)
print
    
N = Vt[gtz:,:].T    # Columns span Null(J)

Perm, L, U = spla.lu(N)

print 'Intuitive Nullspace:'
for l in (Perm.dot(L).T):
    print l


