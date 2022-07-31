import logging
import azure.cosmos.exceptions as db_exceptions
from azure.cosmos.cosmos_client import CosmosClient
from azure.cosmos.partition_key import PartitionKey
from os import getenv

DATABASE_ID = getenv("COSMOS_DATABASE_ID")

"""
    Class that retrieves database connection and operations
"""
class DatabaseConnection:

    # TODO: Make it a functional singleton class
    db = None
    
    def __init__(self):
        
        if (self.db == None):
            self.get_db_instance()

    def get_db_instance(self):
        client = CosmosClient(
            getenv("COSMOS_DATABASE_HOST"),
            {'masterKey': getenv("COSMOS_ACCOUNT_KEY")},
            user_agent='GetMySecretApiFunction')

        try:
            # te
            self.db = client.create_database_if_not_exists(DATABASE_ID)
        except db_exceptions.CosmosHttpResponseError as http_r_err:
            logging.error("Failed to connect to database: {0}".format(http_r_err))

    
    def create_item(self, container_id: str, content_body: any):
        container = self.db.get_container_client(container_id)
        response = container.create_item(body=content_body)
        return response
    
    def get_item_by_id(self, container_id, item_id):
        
        response = None
        
        try:
            container = self.db.get_container_client(container_id)
            response = container.read_item(item=item_id, partition_key=item_id)
        except db_exceptions.CosmosResourceNotFoundError as not_found_err:
            logging.info(
                'Searched "{0}" resource not found on {1} container.'.format(
                    item_id, container_id))
        
        return response
    
    def list_items(self, container_id):
        container = self.db.get_container_client(container_id)
        response = list(container.read_all_items(max_item_count=10)) # symbolic value...
        return response
    
    def replace_item(self, container_id, item):
        
        response = None

        try:
            container = self.db.get_container_client(container_id)
            item = container.replace_item(item=item, body=item)

        except db_exceptions.CosmosResourceNotFoundError as not_found_err:
            logging.info(
                'Searched "{0}" resource not found on {1} container.'.format(
                    item['id'], container_id))

        return response
    
    def delete_item(self, container_id, item_id):
        container = self.db.get_container_client(container_id)
        response = container.delete_item(body=item_id)
        return response
    
    def query(self, container_id, query_text, params):
        container = self.db.get_container_client(container_id)
        response = container.query_items(query=query_text, parameters=params, enable_cross_partition_query=True)
        return response

