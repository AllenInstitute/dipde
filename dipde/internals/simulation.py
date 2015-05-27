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
    '''Initialize and run a dipde simulation
    
    The Simulation class handles the initialization of population and connection
    objects, and provides a convenience time stepping loop to drive a network  
    '''
    
    
    def __init__(self, 
                 population_list, 
                 connection_list, 
                 verbose=True):
        
        self.verbose = verbose
        
        self.population_list = population_list
        self.connection_list = [c for c in connection_list if c.nsyn != 0]
        
    def initialize(self, t0=0):
        
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









