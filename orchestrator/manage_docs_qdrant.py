import logging.config
from pathlib import Path

from qdrant.qdrant_helper import QdrantHelper
from azure_blob.azure_blob_helper import AzureBlobHelper
from azure_blob.read_pdf import PDFHelper
from config import *
from azure_ai_search.azure_ai_vector_search import CustomAzureSearch
from azureopenaimanager.azureopenai_helper import AzureOpenAIManager
import base64
from azurequeues import azure_queue_helper
import logging
from cosmos.cosmosdbmanager import CosmosDBManager
import pandas as pd
from fastapi import UploadFile, File
from sqlmanager.azuresqlmanager import AzureSQLManager

from pydantic import BaseModel
from typing import Dict, Any, List

from api.chat import ChatResponse
from api.getFiles import FilesResponse

import io

def get_reply(user_input, content, token = None, conversation_id = None):

    
    cosmosdb_helper = CosmosDBManager(COSMOSDB_ENDPOINT,    
                                    COSMOSDB_KEY, 
                                    COSMOSDB_DATABASE_NAME, 
                                    COSMOSDB_CONTAINER_NAME_CONVERSATIONS)
    
    azure_open_ai_manager = AzureOpenAIManager(
                    endpoint=AZURE_OPENAI_ENDPOINT,
                    api_key=AZURE_OPENAI_KEY,
                    deployment_id=AZURE_OPENAI_DEPLOYMENT_ID,
                    api_version="2023-05-15",
                    cosmosdb_helper = cosmosdb_helper,
                    token = token
                )             
    
    conversation=[{"role": "system", "content": "If the answer is not found within the context, please mention \
        that the answer is not found \
        Do not answer anything which is not in the context"}]
    reply,conversation_id = azure_open_ai_manager.generate_reply_from_context(user_input, 
                        content,conversation, conversation_id)
    return reply,conversation_id


def search_docs_qdrant(query,token = None, conversation_id = None):
    """
    Searches for documents in Azure Search
    :param query: The query to search for
    :return: The search results
    
    """

    search = QdrantHelper(QDRANT_URL,QDRANT_KEY,MODEL_NAME,QDRANT_COLLECTION)
    
    azure_blob_helper = AzureBlobHelper(AZ_ST_ACC_NAME,
                                    AZ_ST_ACC_KEY,
                                    AZ_ST_CONTAINER_NAME)
    results, \
    metadata_source_filename_to_return, \
    metadata_source_page_to_return, \
    reranker_score =  search.get_search_results(query)
    
    context = "\n".join(results)
    reply,conversation_id = get_reply(query, context,token=token, conversation_id=conversation_id)

    

    URLs = []
    
    reranker_confidence = " "

    for page in metadata_source_page_to_return:
       URLs.append(azure_blob_helper.generate_sas_url(page))

    print(f"reply = {reply[0]}")
    print(f"metadata_source_page_to_return = {metadata_source_page_to_return}")
    print(f"URLs = {URLs}")
    print(f"reranker_confidence = {reranker_confidence}")
    return ChatResponse(reply=reply[0], 
    metadata_source_page_to_return=metadata_source_page_to_return,
    URLs=URLs, reranker_confidence=reranker_confidence,
    conversation_id=conversation_id,
    search_results=results)
