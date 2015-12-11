
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

import bisect
import numpy as np
import scipy.stats as sps
import json
from dipde.internals import utilities as util
import logging
logger = logging.getLogger(__name__)

class InternalPopulation(object):
    """Population density class
    
    This class encapulates all the details necessary to propagate a population
    density equation driven by a combination of recurrent and background
    connections.  The voltage (spatial) domain discretization is defined by
    linear binning from v_min to v_max, in steps of dv (All in units of volts).
    The probability densities on this grid are recorded pv, and must always sum
    to 1. 
    
    Parameters
    ----------
    tau_m : float (default=.02)
        Time constant (unit: 1/sec) of neuronal population.
    v_min : float (default=-.1)
        Minimum of voltage domain (unit: volt).
    v_max : float (default=.02)
        Maximum of voltage domain (Absorbing boundary), i.e spiking threshold (unit: volt).
    dv : float (default=.0001)
        Voltage domain discritization size (unit: volt).
    record : bool (default=False)
        If True, a history of the output firing rate is recorded (firing_rate_record attribute).
    curr_firing_rate : float (default=0.0
        Initial/Current firing rate of the population (unit: Hz).
    update_method : str 'approx' or 'exact' (default='approx')
        Method to update pv (exact can be quite slow).
    approx_order : int or None (default=None)
        Maximum Taylor series expansion order to use when computing update to pv.
    tol : float (default=1e-12)
        Error tolerance used when computing update to pv.
    norm : non-zero int, np.inf, -np.inf, or 'fro' (default=np.inf)
        Vector norm used in computation of tol.
    **kwargs
        Any additional keyword args are stored as metadata (metadata attribute).
    
    Attributes
    ----------
    self.edges : np.array
        Vector defining the boundaries of voltage bins.
    self.pv : np.array
        Vector defining the probability mass in each voltage bin (self.pv.sum() = 1).
    self.firing_rate_record : list
        List of firing rates recorded during Simulation.
    self.t_record : list
        List of times that firing rates were recorded during Simulation.
    self.leak_flux_matrix : np.array
        Matrix that defines the flux between voltage bins.
    """
    
    def __init__(self, rank=0,
                       tau_m=.02,
                       v_min=-.1,
                       v_max=.02,
                       dv=.0001,
                       record=True,
                       initial_firing_rate=0.0,
                       update_method='approx',
                       approx_order=None,
                       tol=1e-12,
                       norm=np.inf,
                       p0=([0.],[1.]),
                       metadata={},
                       firing_rate_record=[],
                       t_record=[],
                       update_callback=lambda s:None, 
                       initialize_callback=lambda s:None,
                       **kwargs):
        
        # Store away inputs:
        self.rank = 0
        self.tau_m = util.discretize_if_needed(tau_m)
        self.p0 = util.discretize_if_needed(p0)
        if np.sum(self.tau_m.xk <= 0) > 0:
            raise Exception('Negative tau_m values detected: %s' % self.tau_m.xk) # pragma: no cover 
        
        self.v_min = v_min
        self.v_max = v_max
        self.dv = dv
        self.record = record
        self.curr_firing_rate = initial_firing_rate
        self.update_method = update_method
        self.approx_order = approx_order
        self.tol = tol
        self.norm = norm
        self.update_callback = update_callback
        self.initialize_callback = initialize_callback
        self.firing_rate_record = [x for x in firing_rate_record]
        self.t_record = [x for x in t_record]
        assert len(self.firing_rate_record) == len(self.t_record)

        # Additional metadata:
        self.metadata = metadata
        
        # Defined in initialization:
        self.edges = None
        self.pv = None
        self.leak_flux_matrix = None
        
        for key in kwargs.keys():
            assert key in ['class']
        
    def initialize(self):
        '''Initialize the population at the beginning of a simulation.
        
        In turn, this method:
        
            1) Initializes the voltage edges (self.edges) and probability mass in each bin (self.pv),
            
            2) Creates an initial dictionary of inputs into the population, and
             
            3) Resets the recorder that tracks firing rate during a simulation.
        
        This method is called by the Simulation object (initialization method),
        but can also be called by a user when defining an alternative time
        stepping loop.
        '''

        self.initialize_edges()
        self.initialize_probability()  # TODO: different initialization options

        if self.record == True: self.initialize_firing_rate_recorder()
        self.initialize_callback(self)
            
    def update(self):
        '''Update the population one time step.
        
        This method is called by the Simulation object to update the population 
        one time step.  In turn, this method:
            
            1) Calls the update_total_input_dict method to gather the current strengths of presynaptic input populations,
            
            2) Calls the update_propability_mass method to propagate self.pv one time-step,
            
            3) Calls the update_firing_rate method to compute the firing rate of the population based on flux over threshold, and
            
            4) Calls the update_firing_rate_recorder method to register the current firing rate with the recorder.
        '''
        
        self.update_total_input_dict()
        self.update_propability_mass()
        self.update_firing_rate()
        if self.record == True: self.update_firing_rate_recorder()
        logger.debug('GID(%s) Firing rate: %3.2f' % (self.gid, self.curr_firing_rate))
        self.update_callback(self)
        
    def initialize_edges(self):
        '''Initialize self.edges and self.leak_flux_matrix attributes.
        
        This method initializes the self.edges attribute based on the v_min,
        v_max, and dv settings, and creates a corresponding leak flux matrix
        based on this voltage discretization.
        '''

        # Voltage edges and leak matrix construction
        self.edges = util.get_v_edges(self.v_min, self.v_max, self.dv)
        self.leak_flux_matrix = util.leak_matrix(self.edges, self.tau_m)
    
    def initialize_probability(self):
        '''Initialize self.pv to delta-distribution at v=0.'''

        self.pv = util.get_pv_from_p0(self.p0, self.edges)
        util.assert_probability_mass_conserved(self.pv, 1e-15)
        
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
        
    def initialize_total_input_dict(self):
        '''Initialize dictionary of presynaptic inputs at beginning of simulation
        
        This method is typically called by the initialize method rather than on 
        its own.  It creates a dictionary of synaptic inputs to the population.
        '''
        
        # Aggregate input for each connection distribution:        
        self.total_input_dict = {}
        for c in self.source_connection_list:
            try:
                curr_input = self.total_input_dict.setdefault(c.connection_distribution, 0)
            except:
                c.initialize_connection_distribution()
                curr_input = self.total_input_dict.setdefault(c.connection_distribution, 0)
            self.total_input_dict[c.connection_distribution] = curr_input + c.curr_delayed_firing_rate * c.nsyn

    def get_total_flux_matrix(self):
        '''Create a total flux matrix by summing presynaptic inputs and the leak matrix.'''
        
        total_flux_matrix = self.leak_flux_matrix.copy()
        for key, val in self.total_input_dict.items():
            try:
                total_flux_matrix += key.flux_matrix * val
            except:  
                key.initialize()
                total_flux_matrix += key.flux_matrix * val
        return total_flux_matrix

    def update_total_input_dict(self):
        '''Update the input dictionary based on the current firing rates of presynaptic populations.'''
                    
        # Initialize to zero:
        for curr_connection_distribution in self.total_input_dict.keys():
            self.total_input_dict[curr_connection_distribution] = 0

        for c in self.source_connection_list:
            self.total_input_dict[c.connection_distribution] += c.curr_delayed_firing_rate * c.nsyn

    
    def update_propability_mass(self):
        """Create a total flux matrix, and propogate self.pv one time-step."""
        
        J = self.get_total_flux_matrix()
        
        if self.update_method == 'exact':
            self.pv = util.exact_update_method(J, self.pv, dt=self.simulation.dt)
            
        elif self.update_method == 'approx':

            if self.approx_order == None:
                self.pv = util.approx_update_method_tol(J, self.pv, tol=self.tol, dt=self.simulation.dt, norm=self.norm)

            else:
                self.pv = util.approx_update_method_order(J, self.pv, approx_order=self.approx_order, dt=self.simulation.dt)
        
        else:
            raise Exception('Unrecognized population update method: "%s"' % self.update_method)  # pragma: no cover
        
        # Checking stability of  
        if len(np.where(self.pv<0)[0]) != 0 or np.abs(np.abs(self.pv).sum() - 1) > 1e-15:
            self.pv[np.where(self.pv<0)] = 0
            self.pv /= self.pv.sum()
            logger.critical('Normalizing Probability Mass')
         
        
        
    def update_firing_rate(self):
        '''Update curr_firing_rate attribute based on the total flux of probability mass across threshold.'''
        
        # Compute flux:
        flux_vector = reduce(np.add, [key.threshold_flux_vector * val for key, val in self.total_input_dict.items()])
        self.curr_firing_rate = np.dot(flux_vector, self.pv) 
        
    def update_firing_rate_recorder(self):
        '''Record current time and firing rate, if record==True.
        
        This method is called once per time step.  If record is True, calling 
        this method will append the current time and firing rate to the firing 
        rate recorder.
        '''
        
        self.firing_rate_record.append(self.curr_firing_rate)
        self.t_record.append(self.simulation.t)
        
    @property
    def source_connection_list(self):
        '''List of all connections that are a source for this population.'''
        return [c for c in self.simulation.connection_list if c.target == self]
    
    @property
    def n_bins(self):
        '''Number of probability mass bins.'''
        
        return len(self.edges) - 1
    
    @property
    def n_edges(self):
        '''Number of probability mass bin edges.'''
        
        return len(self.edges)
    
    @property
    def gid(self):
        return self.simulation.gid_dict[self]
    
    def plot_probability_distribution(self, ax=None):
        '''Convenience method to plot voltage distribution.
        
        Parameters
        ----------
        ax : None or matplotlib.pyplot.axes object (default=None)
            Axes object to plot distribution on.  If None specified, a figure and axes object will be created.
        
        '''
        
        import matplotlib.pyplot as plt
        
        if ax == None:
            fig = plt.figure()
            ax = fig.add_subplot(1, 1, 1)
            
        ax.plot(self.edges[:-1], self.pv)
        return ax
    
    def plot(self, ax=None, **kwargs):
        '''Convenience method to plot firing rate history.
        
        Parameters
        ----------
        ax : None or matplotlib.pyplot.axes object (default=None)
            Axes object to plot distribution on.  If None specified, a figure and axes object will be created.
        
        '''
        
        import matplotlib.pyplot as plt
        
        if ax == None:
            fig = plt.figure()
            ax = fig.add_subplot(1, 1, 1)
        
        if self.firing_rate_record is None or self.t_record is None:
            raise RuntimeError('Firing rate not recorded on gid: %s' % self.gid)  # pragma: no cover
        ax.plot(self.t_record, self.firing_rate_record, **kwargs)
        return ax
    
    def get_firing_rate(self, t):
        '''Convenience function to get the firing rate at time "t" after simulation'''
        
        try:
            ind_list = [bisect.bisect_left(self.t_record,curr_t) for curr_t in t]
            return [self.firing_rate_record[ind] for ind in ind_list]    
        except:
            return self.firing_rate_record[bisect.bisect_left(self.t_record,t)]

    def to_dict(self):
        
        # Only needed if population not yet initialized:
        if self.edges is None:
            edges = util.get_v_edges(self.v_min, self.v_max, self.dv).tolist()
        else:
            edges = self.edges.tolist()
            
        if self.pv is None:
            pv = util.get_pv_from_p0(self.p0, edges).tolist()
        else:
            pv = self.pv.tolist()
            
        if len(self.firing_rate_record) is 0:
            initial_firing_rate = 0
        else:
            initial_firing_rate = self.firing_rate_record[-1] 
        

        data_dict = {'rank':self.rank,
                     'p0':(edges, pv), 
                      'norm':self.norm, 
                      'tau_m':(self.tau_m.xk.tolist(), self.tau_m.pk.tolist()),
                      'v_min':self.v_min,
                      'v_max':self.v_max,
                      'dv':self.dv,
                      'record':self.record,
                      'initial_firing_rate':initial_firing_rate,
                      'update_method':self.update_method,
                      'approx_order':self.approx_order,
                      'tol':self.tol,
                      'metadata':self.metadata,
                      'class':(__name__, self.__class__.__name__),
                      'firing_rate_record':self.firing_rate_record,
                      't_record':self.t_record}
        
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
        return InternalPopulation(**self.to_dict())
