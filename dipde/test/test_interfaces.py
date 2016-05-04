from dipde.internals.network import Network
from dipde.interfaces import PopulationInterface, ODE
from dipde.internals.connection import Connection as Connection
import sys
import os
import numpy as np

def test_general_interface():
    
    # Settings:
    t0 = 0.
    dt = .001
    tf = .01
    
    # Run simulation:
    b1 = ODE(lambda y, t:(100-t)/.1)
    i1 = PopulationInterface()
    b1_i1 = Connection(b1, i1, 1, weights=.005)
    
    
    
    network = Network([b1, i1], [b1_i1])
    network.run(dt, tf=tf, t0=t0)
    
    # Tests:
    final_firing_rate = 9.99949999997
    np.testing.assert_almost_equal(b1.curr_firing_rate, final_firing_rate, 10)
    np.testing.assert_almost_equal(i1.source_firing_rate_dict[0], final_firing_rate, 10)
    assert len(i1.source_connection_list) == 1
    assert i1.source_connection_list[0] == b1_i1 
    
if __name__ == "__main__":              # pragma: no cover
    test_general_interface()      # pragma: no cover
