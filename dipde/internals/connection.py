import numpy as np
from dipde.internals import utilities as util
from dipde.internals import ConnectionDistribution

class Connection(object):
    
    def __init__(self, source, target, nsyn, weights=None, probs=None, delay=0, distribution=None, N=None, scale=None, **kwargs):

        if weights != None or probs != None:
            assert len(weights) == len(probs)
        else:
            weights, probs = util.descretize(distribution, N, scale=scale)
        assert np.abs(probs).sum() == 1
        
        self.source = source
        self.target = target
        self.nsyn = nsyn
        self.weights = weights
        self.probs = probs
        self.delay = float(delay)
        self.metadata = kwargs

            
    def initialize_connection_distribution(self):

        cd = ConnectionDistribution(self.target.edges, self.weights, self.probs)
        cd.simulation = self.simulation
        self.simulation.connection_distribution_collection.add_connection_distribution(cd)
        self.connection_distribution = self.simulation.connection_distribution_collection.connection_distribution_dict[cd.signature]

    def initialize_delay_queue(self):

        # Set up delay queue:
        self.delay_ind = int(np.round(self.delay/self.simulation.dt))
        if self.source.type == 'internal':
            self.delay_queue = np.ones(self.delay_ind+1)*self.source.curr_firing_rate
        elif self.source.type == 'external':
            self.delay_queue = np.zeros(self.delay_ind+1)
            for ii in range(len(self.delay_queue)):
                self.delay_queue[ii] = self.source.firing_rate(self.simulation.t - self.simulation.dt*ii)
                self.delay_queue = self.delay_queue[::-1]
        else:
            raise Exception('Unrecognized source type: "%s"' % self.source.type)    # pragma: no cover
        
    def update_delay_queue(self):
        self.delay_queue[0] = self.source.curr_firing_rate
        self.delay_queue = np.roll(self.delay_queue, -1)
        
    @property
    def curr_delayed_firing_rate(self):
        return self.delay_queue[0]

#         print self.source.curr_firing_rate