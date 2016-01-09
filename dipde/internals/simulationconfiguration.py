import json

class SimulationConfiguration(object):
    
    def __init__(self, dt, tf, t0=0):
        
        self.dt = dt
        self.tf = tf
        self.t0 = t0
        
        
    def to_dict(self):
        
        return {'dt':self.dt,
                'tf':self.tf,
                't0':self.t0,
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