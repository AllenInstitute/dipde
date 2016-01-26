# import numpy as np
from dipde.interfaces.mpi import MPIJob
import dipde.interfaces.mpi.benchmark as benchmark


def test_benchmark_singlepop(verbose=False, np_range=[1,2], scale=2):
    
    run_time_list = []
    for num_proc in np_range:
        run_time = float(MPIJob(np=num_proc,python='python',module_args=['--benchmark=singlepop', '--scale=%s' % scale],module=benchmark.__file__).run())
        run_time_list.append(run_time)
        if verbose == True:
#             print '%2s: %3.3fs (%3.2fx)' % (num_proc, run_time_list[-1], np_range[0]*1./(num_proc/1./(run_time_list[0]/run_time_list[-1])))
            speedup_factor = run_time_list[0]/run_time_list[-1]
            percent_of_linear = speedup_factor/num_proc 
            print '%2s: %3.3fs (s:%3.2f, %%:%3.2f)' % (num_proc, run_time_list[-1], speedup_factor, percent_of_linear)
    
if __name__ == "__main__":                       # pragma: no cover
    test_benchmark_singlepop(verbose=True, np_range=[1,2])       # pragma: no cover