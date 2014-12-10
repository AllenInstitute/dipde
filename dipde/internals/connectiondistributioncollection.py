
class ConnectionDistributionCollection(object):
    
    def __init__(self):
        self.connection_distribution_dict = {}
        
    def add_connection_distribution(self, cd):
        if not cd.signature in self.connection_distribution_dict.keys():
            self.connection_distribution_dict[cd.signature] = cd
            if not cd.initialized:
                cd.initialize()