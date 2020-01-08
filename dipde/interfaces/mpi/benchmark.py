import json
import os
# Set up number of threads for fair comparison:
os.environ['OPENBLAS_NUM_THREADS'] = '1'
import copy
import logging
import argparse
logging.disable(logging.CRITICAL)
from dipde.interfaces.mpi.synchronizationharness import MPISynchronizationHarness
from dipde.profiling import time_network

# Example call to run:
# mpiexec -n 1 python benchmark.py --benchmark=singlepop --scale=4

def get_singlepop_benchmark_network(scale=2):
    
    from dipde.internals.internalpopulation import InternalPopulation
    from dipde.internals.externalpopulation import ExternalPopulation
    from dipde.internals.network import Network
    from dipde.internals.connection import Connection as Connection

    # Settings:
    dv = .0001
    update_method = 'approx'
    approx_order = None
    tol = 1e-14
    
    # Run simulation:
    b_list = []
    i_list = []
    conn_list = []
    for _ in range(scale):
        b = ExternalPopulation(100, record=True)
        i = InternalPopulation(v_min=0, v_max=.02, dv=dv, update_method=update_method, approx_order=approx_order, tol=tol)
        c = Connection(b, i, 1, weights=.005)
        b_list += [b]
        i_list += [i]
        conn_list += [c]
    return Network(b_list+i_list, conn_list)

def get_recurrent_singlepop_benchmark_network(scale=2):
    
    from dipde.internals.internalpopulation import InternalPopulation
    from dipde.internals.externalpopulation import ExternalPopulation
    from dipde.internals.network import Network
    from dipde.internals.connection import Connection as Connection

    # Settings:
    dv = .0001
    update_method = 'approx'
    approx_order = None
    tol = 1e-14
    
    # Run simulation:
    b_list = []
    i_list = []
    conn_list = []
    for _ in range(scale):
        
        b = ExternalPopulation(100, record=True)
        i = InternalPopulation(v_min=0, v_max=.02, dv=dv, update_method=update_method, approx_order=approx_order, tol=tol)
        c = Connection(b, i, 1, weights=.005)
        b_list += [b]
        i_list += [i]
        conn_list += [c]
        
    for i_s in i_list:
        for i_t in i_list:
            c = Connection(i_s, i_t, 2./len(i_list), weights=.005)
            conn_list += [c]
    
    return Network(b_list+i_list, conn_list)

# This is envoked by test_mpi, for module-level running
if __name__ == '__main__':
    
    # Parse arguments:
    parser = argparse.ArgumentParser() # pragma: no cover
    parser.add_argument('--benchmark',type=str, choices=['singlepop', 'recurrent_singlepop'],default='recurrent_singlepop') # pragma: no cover
    args, remaining_args = parser.parse_known_args() # pragma: no cover
    
    if args.benchmark == 'singlepop':                   # pragma: no cover
        
        # Singlepop-specific configuration:
        network_getter = get_singlepop_benchmark_network  # pragma: no cover
        parser_singlepop = argparse.ArgumentParser()  # pragma: no cover
        parser_singlepop.add_argument('--scale',type=int,default=2)  # pragma: no cover
        trial_args = parser_singlepop.parse_args(remaining_args)  # pragma: no cover
        
    elif args.benchmark == 'recurrent_singlepop':               # pragma: no cover
        
        # Singlepop-specific configuration:
        network_getter = get_recurrent_singlepop_benchmark_network # pragma: no cover
        parser_singlepop = argparse.ArgumentParser()  # pragma: no cover
        parser_singlepop.add_argument('--scale',type=int,default=2)  # pragma: no cover
        trial_args = parser_singlepop.parse_args(remaining_args) # pragma: no cover
        
    else:                                           # pragma: no cover
        raise NotImplementedError(args.benchmark)  # pragma: no cover
    
    network = network_getter(**vars(trial_args))        # pragma: no cover
    synchronization_harness = MPISynchronizationHarness(network)        # pragma: no cover
    run_time = time_network(network, synchronization_harness=synchronization_harness)       # pragma: no cover
    
    if network.rank == 0:                               # pragma: no cover

        result_dict = copy.copy(network.firing_rate_organizer.firing_rate_dict_internal)[network.ti]        # pragma: no cover
        result_dict['run_time'] = run_time          # pragma: no cover

        print(json.dumps(result_dict))       # pragma: no cover
            
            


    