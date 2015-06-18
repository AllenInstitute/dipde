"""Module containing Connection class, connections between source and target populations."""

# Copyright 2013 Allen Institute
# This file is part of dipde
# dipde is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# dipde is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with dipde.  If not, see <http://www.gnu.org/licenses/>.

import numpy as np
from dipde.internals import utilities as util
from dipde.internals import ConnectionDistribution

class Connection(object):
    '''Class that connects dipde source population to dipde target population.

    The Connection class handles all of the details of propogating connection
    information between a source population (dipde ExtermalPopulation or
    InternalPopulation) and a target population (dipde InternalPopulation).
    Handles delay information via a delay queue that is rolled on each timestep,
    and reuses connection information by using a ConnectionDistribution object
    with a specific signature to avoid duplication among identical connections.
    
    Parameters
    ----------
     source : InternalPopulation or ExternalPopulation
         Source population for connection.
     target : InternalPopulation
         Target population for connection.
     nsyn : int
         In-degree of connectivity from source to target.
     weights : list 
         Weights defining synaptic distribution (np.ndarray).
     probs : list (same length as weights, and sums to 1) 
         Probabilities corresponding to weights.
     delay: float (default=0) 
         Transmission delay (units: sec).
     metadata: Connection metadata, all other kwargs
    '''

    def __init__(self,
                 source,
                 target,
                 nsyn,
                 **kwargs):

        self.source = source
        self.target = target
        self.nsyn = nsyn
        self.weights = kwargs.pop('weights', None)
        self.probs = kwargs.pop('probs', None)
        self.delay = float(kwargs.pop('delay', 0))
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
        '''Initialize the connection at the beginning of a simulation.
        
        Calling this method: 
        
            1) Initializes a delay queue used to store values of inputs in a last-in-first-out rolling queue.
            
            2) Creates a connection_distribution object for the connection, if a suitable object is not already registered with the  simulation-level connection distribution collection.
        
        This method is called by the Simulation object (initialization method),
        but can also be called by a user when defining an alternative time
        stepping loop.
        '''
        
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
        from the source population.
        """
        
        try:

            return self.delay_queue[0]
        except:
            self.initialize_delay_queue()
            return self.delay_queue[0]
            
