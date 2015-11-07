import numpy as np 
from dipde.internals.internalpopulation import InternalPopulation
from dipde.internals.externalpopulation import ExternalPopulation
from dipde.internals.simulation import Simulation
from dipde.internals.connection import Connection as Connection
import scipy.stats as sps

def test_basic():
    singlepop(5.110935325325733)
    
def test_tau_normal():
    mu = .02
    sigma = 0.004
    a = 0
    b = np.inf
    tau_m_dist = sps.truncnorm(float(a - mu) / sigma, float(b - mu)/sigma, loc=mu, scale=sigma)
    singlepop(4.4905752835535582, tau_m=(tau_m_dist,50))

def test_p0():
    p0 = sps.norm(0.01,.001)
    singlepop(5.4339926624266566, p0=p0)
    
def test_weight():
    weights = sps.norm(0.005,.001)
    singlepop(5.7051134618017816, weights=weights)
    
def test_drive():
    bgfr = lambda t: 100
    singlepop(5.110935325325733, bgfr=bgfr)

def singlepop(steady_state, tau_m=.02, p0=((0.,),(1.,)), weights={'distribution':'delta', 'weight':.005}, bgfr=100):
    
    # Settings:
    t0 = 0.
    dt = .001
    dv = .001
    v_min = -.01
    v_max = .02
    tf = .1
    verbose = False
    
    # Create simulation:
    b1 = ExternalPopulation(bgfr)
    i1 = InternalPopulation(v_min=v_min, tau_m=tau_m, v_max=v_max, dv=dv, update_method='exact', p0=p0)
    b1_i1 = Connection(b1, i1, 1, weights=weights)
    simulation = Simulation([b1, i1], [b1_i1], verbose=verbose)
    simulation.run(dt=dt, tf=tf, t0=t0)

    i1.plot_probability_distribution()
    i1.plot()
    assert i1.n_edges == i1.n_bins+1 

    # Test steady-state:    
    np.testing.assert_almost_equal(i1.get_firing_rate(.05), steady_state, 12)

    
if __name__ == "__main__":      # pragma: no cover 
    test_basic()                # pragma: no cover
    test_tau_normal()           # pragma: no cover
    test_p0()                   # pragma: no cover
    test_weight()               # pragma: no cover
    test_drive()                # pragma: no cover

# import numpy as np 
# from dipde.internals.internalpopulation import InternalPopulation
# from dipde.internals.externalpopulation import ExternalPopulation
# from dipde.internals.simulation import Simulation
# from dipde.internals.connection import Connection as Connection
# 
# def xtest_singlepop():
#     
#     # Settings:
#     t0 = 0.
#     dt = .001
#     dv = .001
#     v_min = -.01
#     v_max = .02
#     tf = .2
#     verbose = False
#     
#     # Create simulation:
#     b1 = ExternalPopulation(50)
#     b2 = ExternalPopulation(lambda t:50)
#     i1 = InternalPopulation(v_min=v_min, v_max=v_max, dv=dv, update_method='exact')
#     b1_i1 = Connection(b1, i1, 1, weights={'distribution':'delta', 'weight':.005})
#     b2_i1 = Connection(b2, i1, 1, weights=.005)
#     simulation = Simulation([b1, b2, i1], [b1_i1, b2_i1], verbose=verbose)
#     simulation.run(dt=dt, tf=tf, t0=t0)
#     
#     np.testing.assert_almost_equal(i1.t_record[-1], .2, 15)
#     np.testing.assert_almost_equal(i1.firing_rate_record[-1], 5.3550004610797552, 12)
#     assert i1.n_bins == (v_max - v_min)/dv
#     assert i1.n_edges - 1 == i1.n_bins
#     assert len(simulation.population_list) == 3
#     

#     true_ans = 5.3520134135165973
#     np.testing.assert_almost_equal(i1.get_firing_rate(.1), true_ans, 12)
# 
# if __name__ == "__main__":      # pragma: no cover 

# 
#     