from cosmos.cosmosdbmanager import CosmosDBManager
from config import *
from file_load_status_helper.interface_load_status_helper import *
import uuid

class CosmosDBLoadStatusHelper(ILoadStatusHelper):
    def __init__(self):
        self.cosmos_db_helper = CosmosDBManager(COSMOSDB_ENDPOINT,
                                    COSMOSDB_KEY,
                                    COSMOSDB_DATABASE_NAME,
                                    COSMOSDB_CONTAINER_NAME)

    def get_file_load_status(self,filename,user_id,category):

        query = f'SELECT * FROM c WHERE c.filename = "{filename}" AND c.user_id = "{user_id}" AND c.category = "{category}"'    
        items = self.cosmos_db_helper.read_items(query)

        return items

    def set_file_load_status(self, item_to_create):
        items = self.get_file_load_status(item_to_create["filename"],item_to_create["user_id"],item_to_create["category"])
        
        print(f"items : {items}")
        if items is None :
            item_to_create["id"] = str(uuid.uuid4())
            self.cosmos_db_helper.create_item(item_to_create)
        elif len(items) == 0:
            item_to_create["id"] = str(uuid.uuid4())
            self.cosmos_db_helper.create_item(item_to_create)
        else:
            id = items[0]["id"]
            item_to_replace = items[0]
            item_to_replace["status"] = item_to_create["status"]

            print(f"Updating item with id {item_to_create}")

            self.cosmos_db_helper.container.replace_item(id, item_to_replace)


        
        