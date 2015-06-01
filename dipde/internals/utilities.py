# Copyright 2013 Allen Institute
# This file is part of dipde
# dipde is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# dipde is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with dipde.  If not, see <http://www.gnu.org/licenses/>.

import numpy as np
import scipy.linalg as spla
import scipy.stats as sps
import scipy.integrate as spi
import bisect

def fraction_overlap(a1, a2, b1, b2):
    '''Calculate the fractional overlap between range (a1,a2) and (b1,b2).
    
    Used to compute a reallocation of probability mass from one set of bins to
    another, assuming linear interpolation.
    '''
    if a1 >= b1:    # range of A starts after B starts
        if a2 <= b2:    
            return 1       # A is within B
        if a1 >= b2:
            return 0       # A is after B
        # overlap is from a1 to b2
        return (b2 - a1) / (a2 - a1)
    else:            # start of A is before start of B
        if a2 <= b1:
            return 0       # A is completely before B
        if a2 >= b2:
            # B is subsumed in A, but fraction relative to |A|
            return (b2 - b1) / (a2 - a1)
        # overlap is from b1 to a2
        return (a2 - b1) / (a2 - a1) 
    

def redistribute_probability_mass(A, B):
    '''Takes two 'edge' vectors and returns a 2D matrix mapping each 'bin' in B
    to overlapping bins in A. Assumes that A and B contain monotonically increasing edge values.
    '''
    
    mapping = np.zeros((len(A)-1, len(B)-1))
    newL = 0
    newR = newL
    
    # Matrix is mostly zeros -- concentrate on overlapping sections
    for L in range(len(A)-1):
        
        # Advance to the start of the overlap
        while newL < len(B) and B[newL] < A[L]:
            newL = newL + 1
        if newL > 0:
            newL = newL - 1
        newR = newL
        
        # Find end of overlap
        while newR < len(B) and B[newR] < A[L+1]:
            newR = newR + 1
        if newR >= len(B):
            newR = len(B) - 1

        # Calculate and store remapping weights
        for j in range(newL, newR):
            mapping[L][j] = fraction_overlap(A[L], A[L+1], B[j], B[j+1])

    return mapping

def leak_matrix(v, tau):
    'Given a list of edges, construct a leak matrix with time constant tau.'
    
    zero_bin_ind_list = get_zero_bin_list(v)
    
    # Initialize:
    A = np.zeros((len(v)-1,len(v)-1))

    # Positive leak:
    delta_w_ind = -1
    for source_ind in np.arange(max(zero_bin_ind_list)+1, len(v)-1):
        target_ind = source_ind + delta_w_ind
        dv = v[source_ind+1]-v[source_ind]
        bump_rate = v[source_ind+1]/(tau*dv)
        A[source_ind, source_ind] -= bump_rate
        A[target_ind, source_ind] += bump_rate
    
    # Negative leak:
    delta_w_ind = 1
    for source_ind in np.arange(0, min(zero_bin_ind_list)):
        target_ind = source_ind + delta_w_ind
        dv = v[source_ind]-v[target_ind]
        bump_rate = v[source_ind]/(tau*dv)
        A[source_ind, source_ind] -= bump_rate
        A[target_ind, source_ind] += bump_rate
        
    return A
    
def flux_matrix(v, w, lam, p=1):
    'Compute a flux matrix for voltage bins v, weight w, firing rate lam, and probability p.'
    
    zero_bin_ind_list = get_zero_bin_list(v)
    
    # Flow back into zero bin:
    if w > 0:
        
        # Outflow:
        A = -np.eye(len(v)-1)*lam*p
        
        # Inflow:
        A += redistribute_probability_mass(v+w, v).T*lam*p

        # Threshold:
        flux_to_zero_vector = -A.sum(axis=0)
        for curr_zero_ind in zero_bin_ind_list:
            A[curr_zero_ind,:] += flux_to_zero_vector/len(zero_bin_ind_list)
    else:
        # Outflow:
        A = -np.eye(len(v)-1)*lam*p
        
        # Inflow:
        A += redistribute_probability_mass(v+w, v).T*lam*p
        
        
        missing_flux = -A.sum(axis=0)
        A[0,:] += missing_flux
        
        flux_to_zero_vector = np.zeros_like(A.sum(axis=0))

    return flux_to_zero_vector, A

def get_zero_bin_list(v):
    'Return a list of indices that map flux back to the zero bin.'

    # Cast here to avoid mistakes:    
    v = np.array(v)

    if len(np.where(v==0)[0]) == 1:
        zero_edge_ind = np.where(v==0)[0][0]
        if zero_edge_ind == 0:
            return [0]
        else:
            return [zero_edge_ind-1, zero_edge_ind]
    else:
        return [bisect.bisect_right(v, 0) - 1]
    
def get_v_edges(v_min, v_max, dv):
    'Construct voltage edegs, linear discretization.'
    
    edges = np.concatenate(( np.arange(v_min, v_max, dv), [v_max] ))
    
    edges[np.abs(edges) < np.finfo(np.float).eps] = 0
    
    return edges

def assert_probability_mass_conserved(pv):
    'Assert that probability mass in control nodes sums to 1.'
    
    try:
        assert np.abs(np.abs(pv).sum() - 1) < 1e-12
    except:                                                                                 # pragma: no cover
        raise Exception('Probability mass below threshold: %s' % (np.abs(pv).sum() - 1))    # pragma: no cover
        


def descretize(distribution, N, loc=0, scale=1, shape=[]):
    'Compute a discrete approzimation to a scipy.stats continuous distribution.'
 
    x_list = np.linspace(0,1,N+1)
    
    rv = sps.expon(*shape, loc=loc, scale=scale)
    y = np.zeros(len(x_list))
    for ii, x in enumerate(x_list):
        y[ii] = rv.ppf(x)
    
    mean = np.zeros(len(x_list)-1)
    height = np.zeros(len(x_list)-1)
    a = np.zeros(len(x_list)-1)
    for ii, yl_yr in enumerate(zip(y[:-1],y[1:])):
        yl, yr = yl_yr
        height[ii] = rv.cdf(yr) - rv.cdf(yl)
        
        def mu(x):
            return x*rv.pdf(x)
        mean[ii] = spi.quad(mu, yl, yr)[0]
        a[ii] = mean[ii]/height[ii]
        
    return a, height
 
def exact_update_method(J, pv, dt=.0001):
    'Given a flux matrix, pdate probabilty vector by computing the matrix exponential.'
    
    # Exact computation of propogation method, matrix exponential:
    pv = np.dot(spla.expm(J*dt), pv)
    assert_probability_mass_conserved(pv)
    return pv

def approx_update_method_tol(J, pv, tol=2.2e-16, dt=.0001, norm='inf'):
    'Approximate the effect of a matrix exponential, with residual smaller than tol.'
    
    # No order specified:
    J *= dt
    curr_err = np.inf
    counter = 0.
    curr_del = pv
    pv_new = pv
    
    while curr_err > tol:
        counter += 1
        curr_del = J.dot(curr_del)/counter
        pv_new += curr_del
        curr_err = spla.norm(curr_del, norm)

    
    try:
        assert_probability_mass_conserved(pv)
    except:                                                                                                                                                     # pragma: no cover
        raise Exception("Probabiltiy mass error (p_sum=%s) at tol=%s; consider higher order, decrease dt, or increase dv" % (np.abs(pv).sum(), tol))            # pragma: no cover
    
    return pv_new

def approx_update_method_order(J, pv, dt=.0001, approx_order=2):
    'Approximate the effect of a matrix exponential, truncating Taylor series at order \'approx_order\'.'
    
    # Iterate to a specific order:
    coeff = 1.
    curr_del = pv
    pv_new = pv
    for curr_order in range(approx_order):
        coeff *= curr_order+1
        curr_del = J.dot(curr_del*dt)
        pv_new += (1./coeff)*curr_del
    
    try:
        assert_probability_mass_conserved(pv_new)
    except:                                                                                                                                                             # pragma: no cover
        raise Exception("Probabiltiy mass error (p_sum=%s) at approx_order=%s; consider higher order, decrease dt, or increase dv" % (np.abs(pv).sum(), approx_order))  # pragma: no cover

    return pv_new
    