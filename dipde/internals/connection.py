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
from dipde.internals.externalpopulation import ExternalPopulation
from dipde.internals.internalpopulation import InternalPopulation
import collections
import json

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
     weights : 
         Weights defining synaptic distribution.
     delay: float (default=0) 
         Transmission delay (units: sec).
     metadata: Connection metadata, all other kwargs
    '''

    def __init__(self,
                 source=None,
                 target=None,
                 nsyn=None,
                 delays=0,
                 weights=None,
                 delay_queue=None,
                 metadata={},
                 **kwargs):

        self.source_gid_or_population = source
        self.target_gid_or_population = target
        
        self.nsyn = nsyn
        self.synaptic_weight_distribution = util.discretize_if_needed(weights)
        self.weights, self.probs = self.synaptic_weight_distribution.xk, self.synaptic_weight_distribution.pk

        self.delay_distribution = util.discretize_if_needed(delays)
        self.delay_vals, self.delay_probs = self.delay_distribution.xk, self.delay_distribution.pk
        self.delay_queue_initial_condition = delay_queue

        util.check_metadata(metadata)
        self.metadata = metadata

        # Defined at runtime:
        self.delay_queue = None
        self.delay_ind = None
        self.simulation = None
        
        for key in kwargs.keys():
            assert key in ['class']

    @property
    def source(self):
        if isinstance(self.source_gid_or_population, int):
            if self.simulation is None:
                return None
            else:
                return self.simulation.gid_dict[self.source_gid_or_population]
        else: 
            return self.source_gid_or_population
        
    @property
    def target(self):
        if isinstance(self.target_gid_or_population, int):
            if self.simulation is None:
                return None
            else:
                return self.simulation.gid_dict[self.target_gid_or_population]
        else: 
            return self.target_gid_or_population

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
        try:
            self.initialize_connection_distribution()
        except AttributeError:
            pass  

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

        # Delay vals need to be cleaned up to account for not necessarily being evenly divisible by dt:
        delay_ind_dict = {}
        self.delay_inds = np.array(np.round(self.delay_vals/self.simulation.dt), dtype=np.int)
        for curr_ind, curr_prob in zip(self.delay_inds, self.delay_probs):
            delay_ind_dict.setdefault(curr_ind, []).append(curr_prob)

        self.delay_inds = sorted(delay_ind_dict.keys())
        self.delay_vals = np.array([self.simulation.dt*ii for ii in self.delay_inds])
        self.delay_probs = np.array([np.sum(delay_ind_dict[ii]) for ii in self.delay_inds])
        util.assert_probability_mass_conserved(self.delay_probs)
        
        max_delay_ind = max(self.delay_inds)
        self.delay_probability_vector = np.zeros(max_delay_ind+1)
        self.delay_probability_vector[self.delay_inds] = self.delay_probs
        self.delay_probability_vector = self.delay_probability_vector[::-1]
        
        # Determine delay_queue:
        if self.delay_queue_initial_condition is None:
            self.delay_queue = self.source.initialize_delay_queue(max_delay_ind)
        else:
            self.delay_queue = self.delay_queue_initial_condition
            assert len(self.delay_queue) == len(self.delay_probability_vector)
    
        self.delay_queue = collections.deque(self.delay_queue)

    def update(self):
        """Update Connection,  called once per timestep."""
        
        self.delay_queue[0] = self.simulation.get_curr_firing_rate(self.simulation.gid_dict[self.source])
        self.delay_queue.rotate(-1)

    @property
    def curr_delayed_firing_rate(self):
        """Current firing rate of the source (float).

        Property that accesses the firing rate at the top of the delay queue,
        from the source population.
        """
        
        try:
            assert len(self.delay_queue) == len(self.delay_probability_vector)
            return np.dot(self.delay_queue, self.delay_probability_vector)
        except:
            self.initialize_delay_queue()
            assert len(self.delay_queue) == len(self.delay_probability_vector)
            return np.dot(self.delay_queue, self.delay_probability_vector)
            
    def to_dict(self):
        
        if self.source is None or isinstance(self.source, int):
            source = self.source
        else:
            source = self.source.gid
            
        if isinstance(self.target, int) or self.target is None:
            target = self.target
        else:
            target = self.target.gid
        
        data_dict = {'source':source,
                     'target':target,
                     'nsyn':self.nsyn,
                     'weights':(self.weights.tolist(), self.probs.tolist()),
                     'delays':(self.delay_vals.tolist(), self.delay_probs.tolist()),
                     'metadata':self.metadata,
                     'class':(__name__, self.__class__.__name__)
                    }
        
        return data_dict

    
    def to_json(self, fh=None, **kwargs):
        '''Save the population contents to json'''
         
        data_dict = self.to_dict()
        indent = kwargs.pop('indent',2)
         
        if fh is None:
            return json.dumps(data_dict, indent=indent, **kwargs)
        else:
            return json.dump(data_dict, fh, indent=indent, **kwargs)
        
    def copy(self):
        return Connection(**self.to_dict())