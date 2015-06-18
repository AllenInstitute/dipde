
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

import numpy as np
from dipde.internals import utilities as util

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
    
    def __init__(self, tau_m=.02,
                       v_min=-.1,
                       v_max=.02,
                       dv=.0001,
                       record=True,
                       curr_firing_rate=0.0,
                       update_method='approx',
                       approx_order=None,
                       tol=1e-12,
                       norm=np.inf,
                       **kwargs):
        
        # Store away inputs:
        self.tau_m = tau_m
        self.v_min = v_min
        self.v_max = v_max
        self.dv = dv
        self.record = record
        self.curr_firing_rate = curr_firing_rate
        self.update_method = update_method
        self.approx_order = approx_order
        self.tol = tol
        self.norm = norm
        self.type = "internal"
        
        # Additional metadata:
        self.metadata = kwargs
        
        # Defined in initialization:
        self.edges = None
        self.pv = None
        self.firing_rate_record = None
        self.t_record = None
        self.leak_flux_matrix = None
        
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
        self.initialize_total_input_dict()
        if self.record == True: self.initialize_firing_rate_recorder()
            
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

        # Delta initial probability distribution:
        self.pv = np.zeros_like(self.edges[:-1])
        zero_bin_list = util.get_zero_bin_list(self.edges)
        for ii in zero_bin_list:
            self.pv[ii] = 1. / len(zero_bin_list)
        
    def initialize_firing_rate_recorder(self):
        '''Initialize recorder at the beginning of a simulation.
        
        This method is typically called by the initialize method rather than on 
        its own.  It resets the lists that track the firing rate during 
        execution of the simulation.
        '''

        # Set up firing rate recorder:
        self.firing_rate_record = [self.curr_firing_rate]
        self.t_record = [self.simulation.t]
        
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
        

        
