from unittest import mock 

class QueryResponse(object):
   
    def __init__(self,total_bytes_processed):
        self.total_bytes_processed = total_bytes_processed

class ClientMock(object):
    
    ### Query is the totalbytes  processed!
    def query(self,query,job_config):
        return QueryResponse(int(query))

class QueryJobConfig(object):

    def __init__(self,dry_run=True, use_query_cache=False):
        pass

class DisplayHolder(object):
    display_array = []


def displyMocker(displayHolder):
    def getDisplay(message):
        displayHolder.display_array.append(message)
    return getDisplay