
class ConnectionDistributionCollection(dict):
        
    def add_connection_distribution(self, cd):
        if not cd.signature in self.keys():
            self[cd.signature] = cd