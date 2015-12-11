import numpy as np 
from dipde.internals.internalpopulation import InternalPopulation
from dipde.internals.externalpopulation import ExternalPopulation
from dipde.internals.network import Simulation
from dipde.internals.connection import Connection as Connection
import scipy.stats as sps
from dipde.interfaces.zmq import RequestFiringRate, ReplyServerThread
from dipde.interfaces.zmq import context as zmq_context
import time

basic_steady_state = 5.110935325325733

def test_basic():
    singlepop(basic_steady_state)
    
def test_tau_normal():
    mu = .02
    sigma = 0.004
    a = 0
    b = np.inf
    tau_m_dist = sps.truncnorm(float(a - mu) / sigma, float(b - mu)/sigma, loc=mu, scale=sigma)
    singlepop(4.4905752835535582, tau_m=(tau_m_dist,50))

def test_p0():
    p0 = sps.norm(0.01,.001)
    singlepop(5.4319721344676637, p0=p0)
    
def test_weight():
    weights = sps.norm(0.005,.001)
    singlepop(5.7051134618017816, weights=weights)
    
def test_drive():
    bgfr = lambda t: 100
    singlepop(basic_steady_state, bgfr=bgfr)
    
def test_zmq_drive_bind_server():
    
    test_port = 5555

    try:
        # Start reply server:
        reply_server_thread = ReplyServerThread(test_port, lambda t: 100)
        reply_server_thread.start()
    
        # Run test:
        singlepop(basic_steady_state, bgfr=RequestFiringRate(test_port))

    finally:
        import zmq
        socket = zmq_context.socket(zmq.REQ)
        socket.connect("tcp://localhost:%s" % test_port)
        socket.send('SHUTDOWN')
        message = socket.recv()
        assert message == 'DOWN'
        time.sleep(.1)
        assert reply_server_thread.is_alive() == False    

def singlepop(steady_state, tau_m=.02, p0=((0.,),(1.,)), weights={'distribution':'delta', 'weight':.005}, bgfr=100):
    
    # Settings:
    t0 = 0.
    dt = .001
    dv = .001
    v_min = -.01
    v_max = .02
    tf = .1
    
    # Create simulation:
    b1 = ExternalPopulation(bgfr)
    i1 = InternalPopulation(v_min=v_min, tau_m=tau_m, v_max=v_max, dv=dv, update_method='exact', p0=p0)
    b1_i1 = Connection(b1, i1, 1, weights=weights)
    simulation = Simulation([b1, i1], [b1_i1])
    simulation.run(dt=dt, tf=tf, t0=t0)

    i1.plot_probability_distribution()
    i1.plot()
    assert i1.n_edges == i1.n_bins+1 

    # Test steady-state:    
    np.testing.assert_almost_equal(i1.get_firing_rate(.05), steady_state, 12)

    
if __name__ == "__main__":          # pragma: no cover 
    test_basic()                    # pragma: no cover
    test_tau_normal()               # pragma: no cover
    test_p0()                       # pragma: no cover
#     test_weight()                   # pragma: no cover
#     test_drive()                    # pragma: no cover
#     test_zmq_drive_bind_server()    # pragma: no cover

     