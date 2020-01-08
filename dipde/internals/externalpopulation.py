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

import sympy.parsing.sympy_parser as symp
from dipde.interfaces.pandas import to_df
from sympy.utilities.lambdify import lambdify
from sympy.abc import t as sym_t
import sympy
import numpy as np 
import types
from dipde.internals import utilities as util
import json
import logging
logger = logging.getLogger(__name__)
import numpy as np
from sympy import Piecewise

class ExternalPopulation(object):
    '''External (i.e. background) source for connections to Internal Populations.
    
    This class provides a background drive to internal population.  
    It is used as the source argument to a connection, in order to provide background drive.

    Parameters
    ----------
    firing_rate : numeric, str
        Output firing rate of the population.  If numeric type, this defines a constant background generator; if str, it is interpreted as a SymPy function with independent variable 't'.
    record : bool (default=False)
        If True, a history of the output firing rate is recorded (firing_rate_record attribute).
    **kwargs
        Any additional keyword args are stored as metadata (metadata attribute).
        
    Attributes
    ----------
    self.firing_rate_string : str
        String representation of firing_rate input parameter.
    self.metadata : dict
        Dictonary of metadata, constructed by kwargs not parsed during construction.
    self.firing_rate_record : list
        List of firing rates recorded during Simulation.
    self.t_record : list
        List of times that firing rates were recorded during Simulation.
    '''

    def __init__(self, firing_rate, rank=0,record=False, firing_rate_record=[], t_record=[], metadata={}, **kwargs):
        
        self.rank = 0
        if isinstance(firing_rate, str):
            self.firing_rate_string = str(firing_rate)
            self.closure = lambdify(sym_t,symp.parse_expr(self.firing_rate_string, local_dict={'Heaviside':lambda x: Piecewise((0,x<0), (1,x>0),(.5,True))}))
        elif hasattr(firing_rate, "__call__"):
            self.closure = firing_rate
        else:
            self.firing_rate_string = str(firing_rate)
            self.closure = lambdify(sym_t,symp.parse_expr(self.firing_rate_string))

        self.firing_rate_record = [x for x in firing_rate_record]
        self.t_record = [x for x in t_record]
        assert len(self.firing_rate_record) == len(self.t_record)

        self.record = record
        util.check_metadata(metadata)
        self.metadata = metadata

        self._simulation = None

        for key in kwargs.keys():
            assert key in ['class', 'module']

    @property
    def simulation(self):
        return self._simulation

    @simulation.setter
    def simulation(self, sim_obj):
        self._simulation = sim_obj


    def firing_rate(self, t):
        '''Firing rate of the population at time t (Hz).''' 
        
        curr_firing_rate = self.closure(t)
        if curr_firing_rate < 0:
            if np.abs(curr_firing_rate) < 1e-14:
                return np.abs(curr_firing_rate)
            else:
                raise RuntimeError("negative firing rate requested: %s, at t=%s" % (curr_firing_rate, t)) # pragma: no cover
        
        return curr_firing_rate
    
    @property
    def curr_firing_rate(self):
        return self.get_firing_rate(self.simulation.t)
    
    def initialize(self):
        '''Initialize the population at the beginning of a simulation.
        
        Calling this method resets the recorder that tracks firing rate during a
        simulation. This method is called by the Simulation object (
        initialization method), but can also be called by a user when defining
        an alternative time stepping loop.
        '''
        
        if self.record == True: self.initialize_firing_rate_recorder()
        
    def update(self):
        '''Update the population one time step.
        
        This method is called by the Simulation object to update the population 
        one time step.  In turn, this method calls the 
        update_firing_rate_recorder method to register the current firing rate 
        with the recorder.
        '''
        
        if self.record == True: self.update_firing_rate_recorder()
        logger.debug('GID(%s) Firing rate: %3.2f' % (self.gid, self.curr_firing_rate))
    
    def initialize_firing_rate_recorder(self):
        '''Initialize recorder at the beginning of a simulation.
        
        This method is typically called by the initialize method rather than on 
        its own.  It resets the lists that track the firing rate during 
        execution of the simulation.
        '''
        
        # Set up firing rate recorder:
        if len(self.firing_rate_record) == 0:
            self.firing_rate_record.append(self.curr_firing_rate)
        if len(self.t_record) == 0:
            self.t_record.append(self.simulation.t)
    
    def update_firing_rate_recorder(self):
        '''Record current time and firing rate, if record==True.
        
        This method is called once per time step.  If record is True, calling 
        this method will append the current time and firing rate to the firing 
        rate recorder.
        '''
        
        self.firing_rate_record.append(self.curr_firing_rate)
        self.t_record.append(self.simulation.t)
    
    def get_firing_rate(self, t):
        '''Property that accesses the firing rate ar time t of the population (Hz).'''

        return float(self.firing_rate(t))
    
    @property
    def gid(self):
        return self.simulation.gid_dict[self]
    
    @property
    def module_name(self):
        return __name__
    
    def to_dict(self):

        if not hasattr(self, 'firing_rate_string') and not hasattr(self, 'nwb_file_name'):
            raise RuntimeError('Cannot marshal ExternalPopulation with not firing_rate_string') # pragma: no cover

        data_dict = {'rank':self.rank,
                     'record':self.record,
                     'metadata':self.metadata,
                     'class':self.__class__.__name__,
                     'module':self.module_name
                      }
        
        if hasattr(self, 'firing_rate_string'):
            data_dict['firing_rate'] = self.firing_rate_string
#             raise RuntimeError('Cannot marshal ExternalPopulation with not firing_rate_string') # pragma: no cover
        

        
        return data_dict

    
    def to_json(self, fh=None, **kwargs):
        '''Save the population contents to json'''
        
        data_dict = self.to_dict()
        indent = kwargs.pop('indent',2)
        
        if fh is None:
            return json.dumps(data_dict, indent=indent, **kwargs)
        else:
            return json.dump(data_dict, fh, indent=indent, **kwargs)
        
    def copy(self):
        return ExternalPopulation(**self.to_dict())
    
    def to_df(self):
        return to_df(self)
    
    def plot(self, ax=None, **kwargs):
        '''Convenience method to plot firing rate history.
        
        Parameters
        ----------
        ax : None or matplotlib.pyplot.axes object (default=None)
            Axes object to plot distribution on.  If None specified, a figure and axes object will be created.
        
        '''
        
        import matplotlib.pyplot as plt
        show = kwargs.pop('show',False)
        close = kwargs.pop('close', False)
        
        if ax == None:
            fig = plt.figure()
            ax = fig.add_subplot(1, 1, 1)
        
        if self.firing_rate_record is None or self.t_record is None:
            raise RuntimeError('Firing rate not recorded on gid: %s' % self.gid)  # pragma: no cover
        ax.plot(self.t_record, self.firing_rate_record, **kwargs)
        
        if show == True:
            plt.show()

        if close == True:
            plt.close()

        return ax
    
    def initialize_delay_queue(self, max_delay_ind):
        delay_queue = np.core.numeric.zeros(max_delay_ind+1)
        for i in range(len(delay_queue)):
            delay_queue[i] = self.simulation.get_firing_rate(self.gid, self.simulation.t - self.simulation.dt*i)
        delay_queue = delay_queue[::-1]
        
        return delay_queue

