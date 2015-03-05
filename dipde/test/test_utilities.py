import numpy as np
import dipde.internals.utilities as util
import scipy.linalg as spla

def test_get_zero_bin_list():
    
    assert util.get_zero_bin_list([0,1,2]) == [0]
    assert util.get_zero_bin_list([-1,0,1]) == [0,1]
    assert util.get_zero_bin_list([-2,-1,1]) == [1] 

def test_flux_ex():
    
    # Flux example 1:
    v_min = 0
    v_max = .02
    tau=.02
    w = .005
    dv_n = 500
    dv = .005/dv_n
    v = np.arange(v_min, v_max+dv, dv)
    
    A = util.leak_matrix(v, tau)
    flux_to_zero_vector = np.zeros_like(A.sum(axis=0))
    
    flux_to_zero_vector_tmp, A_tmp = util.flux_matrix(v, w, 100)
    A += A_tmp    
    flux_to_zero_vector += flux_to_zero_vector_tmp
    
    x = spla.solve(A+np.ones_like(A), np.ones_like(v[:-1]))
    FR_ss = np.dot(x, flux_to_zero_vector)
    
    assert np.abs(FR_ss - 5.28031853301) < 1e-10

def test_flux_ex_inh_border():
    
    # Flux example 2:
    v_min = 0
    v_max = .02
    tau=.02
    w = .005
    dv_n = 500
    dv = .005/dv_n
    v = np.arange(v_min, v_max+dv, dv)
    
    A = util.leak_matrix(v, tau)
    flux_to_zero_vector = np.zeros_like(A.sum(axis=0))
    
    flux_to_zero_vector_tmp, A_tmp = util.flux_matrix(v, w, 100)
    A += A_tmp    
    flux_to_zero_vector += flux_to_zero_vector_tmp
        
    flux_to_zero_vector_tmp, A_tmp = util.flux_matrix(v, -w, 100)
    A += A_tmp
    flux_to_zero_vector += flux_to_zero_vector_tmp 
    
    x = spla.solve(A+np.ones_like(A), np.ones_like(v[:-1]))
    FR_ss = np.dot(x, flux_to_zero_vector)
    
    assert np.abs(FR_ss - 1.47243297098) < 1e-10 
    
def test_flux_ex_inh():
    
    # Flux example 2:
    v_min = -.02
    v_max = .02
    tau=.02
    w = .005
    dv_n = 500
    dv = .005/dv_n
    v = np.arange(v_min, v_max+dv, dv)
    
    A = util.leak_matrix(v, tau)
    flux_to_zero_vector = np.zeros_like(A.sum(axis=0))
    
    flux_to_zero_vector_tmp, A_tmp = util.flux_matrix(v, w, 100)
    A += A_tmp    
    flux_to_zero_vector += flux_to_zero_vector_tmp
        
    flux_to_zero_vector_tmp, A_tmp = util.flux_matrix(v, -w, 100)
    A += A_tmp
    flux_to_zero_vector += flux_to_zero_vector_tmp 
    
    x = spla.solve(A+np.ones_like(A), np.ones_like(v[:-1]))
    FR_ss = np.dot(x, flux_to_zero_vector)
    
    assert np.abs(FR_ss - .899715510935) < 1e-10 

def test_leak_matrix():
    
    # Leak example 1:
    v_min = 0
    v_max = .02
    tau = .02
    dv_n = 1    
    dv = .005/dv_n
    v = np.arange(v_min, v_max+dv, dv)
    L = util.leak_matrix(v, tau)
    L_true = np.array([[   0.,  100.,    0.,    0.],
                       [   0., -100.,  150.,    0.],
                       [   0.,    0., -150.,  200.],
                       [   0.,    0.,    0., -200.]])
    
    np.testing.assert_array_almost_equal_nulp(L, L_true)
    
    # Leak example 2:
    v = [-.02, -.015, -.01, -.005, 0, .005, .01, .015, .02]
    L = util.leak_matrix(v, tau)
    L_true = np.array([[-200.,    0.,    0.,    0.,    0.,    0.,    0.,    0.],
                       [ 200., -150.,    0.,    0.,    0.,    0.,    0.,    0.],
                       [   0.,  150., -100.,    0.,    0.,    0.,    0.,    0.],
                       [   0.,    0.,  100.,    0.,    0.,    0.,    0.,    0.],
                       [   0.,    0.,    0.,    0.,    0.,  100.,    0.,    0.],
                       [   0.,    0.,    0.,    0.,    0., -100.,  150.,    0.],
                       [   0.,    0.,    0.,    0.,    0.,    0., -150.,  200.],
                       [   0.,    0.,    0.,    0.,    0.,    0.,    0., -200.]])
    
    np.testing.assert_array_almost_equal_nulp(L, L_true)
    
def test_fraction_overlap():
    assert util.fraction_overlap(0, 1, .5, 1.5) == .5
    assert util.fraction_overlap(0, 1, 2, 3) == 0
    assert util.fraction_overlap(0, 1, .5, .7) == .19999999999999996
    assert util.fraction_overlap(0, 1, -.5, 1.5) == 1.

if __name__ == "__main__":      # pragma: no cover
    test_get_zero_bin_list()    # pragma: no cover
    test_leak_matrix()          # pragma: no cover
    test_flux_ex_inh()          # pragma: no cover
    test_flux_ex_inh_border()   # pragma: no cover
    test_flux_ex()              # pragma: no cover
    test_fraction_overlap()     # pragma: no cover
