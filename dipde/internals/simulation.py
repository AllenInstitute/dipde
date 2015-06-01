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

class Simulation(object):
    '''Initialize and run a dipde simulation.
    
    The Simulation class handles the initialization of population and connection
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
                 population_list, 
                 connection_list, 
                 verbose=True):
        
        self.verbose = verbose
        
        self.population_list = population_list
        self.connection_list = [c for c in connection_list if c.nsyn != 0]
        
    def initialize(self, t0=0.):
        '''Initialize simulation, populations, and connections.
        
        This function is typically called by the self.run() method, however can
        be called independently if defining a new time stepping loop.
        
        Parameters
        ----------
        t0 : float (default=0.)
            Simulation start time (unit=seconds).
        '''
        
        # Initialize:
        self.connection_distribution_collection = ConnectionDistributionCollection()
        self.t = t0
        
        # Monkey-patch dt to the populations:
        for p in self.population_list:
            p.simulation = self
            
        # Each connection needs access to t:
        for c in self.connection_list:
            c.simulation = self
        
        # Initialize populations:
        for p in self.population_list:
            p.initialize()
        
        # Initialize connections:    
        for c in self.connection_list:
            c.initialize()
        
    def run(self, t0=0., dt=.001, tf=.1):
        '''Main iteration control loop for simulation
        
        The time step selection must be approximately of the same order as dv
        for the internal populations, if the 'approx' time stepping method is
        selected.
        
        Parameters
        ----------
        t0 : float (default=0.)
            Simulation start time (unit=seconds), passed to initialize call.
        tf : float (default=.1)
            Simulation end time (unit=seconds).
        dt : float (default=0.001)
            Time step (unit=seconds).
        '''
        
        
        self.dt = dt
        self.tf = tf
        
        # Initialize:
        start_time = time.time()
        self.initialize(t0=t0)
        self.initialization_time = time.time() - start_time
        
        # Run
        start_time = time.time()
        while self.t < self.tf:
            
            self.t += self.dt
            if self.verbose: print 'time: %s' % self.t
            
            for p in self.population_list:
                p.update()
                
            for c in self.connection_list:
                c.update()
                
        self.run_time = time.time() - start_time









