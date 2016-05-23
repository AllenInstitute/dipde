import logging
import os
import subprocess as sp

def set_number_of_threads(number_of_threads):
    os.environ['OPENBLAS_NUM_THREADS'] = '%s' % number_of_threads
    os.environ['MKL_NUM_THREADS']='%s' % number_of_threads
    os.environ['NUMEXPR_NUM_THREADS']='%s' % number_of_threads
    os.environ['OMP_NUM_THREADS']='%s' % number_of_threads

class MPIJob(object):
    log = logging.getLogger(__name__)
    mpi_command = 'mpiexec'
    
    def __init__(self, **kwargs):
        self.np = kwargs.get('np', '1')
        self.env = kwargs.get('env', os.environ.copy())
        self.module = kwargs.get('module', 'benchmark.py')
        self.python = kwargs.get('python', 'nrniv')
        self.module_args = kwargs.get('module_args', [])
    
    def run(self):
        subprocess_args = [MPIJob.mpi_command]
        
        subprocess_args.append('-np')
        subprocess_args.append(str(self.np))
        
        subprocess_args.append(self.python)
        
        subprocess_args.append(self.module)
        for arg in self.module_args:
            subprocess_args.append(arg)

        sub_process = sp.Popen(' '.join(subprocess_args),
                               shell=True,
                               stdin=sp.PIPE,
                               stdout=sp.PIPE,
                               close_fds=True)
        sp_output = sub_process.stdout
        x = sp_output.read()
        return x
