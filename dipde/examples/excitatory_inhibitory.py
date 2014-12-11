import time
import pylab as pl
import numpy as np 
from dipde.internals.internalpopulation import InternalPopulation
from dipde.internals.externalpopulation import ExternalPopulation
from dipde.internals.network import Network
from dipde.internals.simulation import Simulation
from dipde.internals.connection import Connection as Connection

np.set_printoptions(suppress=True)

def get_simulation(dt=.001, dv=.001, tf=.2, verbose=False, update_method='exact', approx_order=None, tol=1e-8):
    '''
    .. function:: foo(x)
              foo(y, z)
   :module: some.module.name

   Return a line of text input from the user.
    '''


    # Create simulation:
    b1 = ExternalPopulation('100')
    i1 = InternalPopulation(v_min=-.02, v_max=.02, dv=dv, update_method=update_method, approx_order=approx_order, tol=tol)
    b1_i1 = Connection(b1, i1, 1, weights=[.005], probs=[1.], delay=0.0)
    b1_i1_2 = Connection(b1, i1, 1, weights=[-.005], probs=[1.], delay=0.0)
    network = Network(population_list=[b1, i1], connection_list = [b1_i1, b1_i1_2])
    simulation = Simulation(dt=dt, tf=tf, network=network, verbose=verbose)

    return simulation


if __name__ == "__main__":

    # Settings:
    dt = .0001
    dv = .0001
    tf = .2
    verbose = False
    
    update_method = 'approx'
    approx_order = None
    tol = 1e-14
    simulation = get_simulation(dt=dt, tf=tf, dv=dv, verbose=verbose, update_method=update_method, approx_order=approx_order, tol=tol)
    t0 = time.time()
    simulation.run()
    i1 = simulation.network.population_list[1]
    print simulation.run_time, i1.firing_rate_record[-1]
    pl.plot(i1.t_record, i1.firing_rate_record)
    pl.xlim([0,tf])
#     i1.plot_probability_distribution()
#     pl.xlim([-.02,.02])

    pl.show()
