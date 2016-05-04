import numpy as np 
from dipde.internals.internalpopulation import InternalPopulation
from dipde.internals.externalpopulation import ExternalPopulation
from dipde.internals.network import Network
from dipde.internals.connection import Connection as Connection


def test_delay_singlepop():

    # Settings:
    t0 = 0.
    dt = .001
    tf = .005
    
    # Create simulation:
    b1 = ExternalPopulation('Heaviside(t)*100')
    i1 = InternalPopulation(v_min=0, v_max=.02, dv=.001, update_method='exact')
    b1_i1 = Connection(b1, i1, 1, weights=.005, delays=2*dt, delay_queue=[0,0,50])
    
#     # DEBUG:
#     b1_i1 = Connection(b1, i1, 1, weights=.005, delays=((0,.001, .002),(0,0,1.)), delay_queue=[0,0,50])
    
    
    simulation = Network([b1, i1], [b1_i1])
    simulation.run(dt=dt, tf=tf, t0=t0)
    
    true_ans = np.array([0, 0.0, 0.0, 0.00066516669656511084, 0.025842290308637855, 0.08117342489138904])
    np.testing.assert_almost_equal(i1.firing_rate_record, true_ans, 12)

def test_delay_doublepop():

    # Settings:
    t0 = 0.
    dt = .001
    tf = .010
    
    # Create populations:
    b1 = ExternalPopulation(50)
    i1 = InternalPopulation(v_min=0, v_max=.02, dv=.001, update_method='exact')
    i2 = InternalPopulation(v_min=0, v_max=.02, dv=.001, update_method='exact')
    
    # Create connections:
    b1_i1 = Connection(b1, i1, 2, weights=.005)
    i1_i2 = Connection(i1, i2, 20, weights=.005, delays=2*dt)    
    
    # Create and run simulation:
    simulation = Network([b1, i1, i2], [b1_i1, i1_i2])
    simulation.run(dt=dt, tf=tf, t0=t0)
    
    true_ans = np.array([0, 0.0, 0.0, 0.0, 1.9089656152757652e-13, 1.9787511418980406e-10, 9.5007650186649266e-09, 1.3334881090883857e-07, 1.0103767575651715e-06, 5.3604521936092067e-06, 2.2383604753409621e-05])
    np.testing.assert_almost_equal(i2.firing_rate_record, true_ans, 12)

def test_delay_distribution():

    # Settings:
    t0 = 0.
    dt = .001
    tf = .1
    
    # Create populations:
    b1 = ExternalPopulation('100*Heaviside(t)')
    i1 = InternalPopulation(v_min=0, v_max=.02, dv=.001, update_method='exact')
    
    # Create connections:
    b1_i1 = Connection(b1, i1, 1, weights=.005, delays=((0,.05),(.5,.5)))
    
    # Create and run simulation:
    simulation = Network([b1, i1], [b1_i1])
    simulation.run(dt=dt, tf=tf, t0=t0)
    
    true_ans = np.array([0.38560647739319964, 5.229266329159536])
    np.testing.assert_almost_equal(np.array(i1.get_firing_rate([.04, .09])), true_ans, 8)

if __name__ == "__main__":                         # pragma: no cover
    test_delay_singlepop()                         # pragma: no cover
    test_delay_doublepop()                         # pragma: no cover    
    test_delay_distribution()                      # pragma: no cover

