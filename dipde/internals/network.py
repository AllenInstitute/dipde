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

from dipde.internals.connectiondistributioncollection import ConnectionDistributionCollection
import time
from dipde.internals import utilities
import json
import importlib

from dipde.internals.firingrateorganizer import FiringRateOrganizer
from dipde.internals.internalpopulation import InternalPopulation
import logging
logger = logging.getLogger(__name__)

class Network(object):
    '''Initialize and run a dipde simulation.
    
    The Network class handles the initialization of population and connection
    objects, and provides a convenience time stepping loop to drive a network
    simulation.  Typical usage involves the create of populations and
    connections, construction of a simulation object, and then call to
    simulation.run()
    
    Parameters
    ----------
    population_list : list of ExternalPopulation, InternalPopulation objects
        List of populations to include in simulation.
    connection_list : list of Connection objects
        List of connections to include in simulation.
    verbose : bool (default=True)
        Setting True prints current time-step at each update evaluation.
    '''
    
    def __init__(self, 
                 population_list=[], 
                 connection_list=[],
                 metadata={},
                 run_callback=lambda s: None,
                 update_callback=lambda s: None):
        
        self.update_callback = update_callback
        self.run_callback = run_callback
        
        self.population_list = []
        for p in population_list:
            if isinstance(p, dict):
                curr_module, curr_class = p['class']
                curr_instance = getattr(importlib.import_module(curr_module), curr_class)(**p)
                self.population_list.append(curr_instance)
            else: 
                self.population_list.append(p)

        self.connection_list = []
        for c in connection_list:
            if isinstance(c, dict):
                curr_module, curr_class = c['class']
                curr_instance = getattr(importlib.import_module(curr_module), curr_class)(**c)
                if curr_instance.nsyn != 0:
                    self.connection_list.append(curr_instance)
            else:
                if c.nsyn != 0:
                    self.connection_list.append(c)


        self.gid_dict = dict((population, ii) for ii, population in enumerate(self.population_list))
        for key, val in self.gid_dict.items():
            self.gid_dict[val] = key
        
        # Initialize:
        self.connection_distribution_collection = ConnectionDistributionCollection()
        
        # Each population needs access to dt:
        for p in self.population_list:
            p.simulation = self
            
        # Each connection needs access to t:
        for c in self.connection_list:
            c.simulation = self
    
    @property
    def rank(self):
        return self.distributed_configuration.rank()

        
    def run(self, dt, tf, t0=0., distributed_configuration=utilities.NullObject()):
        '''Main iteration control loop for simulation
        
        The time step selection must be approximately of the same order as dv
        for the internal populations, if the 'approx' time stepping method is
        selected.
        
        Parameters
        ----------
        t0 : float (default=0.)
            Network start time (unit=seconds), passed to initialize call.
        tf : float (default=.1)
            Network end time (unit=seconds).
        dt : float (default=0.001)
            Time step (unit=seconds).
        '''

        self.distributed_configuration = distributed_configuration
        self.firing_rate_organizer = FiringRateOrganizer(self.distributed_configuration)
        
        self.dt = dt
        self.t0 = t0
        
        # Initialize:
        start_time = time.time()
        self.tf = tf
        self.ti = 0
        
        self.distributed_configuration.initialize(self.ti)
        
        # Initialize populations:
        for gid, p in enumerate(self.population_list):
            p.initialize()
            self.firing_rate_organizer.push(self.ti, gid, p.curr_firing_rate)
        
        self.distributed_configuration.update(self.ti, self.firing_rate_organizer.firing_rate_dict_internal[self.ti])
            
        for p in self.population_list:
            if isinstance(p, InternalPopulation):        
                p.initialize_total_input_dict()
        
        # Initialize connections:    
        for c in self.connection_list:
            c.initialize()
        self.initialization_time = time.time() - start_time
        
        
        
        # Run
        start_time = time.time()
        while self.t < self.tf:
            self.update()
            
        self.run_time = time.time() - start_time
        
        self.distributed_configuration.finalize()
        
        self.run_callback(self)
        
    @property
    def t(self):
        if self.t0 is None:
            return self.ti*self.dt
        else:
            return self.t0+self.ti*self.dt

    def update(self):

        self.firing_rate_organizer.drop(self.ti)
        self.ti += 1
        logger.info( 'time: %s' % self.t)
        
        for gid, p in enumerate(self.population_list):
            if self.distributed_configuration.gid_to_rank(gid) == self.rank:
                p.update()
                self.firing_rate_organizer.push(self.ti, gid, p.curr_firing_rate)
                
        self.distributed_configuration.update(self.ti, self.firing_rate_organizer.firing_rate_dict_internal[self.ti])
        
        for c in self.connection_list:
            c.update()
            
        self.update_callback(self)
        
    def to_dict(self):

        data_dict = {'population_list':[p.to_dict() for p in self.population_list],
                     'connection_list':[c.to_dict() for c in self.connection_list]}
        
        return data_dict
        
    def to_json(self, fh=None, **kwargs):
        '''Save the contents of the InternalPopultion to json'''
        
        data_dict = self.to_dict()

        indent = kwargs.pop('indent',2)

        if fh is None:
            return json.dumps(data_dict, indent=indent, **kwargs)
        else:
            return json.dump(data_dict, fh, indent=indent, **kwargs)

    def copy(self):
        return Network(**self.to_dict())
    
    def get_curr_firing_rate(self, gid):
        return self.firing_rate_organizer.pull(self.ti,gid)
        
    def get_firing_rate(self, gid, t):
        return self.population_list[gid].firing_rate(t)
        
         






