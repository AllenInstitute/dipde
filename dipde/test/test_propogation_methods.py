import numpy as np 
from dipde.internals.internalpopulation import InternalPopulation
from dipde.internals.externalpopulation import ExternalPopulation
from dipde.internals.network import Network
from dipde.internals.simulation import Simulation
from dipde.internals.connection import Connection as Connection

def get_singlepop_simulation(dt=.001, dv=.001, tf=.2, verbose=False, update_method='exact', approx_order=None, tol=1e-8):

    # Create simulation:
    b1 = ExternalPopulation('100')
    i1 = InternalPopulation(v_min=0, v_max=.02, dv=dv, update_method=update_method, approx_order=approx_order, tol=tol)
    b1_i1 = Connection(b1, i1, 1, weights=[.005], probs=[1.], delay=0.0)
    network = Network(population_list=[b1, i1], connection_list = [b1_i1])
    simulation = Simulation(dt=dt, tf=tf, network=network, verbose=verbose)

    return simulation

def test_singlepop_approx_order_1():

    # Settings:
    dt = .001
    dv = .001
    tf = .02
    verbose = False
    
    update_method = 'approx'
    approx_order = 1
    simulation = get_singlepop_simulation(dt=dt, tf=tf, dv=dv, verbose=verbose, update_method=update_method, approx_order=approx_order)
    simulation.run()
    i1 = simulation.network.population_list[1]    
    
    true_ans = np.array([0, 0.27175000000000016, 1.1897988210156254, 2.4418818034709062, 3.395794139471406])
    np.testing.assert_almost_equal(i1.firing_rate_record[0::5], true_ans, 12)

def test_singlepop_approx_order_2():



    # Settings:
    dt = .001
    dv = .001
    tf = .02
    verbose = False
    
    update_method = 'approx'
    approx_order = 2
    simulation = get_singlepop_simulation(dt=dt, tf=tf, dv=dv, verbose=verbose, update_method=update_method, approx_order=approx_order)
    simulation.run()
    i1 = simulation.network.population_list[1]
    
    
    true_ans = np.array([0, 0.30953807350830093, 1.2472786291767501, 2.3696878664430523, 3.2896140506543716])
    np.testing.assert_almost_equal(i1.firing_rate_record[0::5], true_ans, 12)
    


def test_singlepop_tol():

    # Settings:
    dt = .001
    dv = .001
    tf = .02
    verbose = False
    
    update_method = 'approx'
    tol = 1e-5
    simulation = get_singlepop_simulation(dt=dt, tf=tf, dv=dv, verbose=verbose, update_method=update_method, tol=tol)
    simulation.run()
    i1 = simulation.network.population_list[1]
    
    true_ans = np.array([0, 0.31558861561894364, 1.2360741904265171, 2.366683926394197, 3.2901664317642489])
    np.testing.assert_almost_equal(i1.firing_rate_record[0::5], true_ans, 12)
    

