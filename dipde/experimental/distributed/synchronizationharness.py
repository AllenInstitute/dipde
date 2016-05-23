import zmq
import json
import logging

context = zmq.Context()

class SynchronizationHarness(object):
    
    def __init__(self, rank, address_config_dict, number_of_processes, gid_to_rank=None):
        
        self.rank = rank
        self.address_config_dict = address_config_dict
        self.number_of_processes = number_of_processes
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
            
        if gid_to_rank is None:
            def gid_to_rank(gid):
                return gid%self.number_of_processes
        self.gid_to_rank = gid_to_rank
            
    def initialize(self, ii=0):
        self.ii0=ii
        self.logger.debug('Rank %s: Initialized' % (self.rank, ))
        
    def update(self, ii, data_to_send):
        self.logger.debug('Rank %s(%s): Updating step' % (self.rank, ii))
        outgoing_payload = json.dumps(data_to_send)
        
        # Send to all other nodes, not blocking:
        for curr_rank in self.outside_rank_list:
            socket = self.sender_socket_dict[curr_rank]
            self.logger.debug('Rank %s(%s): Sending  payload to   %s(%s), %s' % (self.rank, ii, curr_rank, ii, outgoing_payload))
            socket.send_multipart([b'%s' % self.rank, b'%s' % ii, b'%s' % outgoing_payload])
        
        # Wait to hear from other nodes, blocking:
        received_message_dict = {}
        while len([True for key in received_message_dict.keys() if ii == key[1]]) < len(self.sender_socket_dict):
            curr_source_rank, curr_ii, received_payload = self.receiver_socket.recv_multipart()
            received_message_dict[(int(curr_source_rank), int(curr_ii))] = json.loads(received_payload) 
            self.logger.debug('Rank %s(%s): Received payload from %s(%s), %s' % (self.rank, ii, curr_source_rank, curr_ii, outgoing_payload))
        self.logger.debug('Rank %s(%s): completed' % (self.rank, ii))

        # Load results into organizer:
        for key, payload_dict in received_message_dict.items():
            _, ti = key
            for gid, firing_rate in payload_dict.items():
                if not ti in self.firing_rate_organizer.firing_rate_dict_internal:
                    print 'Hiccup'
                self.firing_rate_organizer.firing_rate_dict_internal.setdefault(ti, {})[int(gid)] = firing_rate
        
    def finalize(self):
        self.logger.debug('Rank %s: Disconnecting' % (self.rank,))
        self.receiver_socket.unbind(self.receiver_socket_location)
        for curr_rank in self.outside_rank_list:
            sender_socket_location = self.sender_socket_location_dict[curr_rank]
            sender_socket = self.sender_socket_dict[curr_rank]
            sender_socket.disconnect(sender_socket_location)

        
            
        