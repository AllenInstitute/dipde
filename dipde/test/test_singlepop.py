import numpy as np 
from dipde.internals.internalpopulation import InternalPopulation
from dipde.internals.externalpopulation import ExternalPopulation
from dipde.internals.simulation import Simulation
from dipde.internals.connection import Connection as Connection

def test_singlepop():
    
    # Settings:
    t0 = 0.
    dt = .001
    dv = .001
    v_min = -.01
    v_max = .02
    tf = .2
    verbose = False
    
    # Create simulation:
    b1 = ExternalPopulation(50)
    b2 = ExternalPopulation(50)
    i1 = InternalPopulation(v_min=v_min, v_max=v_max, dv=dv, update_method='exact')
    b1_i1 = Connection(b1, i1, 1, weights=[.005], probs=[1.])
    b2_i1 = Connection(b2, i1, 1, weights=[.005], probs=[1.])
    simulation = Simulation([b1, b2, i1], [b1_i1, b2_i1], verbose=verbose)
    simulation.run(dt=dt, tf=tf, t0=t0)
    
    np.testing.assert_almost_equal(i1.t_record[-1], .2, 15)
    np.testing.assert_almost_equal(i1.firing_rate_record[-1], 5.3550005434746355, 12)
    assert i1.n_bins == (v_max - v_min)/dv
    assert i1.n_edges - 1 == i1.n_bins
    assert len(simulation.population_list) == 3
    
    i1.plot_probability_distribution()
    
if __name__ == "__main__":      # pragma: no cover 
    test_singlepop()            # pragma: no cover

    