import logging
import scipy.integrate as spi

import numpy as np

logger = logging.getLogger(__name__)

class PopulationInterface(object):
    '''Abstract Base Class for source populations'''
    
    def initialize(self):
        '''Override with behavior that sets an initial value'''
        self.set_curr_firing_rate(None)
    
    def update(self):
        '''Override with behavior that gets called once per time step'''
        logger.debug('GID(%s) Firing rate: %s' % (self.gid, self.curr_firing_rate))
    
    def set_curr_firing_rate(self, curr_firing_rate):
        '''Call to make "curr_firing_rate" visible to other populations. 
        Typically invoked once at initialization, and once in update'''
        self._curr_firing_rate = curr_firing_rate
    
    @property
    def t(self): return self.simulation.t
    
    @property
    def dt(self): return self.simulation.dt
    
    @property
    def gid(self): return self.simulation.gid_dict[self]
    
    @property
    def curr_firing_rate(self):
        return self._curr_firing_rate
    
    @property
    def source_connection_list(self):
        '''List of all connections that are a source for this population.'''
        return [c for c in self.simulation.connection_list if c.target == self]
    
    @property
    def source_firing_rate_dict(self):
        return dict((c.source.gid,self.simulation.get_curr_firing_rate(c.source.gid)) for c in self.source_connection_list)
    
    def initialize_delay_queue(self, max_delay_ind):    
        return np.core.numeric.zeros(max_delay_ind+1)

class ODE(PopulationInterface):
    '''Example Extension class that solves an ODE to provide firing rate input'''
    
    def __init__(self, func, y0=0):
        self.func = func
        self.y0 = y0
    
    def initialize(self):
        '''Set the initial condition'''
        self.set_curr_firing_rate(self.y0)
        
    def update(self):
        '''Update the firing rate based on the solution to an ODE'''
        super(self.__class__, self).update()
        curr_firing_rate = spi.odeint(self.func, self.curr_firing_rate, [self.t-self.dt, self.t])[1][0]
        self.set_curr_firing_rate(curr_firing_rate) 
        