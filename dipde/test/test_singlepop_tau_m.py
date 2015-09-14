import numpy as np 
from dipde.internals.internalpopulation import InternalPopulation
from dipde.internals.externalpopulation import ExternalPopulation
from dipde.internals.simulation import Simulation
from dipde.internals.connection import Connection as Connection
import scipy.stats as sps

def test_tau_constant():
    singlepop(5.3550005434746355)
    
def test_tau_normal():
    singlepop(4.9251936219023831, tau_m=(sps.norm(loc=.02, scale=0.004),50))

def singlepop(steady_state, tau_m=.02):
    
    # Settings:
    t0 = 0.
    dt = .001
    dv = .001
    v_min = -.01
    v_max = .02
    tf = .2
    verbose = False
    
    # Create simulation:
    b1 = ExternalPopulation(100)
    i1 = InternalPopulation(v_min=v_min, tau_m=tau_m, v_max=v_max, dv=dv, update_method='exact')
    b1_i1 = Connection(b1, i1, 1, weights=.005)
    simulation = Simulation([b1, i1], [b1_i1], verbose=verbose)
    simulation.run(dt=dt, tf=tf, t0=t0)

    # Test steady-state:    
    np.testing.assert_almost_equal(i1.firing_rate_record[-1], steady_state, 12)

    
if __name__ == "__main__":      # pragma: no cover 
    test_tau_constant()         # pragma: no cover
    test_tau_normal()           # pragma: no cover

    