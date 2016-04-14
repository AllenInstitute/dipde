import logging
logging.disable(logging.CRITICAL)
import time

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
        b = ExternalPopulation(100)
        i = InternalPopulation(v_min=0, v_max=.02, dv=dv, update_method=update_method, approx_order=approx_order, tol=tol)
        c = Connection(b, i, 1, weights=.005)
        b_list += [b]
        i_list += [i]
        conn_list += [c]
    return Network(b_list+i_list, conn_list)

def get_recurrent_singlepop_benchmark_network(scale):
    
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
        
        b = ExternalPopulation(100)
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

if __name__ == '__main__':
    
    # Parse arguments:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--benchmark',type=str, choices=['singlepop', 'recurrent_singlepop'],default='recurrent_singlepop')
    args, remaining_args = parser.parse_known_args()
 
    # Set up number of threads for fair comparison:
    import os
    os.environ['OPENBLAS_NUM_THREADS'] = '1'
    
    from dipde.interfaces.mpi.synchronizationharness import MPISynchronizationHarness
    from dipde.profiling import time_network
    if args.benchmark == 'singlepop':
        
        # Singlepop-specific configuration:
        network_getter = get_singlepop_benchmark_network
        parser_singlepop = argparse.ArgumentParser()
        parser_singlepop.add_argument('--scale',type=int,default=2)
        trial_args = parser_singlepop.parse_args(remaining_args)
        
    elif args.benchmark == 'recurrent_singlepop':
        
        # Singlepop-specific configuration:
        network_getter = get_recurrent_singlepop_benchmark_network
        parser_singlepop = argparse.ArgumentParser()
        parser_singlepop.add_argument('--scale',type=int,default=6)
        trial_args = parser_singlepop.parse_args(remaining_args)
        
    else:
        raise NotImplementedError(args.benchmark)
    
    
    network = network_getter(**vars(trial_args))
    synchronization_harness = MPISynchronizationHarness(network)
    run_time = time_network(network, synchronization_harness=synchronization_harness)
    if network.rank == 0:
        print run_time
    


    