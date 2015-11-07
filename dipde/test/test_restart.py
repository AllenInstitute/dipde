import numpy as np
import json
from dipde.internals.internalpopulation import InternalPopulation
from dipde.internals.externalpopulation import ExternalPopulation
from dipde.internals.simulation import Simulation
from dipde.internals.connection import Connection as Connection

def test_restart():


    b1 = ExternalPopulation('100', record=True)
    i1 = InternalPopulation(v_min=0, v_max=.02, dv=.001)
    simulation = Simulation([b1, i1], [Connection(b1, i1, 1, weights=.005, delay=0.0)], verbose=False)
    simulation.run(dt=.001, tf=.01, t0=0)
    
    b2 = ExternalPopulation('100', record=True)
    i2 = InternalPopulation(**json.loads(i1.to_json()))
    simulation2 = Simulation([b2, i2], [Connection(b2, i2, 1, weights=.005, delay=0.0)], verbose=False)
    simulation2.run(dt=.001, tf=.02, t0=.01)
    
    b3 = ExternalPopulation('100', record=True)
    i3 = InternalPopulation(v_min=0, v_max=.02, dv=.001)
    simulation3 = Simulation([b3, i3], [Connection(b3, i3, 1, weights=.005, delay=0.0)], verbose=False)
    simulation3.run(dt=.001, tf=.02, t0=0)

    for y1, y2 in zip(i1.firing_rate_record+i2.firing_rate_record[1:], i3.firing_rate_record):
        np.testing.assert_almost_equal(y1, y2, 8) 

    import StringIO
    i3.to_json(StringIO.StringIO())
    

if __name__ == "__main__":                         # pragma: no cover
    test_restart()                         # pragma: no cover