import dipde.interfaces.mpi.benchmark as benchmark_module
from dipde.interfaces.mpi import MPIJob
import json

def run_benchmark(nproc, scale, benchmark='recurrent_singlepop'):
    return json.loads(MPIJob(np=nproc,python='python',module_args=['--benchmark=%s' % benchmark, '--scale=%s' % scale],module=benchmark_module.__file__).run())


scale_list = [1,2,4]
nproc_list = [1,2,4]

nproc_result_dict = {}
for nproc in nproc_list:
    curr_nproc_result_list = []
    for scale in scale_list:
        result = run_benchmark(nproc,scale)
        curr_nproc_result_list.append(result['run_time'])
    nproc_result_dict[nproc] = curr_nproc_result_list
    print nproc, nproc_result_dict[nproc]
