import time
import zmq
import threading

context = zmq.Context()

class PublishCallback(object):
    
    def __init__(self, port, topic, message_callback):
        
        self.port = port
        self.topic = topic
        self.message_callback = message_callback        
        self.socket = context.socket(zmq.PUB)
        
    def __call__(self, obj):
        message_to_send = list(self.message_callback(obj))
        message_to_send.insert(0,"%s" % self.topic)
        self.socket.send_multipart(map(str, message_to_send))
        
class PublishCallbackConnect(PublishCallback):
    
    def __init__(self, port, topic, message_callback):
        super(self.__class__, self).__init__(port, topic, message_callback)
        self.socket.connect("tcp://localhost:%s" % self.port)
        
class PublishCallbackBind(PublishCallback):
    
    def __init__(self, port, topic, message_callback):
        super(self.__class__, self).__init__(port, topic, message_callback)
        self.socket.bind("tcp://*:%s" % self.port)

class RequestFiringRate(object):
    
    def __init__(self, port):
        
        self.port = port        
        self.socket = context.socket(zmq.REQ)
        self.socket.connect("tcp://localhost:%s" % port)
        
    def __call__(self, t):
        self.socket.send('%s' % t)
        message = self.socket.recv_multipart()
        return float(message[0])
    
class ReplyFiringRateServer(object):
    
    def __init__(self, port, reply_function):
        self.port = port
        self.reply_function = reply_function
        self.socket = context.socket(zmq.REP)
        self.socket.bind("tcp://*:%s" % self.port)
        
    def run(self):
        
        while True:
            message = self.socket.recv()
            if message == 'SHUTDOWN':
                break
            requested_t = float(message)
            self.socket.send_multipart([b"%s" % self.reply_function(requested_t)])
        self.socket.send('DOWN')

class ReplyServerThread(threading.Thread):
    def __init__(self, port, reply_function):
        super(self.__class__, self).__init__()
        self.daemon = True
        self.port = port
        self.reply_function = reply_function
    
    def run(self):
        self.server = ReplyFiringRateServer(self.port, self.reply_function)
        self.server.run()

def gid_firing_rate_callback(self):
#     time.sleep(.05)
    return self.gid, self.curr_firing_rate

def simulation_callback(self):
    time.sleep(.05)
    return [self.t]

if __name__ == "__main__":
    
    import matplotlib.pyplot as plt
    from dipde.internals.internalpopulation import InternalPopulation
    from dipde.internals.externalpopulation import ExternalPopulation
    from dipde.internals.network import Network
    from dipde.internals.connection import Connection as Connection
    
    def get_simulation(dv=.001, verbose=False, update_method='exact', approx_order=None, tol=1e-8):
    
        # Create simulation:
        f = RequestFiringRateFunction(5555)
        b1 = ExternalPopulation(f, record=True, name='b1')
        i1 = InternalPopulation(v_min=0, v_max=.02, dv=dv, update_method=update_method, approx_order=approx_order, tol=tol)
        b1_i1 = Connection(b1, i1, 1, weights=.005, delay=0.0)
        simulation = Network([b1, i1], [b1_i1], verbose=verbose)
    
        return simulation
    
    def example(show=False, save=False, verbose=False):
    
        # Settings:
        t0 = 0.
        dt = .0001
        dv = .0001
        tf = .1
        update_method = 'approx'
        approx_order = 1
        tol = 1e-14
        
        # Run simulation:
        simulation = get_simulation(dv=dv, verbose=verbose, update_method=update_method, approx_order=approx_order, tol=tol)
        simulation.run(dt=dt, tf=tf, t0=t0)
        
        # Visualize:
        i1 = simulation.population_list[1]
        fig, ax = plt.subplots(figsize=(3,3))
        i1.plot(ax=ax)
        plt.xlim([0,tf])
        plt.ylim(ymin=0)
        plt.xlabel('Time (s)')
        plt.ylabel('Firing Rate (Hz)')
        fig.tight_layout()
        if save == True: plt.savefig('./singlepop.png')
        if show == True: plt.show()
            
        return i1.t_record, i1.firing_rate_record
        
    example(verbose=True, show=True)