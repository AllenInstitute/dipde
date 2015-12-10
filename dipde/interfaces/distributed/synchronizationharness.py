import zmq
import json
import logging


# Initializations:
context = zmq.Context()

class SynchronizationHarness(object):
    
    def __init__(self, rank, address_config_dict):
        
        self.rank = rank
        self.address_config_dict = address_config_dict
        self.logger = logging.getLogger(__name__)
        
        # Receiver socket setup:
        self.receiver_socket_location = self.address_config_dict[self.rank]
        self.receiver_socket = context.socket(zmq.PULL)
        self.receiver_socket.bind(self.receiver_socket_location)
        self.logger.debug('Rank %s: Bound receiving socket %s' % (self.rank, self.receiver_socket_location))
        
        # Sender sockets setup:
        self.sender_socket_dict = {}
        self.outside_rank_list = [curr_rank for curr_rank in self.address_config_dict.keys() if curr_rank != self.rank]
        self.sender_socket_location_dict = {curr_rank:self.address_config_dict[curr_rank] for curr_rank in self.outside_rank_list}
        for curr_rank in self.outside_rank_list:
            sender_socket_location = self.sender_socket_location_dict[curr_rank]
            sender_socket = context.socket(zmq.PUSH)
            sender_socket.connect(sender_socket_location)
            self.sender_socket_dict[curr_rank] = sender_socket
            self.logger.debug('Rank %s: Connected to socket %s' % (self.rank, sender_socket_location))
            
    def initialize(self, ii=0):
        self.received_message_dict_external = {curr_rank:{} for curr_rank in self.outside_rank_list}
        self.ii0=ii
        self.logger.debug('Rank %s: Initialized' % (self.rank, ))
        
    def update(self, ii, data_to_send):
        self.logger.debug('Rank %s(%s): Updating step' % (self.rank, ii))
        outgoing_payload = json.dumps(data_to_send)
        
        # Trash history on each node if it is not needed:
        if ii > self.ii0: 
            for curr_rank in self.outside_rank_list:
                del self.received_message_dict_external[curr_rank][ii-1]
        
        # Send to all other nodes, not blocking:
        for curr_rank in self.outside_rank_list:
            socket = self.sender_socket_dict[curr_rank]
            self.logger.debug('Rank %s(%s): Sending  payload to   %s(%s), %s' % (self.rank, ii, curr_rank, ii, outgoing_payload))
            socket.send_multipart([b'%s' % self.rank, b'%s' % ii, b'%s' % outgoing_payload])
            
            
        # Wait to hear from other nodes, blocking:
        while len([True for rank_dict in self.received_message_dict_external.values() if ii in rank_dict]) < len(self.sender_socket_dict):
            curr_source_rank, curr_ii, received_payload = self.receiver_socket.recv_multipart()
            self.logger.debug('Rank %s(%s): Received payload from %s(%s), %s' % (self.rank, ii, curr_source_rank, curr_ii, outgoing_payload))
            self.received_message_dict_external[int(curr_source_rank)][int(curr_ii)] = json.loads(received_payload)

        self.logger.debug('Rank %s(%s): completed' % (self.rank, ii))
        
    def finalize(self):
        self.logger.debug('Rank %s: Disconnecting' % (self.rank,))
        self.receiver_socket.unbind(self.receiver_socket_location)
        for curr_rank in self.outside_rank_list:
            sender_socket_location = self.sender_socket_location_dict[curr_rank]
            sender_socket = self.sender_socket_dict[curr_rank]
            sender_socket.disconnect(sender_socket_location)

        
            
        