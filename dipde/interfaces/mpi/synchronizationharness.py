from dipde.interfaces.mpi import set_number_of_threads
from mpi4py import MPI
import json
import logging
import numpy as np

comm = MPI.COMM_WORLD

class MPISynchronizationHarness(object):
    
    def __init__(self, network, number_of_threads=1):
        
        set_number_of_threads(number_of_threads)
        
        
        
        self.size = comm.Get_size()
        self.rank = comm.Get_rank()
        
        self.network = network
        self.logger = logging.getLogger(__name__)
        self.gid_list_dict = {}
        for curr_rank in range(self.size):
            self.gid_list_dict[curr_rank] = [gid for gid in range(len(network.population_list)) if self.gid_to_rank(gid) == curr_rank]
        
        self.gid_list = self.gid_list_dict[self.rank]
        self.send_buffer = np.empty(len(self.gid_list))
        self.receive_buffer = np.empty(len(self.network.population_list))



        # Create dictionary of number of populations per rank:
        self.rank_to_numpop_dict = {}
        for gid in range(len(network.population_list)):
            curr_rank = self.gid_to_rank(gid)
            self.rank_to_numpop_dict[curr_rank] = self.rank_to_numpop_dict.get(curr_rank, 0) + 1
        
        # Create a dictionary of gid to position in receive_buffer:
        counter = 0
        self.receive_buffer_ind_to_gid_dict = {}
        for curr_rank in range(self.size):
            for curr_gid in self.gid_list_dict[curr_rank]:
                self.receive_buffer_ind_to_gid_dict[counter] = curr_gid        
                counter += 1
        
        self.sendcounts = [self.rank_to_numpop_dict.get(curr_rank,0) for curr_rank in range(self.size)]
        self.displacements = np.zeros_like(self.sendcounts)
        self.displacements[1:] = np.cumsum(np.array(self.sendcounts[:-1]))  

    def gid_to_rank(self, gid):
        return gid%self.size
            
    def initialize(self, i0):
        pass
        
    def update(self, ii, data_to_send):
        self.logger.debug('Rank %s(%s): Updating step' % (self.rank, ii))
        
        # Load up send buffer:
        for ii, curr_gid in enumerate(self.gid_list):
            self.send_buffer[ii] = data_to_send[curr_gid]
        
        # Gather firing rates from other processes, and insert into organizer:
        comm.Allgatherv(self.send_buffer,[self.receive_buffer,self.sendcounts,self.displacements,MPI.DOUBLE])
        for ii, curr_fr in enumerate(self.receive_buffer):
            data_to_send[self.receive_buffer_ind_to_gid_dict[ii]] = curr_fr

        # Synchronize
#         comm.Barrier()    

#         if self.rank == 0:
#             for ii in range(len(self.network.population_list)):
#                 print data_to_send[ii]


#             self.logger.debug('Rank %s(%s): Sending  payload to   %s(%s), %s' % (self.rank, ii, curr_rank, ii, outgoing_payload))
            
            
        # Wait to hear from other nodes, blocking:
#             self.logger.debug('Rank %s(%s): Received payload from %s(%s), %s' % (self.rank, ii, curr_source_rank, curr_ii, outgoing_payload))

#         self.logger.debug('Rank %s(%s): completed' % (self.rank, ii))
        
    def finalize(self):
        pass

        
            
        