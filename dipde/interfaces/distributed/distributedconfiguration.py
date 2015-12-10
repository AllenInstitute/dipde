from dipde.interfaces.distributed.synchronizationharness import SynchronizationHarness

class DistributedConfiguration(object):
    
    def __init__(self, rank,
                       number_of_processes = 1,
                       rank_address_function = lambda rank:"ipc://%s" % (5559+rank), 
                       gid_to_rank = None):
        
        self.number_of_processes = number_of_processes
        self.rank_address_function = rank_address_function

        if gid_to_rank is None:
            def gid_to_rank(gid):
                return gid%self.number_of_processes
        self.gid_to_rank = gid_to_rank

        self.address_config_dict = {}
        for ii in range(number_of_processes):
            self.address_config_dict[ii] = self.rank_address_function(ii)
            
        
        self.synchronization_harness = SynchronizationHarness(rank, self.address_config_dict)
    
    def initialize(self, ti):
        self.synchronization_harness.initialize(ti)
        
    def update(self, ti, update_dict):
        self.synchronization_harness.update(ti, update_dict)
        
    def finalize(self):
        self.synchronization_harness.finalize()
        
    def rank(self):
        return self.synchronization_harness.rank

            
            
                    