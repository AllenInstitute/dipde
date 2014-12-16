import numpy as np 
from dipde.internals.internalpopulation import InternalPopulation
from dipde.internals.externalpopulation import ExternalPopulation
from dipde.internals.network import Network
from dipde.internals.simulation import Simulation
from dipde.internals.connection import Connection as Connection
import scipy.stats as sps

def test_singlepop():
    
    # Settings:
    dt = .001
    tf = .2
    verbose = False
    
    # Create simulation:
    b1 = ExternalPopulation(50)
    b2 = ExternalPopulation(50)
    i1 = InternalPopulation(v_min=0, v_max=.02, dv=.001,update_method='exact')
    b1_i1 = Connection(b1, i1, 1, weights=[.005], probs=[1.])
    b2_i1 = Connection(b2, i1, 1, weights=[.005], probs=[1.])
    network = Network(population_list=[b1, b2, i1], connection_list = [b1_i1, b2_i1])
    simulation = Simulation(dt=dt, tf=tf, network=network, verbose=verbose)
    simulation.run()
    
    np.testing.assert_almost_equal(i1.t_record[-1], .2, 15)
    np.testing.assert_almost_equal(i1.firing_rate_record[-1], 5.3915680531750283, 12)
    
def test_singlepop_all_values():
    
    # Settings:
    dt = .01
    tf = .05
    verbose = False
    
    # Create simulation:
    b1 = ExternalPopulation(50)
    b2 = ExternalPopulation(50)
    i1 = InternalPopulation(v_min=0, v_max=.02, dv=.001, update_method='exact')
    b1_i1 = Connection(b1, i1, 1, weights=[.005], probs=[1.])
    b2_i1 = Connection(b2, i1, 1, weights=[.005], probs=[1.])
    network = Network(population_list=[b1, b2, i1], connection_list = [b1_i1, b2_i1])
    simulation = Simulation(dt=dt, tf=tf, network=network, verbose=verbose)
    simulation.run()
    
    true_ans = np.array([0, 1.2360691367893266, 3.290164962389543, 4.4497165056100059, 4.990876549793831, 5.224933789156613])
    np.testing.assert_almost_equal(i1.firing_rate_record, true_ans, 12)

def test_singlepop_exponential():
    
    # Settings:
    dt = .0001
    dv = .0001
    tf = .02
    verbose = False
    update_method = 'approx'
    approx_order = None
    tol = 1e-14
    
    # Create simulation:
    b1 = ExternalPopulation(1000)
    i1 = InternalPopulation(v_min=0, v_max=.02, dv=dv, update_method=update_method, approx_order=approx_order, tol=tol)
    b1_i1 = Connection(b1, i1, 1, delay=0.0, distribution=sps.expon, N=21, scale=.002)
    network = Network(population_list=[b1, i1], connection_list = [b1_i1])
    simulation = Simulation(dt=dt, tf=tf, network=network, verbose=verbose)
    simulation.run()
    i1 = simulation.network.population_list[1]
    result = i1.firing_rate_record[::20]
    
    true_ans = np.array([0, 4.1796691172714144, 19.463588076191844, 39.841246135878954, 57.006804676460995, 67.335260075864284, 71.555153034931635, 72.116772009344487, 71.246053874456649, 70.249266606940949, 69.611261205996058])
    np.testing.assert_almost_equal(result, true_ans, 12)
    
def test_singlepop_excitatory_inhibitory():
    
    # Settings:
    dt = .0001
    dv = .0001
    tf = .05
    verbose = False    
    update_method = 'approx'
    approx_order = None
    tol = 1e-14

    # Create simulation:
    b1 = ExternalPopulation('100')
    i1 = InternalPopulation(v_min=-.02, v_max=.02, dv=dv, update_method=update_method, approx_order=approx_order, tol=tol)
    b1_i1 = Connection(b1, i1, 1, weights=[.005], probs=[1.], delay=0.0)
    b1_i1_2 = Connection(b1, i1, 1, weights=[-.005], probs=[1.], delay=0.0)
    network = Network(population_list=[b1, i1], connection_list = [b1_i1, b1_i1_2])
    simulation = Simulation(dt=dt, tf=tf, network=network, verbose=verbose)
    simulation.run()
    result = i1.firing_rate_record[::100]

    true_ans = np.array([0, 0.50246029916769708, 0.80837853121529257, 0.89685375300046122, 0.91370430022836946, 0.9141404810533561])
    np.testing.assert_almost_equal(result, true_ans, 12)

    