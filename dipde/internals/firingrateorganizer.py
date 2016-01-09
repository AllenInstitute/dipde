
class FiringRateOrganizer(object):
    
    def __init__(self, distributed_configuration):
        
        self.distributed_configuration = distributed_configuration
        self.firing_rate_dict_internal = {}
        
    def push(self, ti, gid, firing_rate):
        self.firing_rate_dict_internal.setdefault(ti,{})[gid] = firing_rate
        
    def pull(self, ti, gid):
        requested_rank = self.distributed_configuration.gid_to_rank(gid)
        if requested_rank == self.rank:
            return self.firing_rate_dict_internal[ti][gid]
        else:
            return self.distributed_configuration.synchronization_harness.received_message_dict_external[requested_rank][ti][str(gid)]
        
    def drop(self, ti):
        del self.firing_rate_dict_internal[ti]
        
    @property
    def rank(self):
        return self.distributed_configuration.rank()
       
       