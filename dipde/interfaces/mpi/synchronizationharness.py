from mpi4py import MPI
import json
import logging

comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()

class MPISynchronizationHarness(object):
    
    def __init__(self, network):
        
        self.network = network
        self.rank = rank
        self.logger = logging.getLogger(__name__)
        self.gid_list = [gid for gid in range(len(network.population_list)) if self.gid_to_rank(gid) == self.rank]

    def gid_to_rank(self, gid):
        return gid%size
            
    def initialize(self, i0):
        pass
        
    def update(self, ii, data_to_send):
        self.logger.debug('Rank %s(%s): Updating step' % (self.rank, ii))
        print ii, data_to_send, self.gid_list
        

#             self.logger.debug('Rank %s(%s): Sending  payload to   %s(%s), %s' % (self.rank, ii, curr_rank, ii, outgoing_payload))
            
            
        # Wait to hear from other nodes, blocking:
#             self.logger.debug('Rank %s(%s): Received payload from %s(%s), %s' % (self.rank, ii, curr_source_rank, curr_ii, outgoing_payload))

#         self.logger.debug('Rank %s(%s): completed' % (self.rank, ii))
        
    def finalize(self):
        pass

        
            
        