import numpy as np
import json
from dipde.internals.internalpopulation import InternalPopulation
from dipde.internals.externalpopulation import ExternalPopulation
from dipde.internals.network import Network
from dipde.internals.connection import Connection as Connection
import StringIO

def test_restart_interal():

    # Run part-way and serialize:
    b1 = ExternalPopulation('100', record=True)
    i1 = InternalPopulation(v_min=0, v_max=.02, dv=.001)
    b1_i1 = Connection(b1, i1, 1, weights=.005, delays=0.0)
    simulation = Network([b1, i1], [b1_i1])
    simulation.run(dt=.001, tf=.01, t0=0)
    i1_str = i1.to_json()
    b1_str = b1.to_json()
    
    # Rehydrate and continue run:
    b2 = ExternalPopulation(**json.loads(b1_str))
    i2 = InternalPopulation(**json.loads(i1_str))
    simulation2 = Network([b2, i2], [Connection(b2, i2, 1, weights=.005, delays=0.0)])
    simulation2.run(dt=.001, tf=.02, t0=.01)
    
    # Run straight through, for comparison:
    b3 = ExternalPopulation('100', record=True)
    i3 = InternalPopulation(v_min=0, v_max=.02, dv=.001)
    simulation3 = Network([b3, i3], [Connection(b3, i3, 1, weights=.005, delays=0.0)])
    simulation3.run(dt=.001, tf=.02, t0=0)

    # Test:
    for y1, y2 in zip(i1.firing_rate_record, i3.firing_rate_record):
        np.testing.assert_almost_equal(y1, y2, 8) 

    b3.to_json(StringIO.StringIO())
    i3.to_json(StringIO.StringIO())
    b1_i1.to_json(StringIO.StringIO())
    
def test_marshal_connection():
    c = Connection(0, 1, 1, weights=.005, delays=.005)
    c.to_json()
    
def test_marshal_simulation():
    
    from dipde.examples.excitatory_inhibitory import get_simulation
    
    
    # Create simulation:
    simulation = get_simulation()
    simulation_2 = simulation.copy()
    
    # Run original simulation: 
    simulation.run(dt=.001, tf=.02, t0=0)

    # Run copy half way, round trip, and then finish:
    simulation_2.run(dt=.001, tf=.01, t0=0)
    s_mid = simulation_2.to_json()
    simulation_3 = Network(**json.loads(s_mid))
    simulation_3.run(tf=.02)

    # Compare:
    y1 = simulation.population_list[1].firing_rate_record
    y2 = simulation_3.population_list[1].firing_rate_record
    assert len(y1) == len(y2)
    for y1i, y2i in zip(y1, y2):
        np.testing.assert_almost_equal(y1i, y2i, 12)
        
    simulation.to_json(StringIO.StringIO())
    
    
if __name__ == "__main__":                         # pragma: no cover
    test_restart_interal()                         # pragma: no cover
    test_marshal_simulation()                         # pragma: no cover
    test_marshal_connection()                 # pragma: no cover