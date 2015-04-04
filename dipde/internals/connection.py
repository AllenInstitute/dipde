"""Module containing Connection class, connections between source and target populations."""

import numpy as np
from dipde.internals import utilities as util
from dipde.internals import ConnectionDistribution

class Connection(object):
    '''Class that connects dipde source population to dipde target population.

    The connection class handles all of the details of propogating connection
    information between a source population (dipde ExtermalPopulation or
    InternalPopulation) and a target population (dipde InternalPopulation).
    Handles delay information via a delay queue that is rolled on each timestep,
    and reuses connection information by using a ConnectionDistribution object
    with a specific signature to avoid duplication among identical connections.

     Attributes:
         source: source population (InternalPopulation or ExternalPopulation

         target: target population (InternalPopulation)

         nsyn: in-degree of connectivity (int)

         weights: weights defining synaptic distribution (np.ndarray)

         probs: probabilities corresponding to weights (np.ndarray)

         delay: transmission delay (float)

         metadata: connection metadata, all other kwargs
    '''

    def __init__(self,
                 source,
                 target,
                 nsyn,
                 **kwargs):

        self.source = source
        self.target = target
        self.nsyn = nsyn
        self.weights = kwargs.get('weights', None)
        self.probs = kwargs.get('probs', None)
        self.delay = float(kwargs.get('delay', 0))
        self.metadata = kwargs

        if self.weights != None or self.probs != None:
            assert len(self.weights) == len(self.probs)
        else:
            self.weights, self.probs = util.descretize(kwargs.get('distribution', None),
                                                       kwargs.get('N', None),
                                                       scale=kwargs.get('scale', None))
        assert np.abs(self.probs).sum() == 1

        # Defined at runtime:
        self.delay_queue = None
        self.delay_ind = None
        self.simulation = None

    def initialize(self):
        self.initialize_delay_queue()
        self.initialize_connection_distribution() 

    def initialize_connection_distribution(self):
        """Create connection distribution, if necessary.

        If the signature of this connection is already registered to the
        simulation-level connection distribution collection, it is associated
        with self.  If not, it adds the connection distribution to the
        collection, and associates it with self.
        """

        conn_dist = ConnectionDistribution(self.target.edges, self.weights, self.probs)
        conn_dist.simulation = self.simulation
        self.simulation.connection_distribution_collection.add_connection_distribution(conn_dist)
        self.connection_distribution = self.simulation.connection_distribution_collection[conn_dist.signature]

    def initialize_delay_queue(self):
        """Initialiaze a delay queue for the connection.

        The delay attribute of the connection defines the transmission delay of
        the signal from the souce to the target.  Firing rate values from the
        source population are held in a queue, discretized by the timestep, that
        is rolled over once per timestep.  if source is an ExternalPopulation,
        the queue is initialized to the firing rate at t=0; if the source is an
        InternalPopulation, the queue is initialized to zero.
        """

        # Set up delay queue:
        self.delay_ind = int(np.round(self.delay/self.simulation.dt))
        if self.source.type == 'internal':
            self.delay_queue = np.core.numeric.ones(self.delay_ind+1)*self.source.curr_firing_rate
        elif self.source.type == 'external':
            self.delay_queue = np.core.numeric.zeros(self.delay_ind+1)
            for i in range(len(self.delay_queue)):
                self.delay_queue[i] = self.source.firing_rate(self.simulation.t - self.simulation.dt*i)
                self.delay_queue = self.delay_queue[::-1]
        else:
            raise Exception('Unrecognized source type: "%s"' % self.source.type)    # pragma: no cover

    def update(self):
        """Update Connection,  called once per timestep."""

        self.delay_queue[0] = self.source.curr_firing_rate
        self.delay_queue = np.core.numeric.roll(self.delay_queue, -1)

    @property
    def curr_delayed_firing_rate(self):
        """Current firing rate of the source (float).

        Property that accesses the firing rate at the top of the delay queue,
        from the source population
        """
        
        try:

            return self.delay_queue[0]
        except:
            self.initialize_delay_queue()
            return self.delay_queue[0]
            
