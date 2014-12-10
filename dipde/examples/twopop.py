import pylab as pl
import numpy as np 
from dipde.internals.internalpopulation import InternalPopulation
from dipde.internals.externalpopulation import ExternalPopulation
from dipde.internals.network import Network
from dipde.internals.simulation import Simulation
from dipde.internals.connection import Connection as Connection

def get_simulation(dt=.001, dv=.001, tf=.2, verbose=False, update_method='exact', approx_order=None, tol=1e-8, delay=0):

    # Create populations:
    b1 = ExternalPopulation(50)
    i1 = InternalPopulation(v_min=0, v_max=.02, dv=.001)
    i2 = InternalPopulation(v_min=0, v_max=.02, dv=.001)
    
    # Create connections:
    b1_i1 = Connection(b1, i1, 2, weights=[.005])
    i1_i2 = Connection(i1, i2, 20, weights=[.005], delay=delay)
    
    # Create and run simulation:
    network = Network(population_list=[b1, i1, i2], connection_list = [b1_i1, i1_i2])
    simulation = Simulation(dt=dt, tf=tf, network=network, verbose=verbose)
    
    return simulation

if __name__ == "__main__":

    # Settings:
    dt = .001
    tf = .2
    verbose = False
    delay = 0
    
    simulation = get_simulation(dt=dt, tf=tf, verbose=verbose, delay=delay)
    simulation.run()
    
    # Plot results:
    i1 = simulation.network.population_list[1]
    i2 = simulation.network.population_list[2]
    pl.plot(i1.t_record, i1.firing_rate_record)
    pl.plot(i2.t_record, i2.firing_rate_record, 'g')
    print i2.firing_rate_record
    pl.show()
