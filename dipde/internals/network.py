class Network(object):
    
    def __init__(self, population_list=[], connection_list=[]):
        
        self.population_list = population_list
        self.connection_list = [c for c in connection_list if c.nsyn != 0]
        
    def initialize(self):
        
        for p in self.internal_population_list:
            p.initialize_edges()
            
        for p in self.internal_population_list:
            p.initialize_probability() # TODO: different initialization options
            
        for p in self.population_list:    
            if p.record == True: p.initialize_firing_rate_recorder()
            
        for c in self.connection_list:
            c.initialize_connection_distribution()
            c.initialize_delay_queue()

        for p in self.internal_population_list:
            p.initialize_total_input_dict()
            
        if self.simulation.semi_implicit == True:
            for p in self.internal_population_list:
                p.initialize_implicit()
                
            
    @property
    def external_population_list(self):
        return [p for p in self.population_list if p.type == 'external']
    
    @property
    def internal_population_list(self):
        return [p for p in self.population_list if p.type == 'internal']
            
    def replace_population(self, old, new):
        self.population_list.remove(old)
        self.population_list.append(new)
        
        for c in self.connection_list:
            if c.source == old:
                c.source = new
            if c.target == old:
                c.target = new
            
                
    
                
             

        