import json
import importlib

class Simulation(object):
    
    def __init__(self, **kwargs):
        
        network = kwargs.get('network', None)
        simulation_configuration = kwargs.get('simulation_configuration', None)
#         distributed_configuration = kwargs.get('distributed_configuration', None)
        
        
        # Create network
        #TODO: factor this functionality into a utility function
        if isinstance(network, dict):
            curr_module, curr_class = network.pop('module'), network.pop('class')
            self.network = getattr(importlib.import_module(curr_module), curr_class)(**network) 
        else: 
            self.network = network
            
        # Create simulation_configuration:
        if isinstance(simulation_configuration, dict):
            curr_module, curr_class = simulation_configuration.pop('module'), simulation_configuration.pop('class')
            self.simulation_configuration = getattr(importlib.import_module(curr_module), curr_class)(**simulation_configuration) 
        else: 
            self.simulation_configuration = simulation_configuration
        
    def run(self): 
        self.network.run(self.simulation_configuration.dt, self.simulation_configuration.tf, self.simulation_configuration.t0)

    @property
    def t0(self): return self.simulation_configuration.t0

    @property
    def dt(self): return self.simulation_configuration.dt
    
    @property
    def tf(self): return self.simulation_configuration.tf
    
    @property
    def completed(self):
        
        if not hasattr(self.network, 't'):
            return False
        else:
        
            if self.network.t == self.tf:
                return True
            else:
                raise Exception('Initialized network but didnt run. This should not be possible.')
    
    
    def to_dict(self):
        
        return {'network':self.network.to_dict(),
                'simulation_configuration':self.simulation_configuration.to_dict(),
                'class':self.__class__.__name__,
                'module':__name__}
        
    def to_json(self, fh=None, **kwargs):
        '''Save the contents of the InternalPopultion to json'''
        
        data_dict = self.to_dict()

        indent = kwargs.pop('indent',2)

        if fh is None:
            return json.dumps(data_dict, indent=indent, **kwargs)
        else:
            return json.dump(data_dict, fh, indent=indent, **kwargs)