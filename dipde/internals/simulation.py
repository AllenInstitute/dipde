from dipde.internals.connectiondistributioncollection import ConnectionDistributionCollection
import time

class Simulation(object):
    
    def __init__(self, 
                 population_list, 
                 connection_list, 
                 dt=.001, 
                 tf=.1, 
                 verbose=True):
        
        self.dt = dt
        self.tf = tf
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
        
    def run(self):
        
        # Initialize:
        t0 = time.time()
        self.initialize()
        self.initialization_time = time.time() - t0
        
        # Run
        t0 = time.time()
        while self.t < self.tf:
            
            self.t += self.dt
            if self.verbose: print 'time: %s' % self.t
            
            for p in self.population_list:
                p.update()
                
            for c in self.connection_list:
                c.update()
                
        self.run_time = time.time() - t0









