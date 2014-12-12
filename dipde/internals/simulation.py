from dipde.internals.connectiondistributioncollection import ConnectionDistributionCollection
import time

class Simulation(object):
    
    def __init__(self, dt=.001, tf=.1, network=None, verbose=True):
        
        self.dt = dt
        self.tf = tf
        self.network = network
        self.verbose = verbose
        
    def initialize(self, t0=0):
        
        # Initialize:
        self.connection_distribution_collection = ConnectionDistributionCollection()
        self.t = t0
        
        # Network needs access to the simulation
        self.network.simulation = self
        
        # Monkey-patch dt to the populations:
        for p in self.network.population_list:
            p.simulation = self
            
        # Each connection needs access to t:
        for c in self.network.connection_list:
            c.simulation = self
        
        # Initialize network:
        self.network.initialize()
        
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
            
            for p in self.network.internal_population_list:
                p.update_total_input_dict()
                p.update_propability_mass()
                p.update_firing_rate()
            
            for p in self.network.population_list:
                if p.record == True: p.update_firing_rate_recorder()
                
            for c in self.network.connection_list:
                c.update_delay_queue()
                
        self.run_time = time.time() - t0

        
    def apply_connection(self):
        pass









