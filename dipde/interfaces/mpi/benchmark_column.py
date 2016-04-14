import logging
logging.disable(logging.CRITICAL)
import time

def get_singlepop_benchmark_network(scale):
    
    from dipde.internals.internalpopulation import InternalPopulation
    from dipde.internals.externalpopulation import ExternalPopulation
    from dipde.internals.network import Network
    from dipde.internals.connection import Connection as Connection

    # Settings:
    dv = .0001
    update_method = 'approx'
    approx_order = None
    tol = 1e-14
    
    def f(self): time.sleep(.001)
#     def f(self): pass
    
    # Run simulation:
    b_list = []
    i_list = []
    conn_list = []
    for _ in range(scale):
        b = ExternalPopulation(100)
        i = InternalPopulation(v_min=0, v_max=.02, dv=dv, update_method=update_method, approx_order=approx_order, tol=tol, update_callback=f)
        c = Connection(b, i, 1, weights=.005)
        b_list += [b]
        i_list += [i]
        conn_list += [c]
    return Network(b_list+i_list, conn_list)

if __name__ == '__main__':
    
    # Parse arguments:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--benchmark',type=str, choices=['singlepop'],default='singlepop')
    args, remaining_args = parser.parse_known_args()
 
    # Set up number of threads for fair comparison:
    import os
    os.environ['OPENBLAS_NUM_THREADS'] = '1'
    
    from dipde.interfaces.mpi.synchronizationharness import MPISynchronizationHarness
    from dipde.profiling import time_network
    if args.benchmark == 'singlepop':
        
        # Singlepop-specific benchmark configuration:
        parser_singlepop = argparse.ArgumentParser()
        parser_singlepop.add_argument('--scale',type=int,default=2)
        args_singlepop = parser_singlepop.parse_args(remaining_args)
        
        network = get_singlepop_benchmark_network(args_singlepop.scale)
        synchronization_harness = MPISynchronizationHarness(network)
        run_time = time_network(network, synchronization_harness=synchronization_harness)
        if network.rank == 0:
            print run_time

    