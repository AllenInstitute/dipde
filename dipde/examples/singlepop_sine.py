import pylab as pl 
from dipde.internals.internalpopulation import InternalPopulation
from dipde.internals.externalpopulation import ExternalPopulation
from dipde.internals.network import Network
from dipde.internals.simulation import Simulation
from dipde.internals.connection import Connection as Connection

def get_simulation(dt=.001, dv=.001, tf=.2, verbose=False, update_method='exact', approx_order=None, tol=1e-8):

    # Create simulation:
    b1 = ExternalPopulation('500*abs(sin(20*t))')
    i1 = InternalPopulation(v_min=0, v_max=.02, dv=dv, update_method=update_method, approx_order=approx_order, tol=tol)
    b1_i1 = Connection(b1, i1, 1, weights=[.005], probs=[1.], delay=0.0)
    network = Network(population_list=[b1, i1], connection_list = [b1_i1])
    simulation = Simulation(dt=dt, tf=tf, network=network, verbose=verbose)

    return simulation


def example(show=True):

    # Settings:
    dt = .0001
    dv = .0001
    tf = .2
    verbose = False
    
    update_method = 'approx'
    approx_order = None
    tol = 1e-14
    simulation = get_simulation(dt=dt, tf=tf, dv=dv, verbose=verbose, update_method=update_method, approx_order=approx_order, tol=tol)
    simulation.run()
    i1 = simulation.network.population_list[1]
    pl.plot(i1.t_record, i1.firing_rate_record)
    pl.xlim([0,tf])

    if show == True: pl.show()
    
    return i1.t_record, i1.firing_rate_record

if __name__ == "__main__": example()        # pragma: no cover