from azure.cosmos import CosmosClient 
from azure.cosmos import PartitionKey

class CosmosDBManager:

    def __init__(self, endpoint, key, database_id = None, 
                 container_id = None):
        self.client = CosmosClient(endpoint, key)
        if database_id:
            self.database = self.client.get_database_client(database_id)
        else:
            self.database = None
        if container_id:
            self.container = self.database.get_container_client(container_id)
        else:
            self.container = None
        

    def create_item(self,item_to_create):        
        # populate the family items in container
        self.container.create_item(body=item_to_create) 

    def read_items(self, query):
        items = list(self.container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))
        return items
    
    
    def check_item(self, filename):
        
        query = f'SELECT * FROM c WHERE c.full_path = "{filename}"'
        items = self.read_items(query)
        if items:
            return True
        else:
            return False
    
    # Create a container
    # Using a good partition key improves the performance of database operations.
    # <create_container_if_not_exists>
    def get_or_create_container(self, container_name,
                                 partition_key_path="/filename"):
        return self.database.create_container(
            id=container_name,
            partition_key=PartitionKey(path = partition_key_path))
    # </create_container_if_not_exists>

    def escape_string(self, s):
        return s.replace("'", "''")