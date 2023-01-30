import re

class Selection:
    def __init__(self, query, collection_blacklist = ''):
        self.query = query
        self.collection_blacklist = re.compile(collection_blacklist)
    
    def is_blacklisted(coll_name):
        if self.collection_blacklist.match(coll_name) is None:
            return False
        
        return True
