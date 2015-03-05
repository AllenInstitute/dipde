import numpy as np
from dipde.internals import utilities as util

class InternalPopulation(object):
    """
    This class does something.
    
    Blah
    
    - **parameters**, **types**, **return** and **return types**::

      :param arg1: description
      :param arg2: description
      :type arg1: type description
      :type arg1: type description
      :return: return description
      :rtype: the return type description
    
    """
    
    def __init__(self, tau_m = .02,
                       v_min = -.1,
                       v_max = .02,
                       dv = .0001,
                       record = True, 
                       initial_firing_rate = 0,
                       update_method = 'approx',
                       approx_order = None,
                       tol = 1e-12,
                       norm = None,
                       **kwargs):
        
        # Store away inputs:
        self.tau_m = tau_m
        self.v_min = v_min
        self.v_max = v_max
        self.dv = dv
        self.record = record
        self.curr_firing_rate = initial_firing_rate
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
        
    def initialize_edges(self):

        # Voltage edges and leak matrix construction
        self.edges = util.get_v_edges(self.v_min, self.v_max, self.dv)
        self.leak_flux_matrix = util.leak_matrix(self.edges, self.tau_m)
    
    def initialize_probability(self):

        # Delta initial probability distribution:
        self.pv = np.zeros_like(self.edges[:-1])
        zero_bin_list = util.get_zero_bin_list(self.edges)
        for ii in zero_bin_list:
            self.pv[ii] = 1./len(zero_bin_list)
        
    def initialize_firing_rate_recorder(self):

        # Set up firing rate recorder:
        self.firing_rate_record = [self.curr_firing_rate]
        self.t_record = [0]
        
    def initialize_total_input_dict(self):
        
        # Aggregate input for each connection distribution:        
        self.total_input_dict = {}
        for c in self.source_connection_list:
            curr_input = self.total_input_dict.setdefault(c.connection_distribution, 0)
            self.total_input_dict[c.connection_distribution] = curr_input + c.curr_delayed_firing_rate*c.nsyn
            

    def get_total_flux_matrix(self):
        return reduce(np.add, [key.flux_matrix*val for key, val in self.total_input_dict.items()]) + self.leak_flux_matrix

    def update_total_input_dict(self):
                    
        # Initialize to zero:
        for curr_connection_distribution in self.total_input_dict.keys():
            self.total_input_dict[curr_connection_distribution] = 0

        for c in self.source_connection_list:
            self.total_input_dict[c.connection_distribution] += c.curr_delayed_firing_rate*c.nsyn

    
    def update_propability_mass(self):
        
        J = self.get_total_flux_matrix()
        
        if self.update_method == 'exact':
            self.pv = util.exact_update_method(J, self.pv, dt=self.simulation.dt)
            
        elif self.update_method == 'approx':

            if self.approx_order == None:
                self.pv = util.approx_update_method_tol(J, self.pv, tol=self.tol, dt=self.simulation.dt, norm=self.norm)

            else:
                self.pv = util.approx_update_method_order(J, self.pv, approx_order=self.approx_order, dt=self.simulation.dt)
        
        else:
            raise Exception('Unrecognized population update method: "%s"' % self.update_method) # pragma: no cover
        
        
    def update_firing_rate(self):
        
        # Compute flux:
        flux_vector = reduce(np.add, [key.threshold_flux_vector*val for key, val in self.total_input_dict.items()])
        self.curr_firing_rate = np.dot(flux_vector, self.pv) 
        
    def update_firing_rate_recorder(self):
        self.firing_rate_record.append(self.curr_firing_rate)
        self.t_record.append(self.t_record[-1]+self.simulation.dt)
        
    @property
    def source_connection_list(self):
        return [c for c in self.simulation.network.connection_list if c.target == self]
    
    @property
    def n_bins(self):
        return len(self.edges) - 1
    
    @property
    def n_edges(self):
        return len(self.edges)
    
    def plot_probability_distribution(self, ax=None):
        
        import matplotlib.pyplot as plt
        
        if ax == None:
            fig = plt.figure()
            ax = fig.add_subplot(1,1,1)
            
        ax.plot(self.edges[:-1], self.pv)
        return ax
        

        