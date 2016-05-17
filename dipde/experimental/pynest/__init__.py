import nest
from distutils.version import LooseVersion
from dipde.internals.internalpopulation import InternalPopulation
from dipde.internals.externalpopulation import ExternalPopulation
from dipde.internals.network import Network
from dipde.internals.connection import Connection as Connection
import numpy as np
import copy

# Check pynest version
try:
    assert LooseVersion(nest.version().split()[1]) >= LooseVersion("2.6.0")
except AssertionError:
    raise Exception('pynest version %s must be updated to >= 2.6.0' % LooseVersion(nest.version().split()[1]))
        

def get_kernel(dt=.0001, seed=None, number_of_processors=1, verbose=True):
    
    if seed is None:
        seed = np.random.randint(1,100000)
    
    import nest as kernel
    kernel.ResetKernel()
    kernel.SetKernelStatus({"local_num_threads": number_of_processors})
    N_vp = kernel.GetKernelStatus(['total_num_virtual_procs'])[0]
    kernel.SetKernelStatus({'grng_seed' : seed+N_vp})
    kernel.SetKernelStatus({'rng_seeds' : range(seed+N_vp+1, seed+2*N_vp+1)})
    kernel.SetKernelStatus({"resolution": dt*1000, "print_time": verbose})
    
    return kernel

class SpikeMonitor(object):
    
    def __init__(self, name, source, kernel):
        
        self.source_gids = source.gids
        self.kernel = kernel
        
        self.gid = kernel.Create("spike_detector")
        
        kernel.SetStatus(self.gid,[{"label": name,
                           "withtime": True,
                           "withgid": True,
                           "to_file":False}])
        
        kernel.Connect(self.source_gids, self.gid, 'all_to_all')
        
    def firing_rate(self, t0, tf, dt):
        bins = np.arange(t0,tf+dt,dt)
        return (bins[1:]+bins[:-1])/2, np.histogram(self.times, bins)[0].astype(np.float64)/len(self.source_gids)/dt
    
    @property
    def senders(self):
        return self.kernel.GetStatus(self.gid, "events")[0]['senders']
    
    @property
    def times(self):
        time_array = np.array(self.kernel.GetStatus(self.gid, "events")[0]['times'])*.001
        return time_array + .00001*np.random.randn(len(time_array))
    
class PoissonPopulation(object):
    
    def __init__(self, name, firing_rate, number_of_neurons, kernel, start=0.):
        
        self.name = name
        self.firing_rate = firing_rate
        self.number_of_neurons = number_of_neurons
        self.gids = kernel.Create("poisson_generator", number_of_neurons, params={"rate": float(firing_rate), 'start':float(start)/.001})
        
def get_poisson_population(external_population, name, number_of_neurons, kernel, start=0):
    
    firing_rate = float(external_population.firing_rate_string)
    name = str(name)
    return PoissonPopulation(name, firing_rate, number_of_neurons, kernel, start=0.)
        
class IAFPSCDeltaPopulation(object):
    
    def __init__(self, 
                 name, 
                 number_of_neurons, 
                 kernel, 
                 tau_m,
                 tau_refrac,
                 v_th):

        self.name = name
        
        if tau_refrac == 0.:
            tau_refrac = kernel.GetKernelStatus("resolution")/1000

        # Create population:
        curr_neuron_params= {   "V_reset"   : 0.,
                                "tau_m"     : tau_m,
                                "C_m"       : 250.,
                                "V_th"      : v_th,
                                "t_ref"     : tau_refrac*1000,
                                "V_m"       : 0.,
                                "E_L"       : 0.}
        
        self.gids = kernel.Create("iaf_psc_delta", number_of_neurons, params=curr_neuron_params)
        
def get_iafpscdelta_population(internal_population, name, number_of_neurons, kernel):
    
    tau_m = internal_population.tau_m
    v_th = internal_population.v_max
    
    return IAFPSCDeltaPopulation(name, 
                                 number_of_neurons, 
                                 kernel,
                                 tau_m,
                                 0,
                                 v_th)
        
def connect_one_to_one(source, target, weight, kernel, delay=None):
    
    delay = clean_up_delay_units(delay, kernel)
    weight = clean_up_units(weight)
    
    kernel.Connect(source.gids, target.gids, "one_to_one", {"weight":weight, 'delay': delay})
    
def connect_nsyn(source, target, nsyn, weight, kernel, autapses=True, multapses=True, delay=None):
    delay = clean_up_delay_units(delay, kernel)
    weight = clean_up_units(weight)
    conn_dict = {'rule': 'fixed_indegree', 'indegree': nsyn, 'autapses': autapses, 'multapses': multapses}
    syn_dict = {'weight': weight, 'delay': delay}
    
    kernel.Connect(source.gids, target.gids, conn_dict, syn_dict)
    
def connect_random(source, target, p, weight, kernel, autapses=True, multapses=True, delay=None):

    delay = clean_up_delay_units(delay, kernel)
    weight = clean_up_units(weight)
    conn_dict = {'rule': 'pairwise_bernoulli', 'p': float(p), 'autapses': autapses, 'multapses': multapses}
    syn_dict = {'weight': weight, 'delay': delay}
    
    kernel.Connect(source.gids, target.gids, conn_dict, syn_dict)
    
def connect_fixed(source, target, N, weight, kernel, autapses=True, multapses=True, delay=None):
    
    delay = clean_up_delay_units(delay, kernel)
    weight = clean_up_units(weight)
     
    conn_dict = {'rule': 'fixed_total_number', 'N': N, 'autapses': autapses, 'multapses': multapses}
    syn_dict = {'weight': weight, 'delay': delay}
    kernel.Connect(source.gids, target.gids, conn_dict, syn_dict)
    
def clean_up_units(input_data):
    
    output = copy.copy(input_data)
    if isinstance(output, (dict,)):
        for key in output.keys():
            if key in ['mu', 'sigma', 'high', 'low', 'lambda']:
                output[key] = output[key]*1000
            elif key in ['distribution']:
                pass
            else:
                raise NotImplementedError
    elif isinstance(output, (float,)):
        output = output*1000
    else:
        raise NotImplementedError
        
    return output

def clean_up_delay_units(input_data, kernel):
    
    if input_data is None or input_data == 0.:
        return kernel.GetKernelStatus("resolution")
    else:
        output = copy.copy(input_data)
        if isinstance(output, (dict,)) and 'low' in output:
            output['low'] = kernel.GetKernelStatus("resolution")*.001 # This will get converted back by the next function
        return clean_up_units(output)

def create_simulation(dipde_simulation):
    
    print 
    
#     kernel = util.get_kernel(dt=dt, tf=tf, seed=seed, number_of_processors=number_of_processors, verbose=verbose)

def get_connection_weight(connection):
    if isinstance(connection.original_weights, dict):
        if connection.original_weights['distribution'] == 'delta':
            return clean_up_units(connection.original_weights['weight'])
        else:
            return clean_up_units(connection.original_weights)
    else:
        raise NotImplementedError
    
def get_connection_delay(connection, kernel):
    return clean_up_delay_units(connection.original_delays, kernel)
#     if isinstance(connection.original_delay, dict):
#         if connection.original_weights['distribution'] == 'delta':
#             return clean_up_units(connection.original_weights['weight'])
#         else:
#             return clean_up_units(connection.original_weights)
#     else:
#         raise NotImplementedError

def set_connection(dipde_connection, linking_dict, kernel):
    
    nest_source = linking_dict[dipde_connection.source]
    nest_target = linking_dict[dipde_connection.target]
    
    nsyn = dipde_connection.nsyn
    weight = get_connection_weight(dipde_connection)
    delay = get_connection_delay(dipde_connection, kernel)
    print delay
    connect_nsyn(nest_source, nest_target, nsyn, weight, kernel, multapses=True, autapses=True, delay=delay)


if __name__ == "__main__":

    k = get_kernel()
    
    


#     # Settings:
#     t0 = 0.
#     dt = .0001
#     dv = .0001
#     tf = .1
#     update_method = 'approx'
#     approx_order = 1
#     tol = 1e-14
#     
#     b1 = ExternalPopulation('100', record=True)
#     i1 = InternalPopulation(v_min=0, v_max=.02, dv=dv, update_method=update_method, approx_order=approx_order, tol=tol)
#     b1_i1 = Connection(b1, i1, 1, weights=.005, delay=0.0)
#     simulation = Network([b1, i1], [b1_i1], verbose=True)
#     
#     simulation.run(dt=dt, tf=tf, t0=t0)
#     
#     # Visualize:
#     import matplotlib.pyplot as plt
#     i1 = simulation.population_list[1]
#     fig, ax = plt.subplots(figsize=(3,3))
#     i1.plot(ax=ax)
#     plt.xlim([0,tf])
#     plt.ylim(ymin=0)
#     plt.xlabel('Time (s)')
#     plt.ylabel('Firing Rate (Hz)')
#     fig.tight_layout()
#     plt.show()