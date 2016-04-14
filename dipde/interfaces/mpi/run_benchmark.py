import matplotlib.pyplot as plt
import subprocess

benchmark_file_name = '/data/mat/nicholasc/dipde2/dipde_dev/dipde/interfaces/mpi/benchmark.py'

def get_benchmark_command(nproc, scale, benchmark='recurrent_singlepop'):
    return 'mpiexec -n %s python %s --benchmark=%s --scale=%s' % (nproc, benchmark_file_name, benchmark, scale)

def run_benchmark(nproc, scale, benchmark='recurrent_singlepop'):
    
    cmd = get_benchmark_command(nproc, scale, benchmark=benchmark)

    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    result_list = [line for line in p.stdout.readlines()]
    retval = int(p.wait())
    assert retval == 0
    assert len(result_list) == 1
    return float(result_list[0])

scale_list = [1,2,4,8,16,32,64]
nproc_list = [1,2,4,8,16]


nproc_result_dict = {}
for nproc in nproc_list:
    curr_nproc_result_list = []
    for scale in scale_list:
        result = run_benchmark(nproc,scale)
        curr_nproc_result_list.append(result)
    nproc_result_dict[nproc] = curr_nproc_result_list
    print nproc, nproc_result_dict[nproc]

# fig, ax = plt.subplots()

# p = subprocess.Popen('ls', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
# for line in p.stdout.readlines():
#     print line
# print p.wait()