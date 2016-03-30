import json
import pymongo.errors
import pymongo.collection
import logging
import time
from pymongo import MongoClient, CursorType
logger = logging.getLogger(__name__)

logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

mongo_config_dict = {'mongodb_ip':'localhost',
                     'mongodb_port':27017,
                     'database_name':'example',
                     'collection_name':'example'}

class MongoDistributedConfiguration(object):
    
    def __init__(self, rank, number_of_processes=1, gid_to_rank=None):
        self._rank = rank
        self.number_of_processes = number_of_processes
        self.client = MongoClient(mongo_config_dict['mongodb_ip'], mongo_config_dict['mongodb_port'])
        if self.rank() == 0:
            self.client.drop_database(mongo_config_dict['database_name'])
        self.db = self.client[mongo_config_dict['database_name']]
        self.outside_rank_list = [ii for ii in range(self.number_of_processes) if ii != self.rank()]
        
        if gid_to_rank is None:
            def gid_to_rank(gid):
                return gid%self.number_of_processes
        self.gid_to_rank = gid_to_rank
        
        self.received_message_dict_external = {curr_rank:{} for curr_rank in self.outside_rank_list}
        while len(self.db.collection_names()) > 0:
            time.sleep(.001)
            
        self.synchronization_harness = self
    
    def rank(self):
        return self._rank
    
    def initialize(self, ii=0):
        pass
#             print self.rank(), 'hi'
    
    
#     self.received_message_dict_external[int(curr_source_rank)][int(curr_ii)] = json.loads(received_payload)
    
    def update(self, ii, data_to_send):
        
        # Access collection corresponding to the current time-step:
        collection_name = '%s' % ii
        try:
            collection = self.db.create_collection(collection_name, **{'capped':True, 'size':100000})
        except (pymongo.errors.OperationFailure, pymongo.errors.CollectionInvalid):
            collection = self.db[collection_name]

        # Push my data:
        collection.insert({"rank":self.rank(), 'data':json.dumps(data_to_send)})
        
        #Get data:
        max_record = len(self.outside_rank_list)
        cursor = collection.find({'rank':{"$in":self.outside_rank_list}}, cursor_type=CursorType.TAILABLE_AWAIT)
        result_dict = {}
        while len(result_dict) < max_record:
            try:
                found_document = cursor.next()
                result_dict[found_document['rank']] = found_document['data']
            except StopIteration:
                pass
        
        for source_rank, payload in result_dict.items():
            self.received_message_dict_external[source_rank][ii] = json.loads(payload)

          
        
#         logger.debug('Rank %s: %s, %s' % (self.rank(), ii, self.db.collection_names()))

    
    def finalize(self):
        pass
#         print 'here'
#         if self.rank == 0:
#             self.client.drop_database(mongo_config_dict['database_name'])
    

#         collection = self.db['%s' % ii]
#         
#         # Push data:
#         collection.insert({"%s" % self.rank:data_to_send})
#         
#         # Pull data:
#         print collection