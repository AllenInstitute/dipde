import json
import importlib
import threading
import types
import numpy as np
import time
from simulationconfiguration import SimulationConfiguration
import logging
logger = logging.getLogger(__name__)

class Simulation(object):
    
    def __init__(self, **kwargs):
        
        network = kwargs.get('network', None)
        simulation_configuration = kwargs.get('simulation_configuration', None)
        
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

        self.checkpoint_period = getattr(self.simulation_configuration, 'checkpoint_period', np.inf)
        self.checkpoint_file_name = getattr(self.simulation_configuration, 'checkpoint_file_name', 'checkpoint.json')
        assert self.checkpoint_file_name[-4:] == 'json'

        self.thread = threading.Thread(target=self.run_checkpoint_thread)
        self.thread.daemon = True

    def run(self):
        
        # Monkey patch the trapping function onto the network callback
        old_network_callback = self.network.update_callback
        def new_network_callback(network_self, network):
            old_network_callback(network)
            self._simulation_update_callback(network)
        self.network.update_callback = types.MethodType(new_network_callback, self.network)
        
        self.pause = False
        if not (self.checkpoint_file_name is None or self.checkpoint_period ==np.inf): 
            self.thread.start() 
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
                raise Exception('Initialized network but didnt run. This should not be possible.') # pragma: no cover
    
    
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
        
    def run_checkpoint_thread(self):
        while True:
            
            time.sleep(self.checkpoint_period)
              
            # Request pause
            self.pause = True 
            while self._network_trapped_at_callback == False:
                time.sleep(.1) 
              
            # Network is at update_callback, safe to write:
            checkpoint_simulation_configuration = SimulationConfiguration(t0=self.network.t, 
                                                                            tf=self.simulation_configuration.tf,
                                                                            dt=self.simulation_configuration.dt,
                                                                            checkpoint_file_name = self.simulation_configuration.checkpoint_file_name,
                                                                            checkpoint_period=self.simulation_configuration.checkpoint_period)
            checkpoint_simulation = Simulation(simulation_configuration=checkpoint_simulation_configuration,
                                                     network = self.network)
            checkpoint_simulation.to_json(fh=open(self.checkpoint_file_name, 'w'))
            logger.info('Checkpoint (%s): %s' % (self.checkpoint_file_name, self.network.t))
              
            # Release from pause
            self.pause = False
            
    def _simulation_update_callback(self, network):
        self._network_trapped_at_callback = True
        while self.pause == True:
            time.sleep(.1)
        self._network_trapped_at_callback = False