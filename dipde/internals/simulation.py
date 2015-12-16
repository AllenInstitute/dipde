import json

class Simulation(object):
    
    def __init__(self, network=None, simulation_configuration={}, distributed_configuration={}):
        
        self.network = network
        self.simulation_configuration = simulation_configuration
        
    def run(self):
        
        print self.simulation_configuration.to_dict()
        self.network.run(**self.simulation_configuration.to_dict())
        
    def to_dict(self):
        
        return {}
        
    def to_json(self, fh=None, **kwargs):
        '''Save the contents of the InternalPopultion to json'''
        
        data_dict = self.to_dict()

        indent = kwargs.pop('indent',2)

        if fh is None:
            return json.dumps(data_dict, indent=indent, **kwargs)
        else:
            return json.dump(data_dict, fh, indent=indent, **kwargs)