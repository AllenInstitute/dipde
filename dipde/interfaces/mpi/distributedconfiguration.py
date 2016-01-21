from dipde.interfaces.mpi.synchronizationharness import SynchronizationHarness
from mpi4py import MPI

class DistributedConfiguration(object):
    
    def __init__(self, gid_to_rank = None):
        
        self.number_of_processes = number_of_processes

        if gid_to_rank is None:
            def gid_to_rank(gid):
                return gid%self.number_of_processes
        self.gid_to_rank = gid_to_rank
        
        print map(self.gid_to_rank, range(10))
        
        self.synchronization_harness = SynchronizationHarness()
    
    def initialize(self, ti):
        self.synchronization_harness.initialize(ti)
        
    def update(self, ti, update_dict):
        self.synchronization_harness.update(ti, update_dict)
        
    def finalize(self):
        self.synchronization_harness.finalize()
        
    def rank(self):
        return self.synchronization_harness.rank

            
            
                    