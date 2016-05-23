import numpy as np
import json

class SimulationConfiguration(object):
    
    def __init__(self, dt, tf, t0=0, checkpoint_file_name='checkpoint.json', checkpoint_period=np.inf):
        
        self.dt = dt
        self.tf = tf
        self.t0 = t0
        self.checkpoint_file_name = checkpoint_file_name
        self.checkpoint_period = checkpoint_period
        
        
    def to_dict(self):
        
        return {'dt':self.dt,
                'tf':self.tf,
                't0':self.t0,
                'checkpoint_file_name':self.checkpoint_file_name,
                'checkpoint_period':self.checkpoint_period,
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