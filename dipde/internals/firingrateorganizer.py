
class FiringRateOrganizer(object):
    
    def __init__(self, synchronization_harness):
        
        self.synchronization_harness = synchronization_harness
        self.synchronization_harness.firing_rate_organizer = self
        self.firing_rate_dict_internal = {}
        
    def push(self, ti, gid, firing_rate):
        self.firing_rate_dict_internal.setdefault(ti,{})[gid] = firing_rate
        
    def pull(self, ti, gid):
        return self.firing_rate_dict_internal[ti][gid]

    def drop(self, ti):
        del self.firing_rate_dict_internal[ti]
        
#     @property
#     def rank(self):
#         return self.distributed_configuration.rank()
       #         else:
#             return self.distributed_configuration.synchronization_harness.received_message_dict_external[requested_rank][ti][str(gid)]
    #         requested_rank = self.distributed_configuration.gid_to_rank(gid)
#         if requested_rank == self.rank:
       
       
       
        
# import numpy as np
# import sys
# import time
# import zmq
# import os




# # Settings:
# keep_history = False
# number_of_iterations = 1000
# 
# address_config_dict = {}
# for ii in range(int(os.environ['NUMBER_OF_NODES'])):
#     address_config_dict[ii] = "%s" % (5559+ii)
# 
# # Initializations:
# rank = int(sys.argv[1])
# context = zmq.Context()
# 
# # Receiver socket setup:
# receiver_socket_location = "ipc://%s" % address_config_dict[rank]
# receiver_socket = context.socket(zmq.PULL)
# receiver_socket.bind(receiver_socket_location)
# 
# # Sender sockets setup:
# sender_socket_list = []
# outside_rank_list = [curr_rank for curr_rank in address_config_dict.keys() if curr_rank != rank]
# sender_socket_location_list = ["ipc://%s" % address_config_dict[curr_rank] for curr_rank in outside_rank_list]
# for sender_socket_location in sender_socket_location_list:
#     sender_socket = context.socket(zmq.PUSH)
#     sender_socket.set_hwm(1)
#     sender_socket.connect(sender_socket_location)
#     sender_socket_list.append(sender_socket)
# 
# t0 = time.time()
# 
# received_message_dict = {}
# for ii in range(number_of_iterations):
#     
#     # Trash history on each node if it is not needed:
#     if ii > 0 and keep_history == False: del received_message_dict[ii-1]
#     
#     # Do some "processing":
#     data_to_send = np.random.rand()
#     
#     # Send to all other nodes, not blocking:
#     for socket in sender_socket_list:
#         socket.send_multipart([b'%s' % rank, b'%s' % data_to_send, b'%s' % ii])
#         
#     # Wait to hear from other nodes, blocking:
#     while len(received_message_dict.get(ii, [])) < len(sender_socket_list):
#         curr_source, payload, curr_ind = receiver_socket.recv_multipart()
#         received_message_dict.setdefault(int(curr_ind), {})[int(curr_source)] = float(payload)    
# 
# tf = time.time()
# print '%s: %s %s' % (rank, tf - t0, (tf-t0)/number_of_iterations)
#  
# # time.sleep(np.random.rand())
# # S = '%s: %s\n' % (rank, time.time() - t0)
# # for ii2 in range(ii+1):
# #     S += "%s: " % ii2+str(received_message_dict[ii2]) + '\n'
# # S += '\n'
# # print S
#  
#     
#     
#     