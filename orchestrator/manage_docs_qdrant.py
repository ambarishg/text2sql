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

def get_reply(user_input, content):

    azure_open_ai_manager = AzureOpenAIManager(
                    endpoint=AZURE_OPENAI_ENDPOINT,
                    api_key=AZURE_OPENAI_KEY,
                    deployment_id=AZURE_OPENAI_DEPLOYMENT_ID,
                    api_version="2023-05-15"
                )
    
    conversation=[{"role": "system", "content": "If the answer is not found within the context, please mention \
        that the answer is not found \
        Do not answer anything which is not in the context"}]
    reply = azure_open_ai_manager.generate_reply_from_context(user_input, content, conversation)
    return reply


def search_docs_qdrant(query):
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
    reply = get_reply(query, context)

    URLs = []
    
    reranker_confidence = ""

    for page in metadata_source_page_to_return:
       URLs.append(azure_blob_helper.generate_sas_url(page))


    return ChatResponse(reply=reply[0], 
    metadata_source_page_to_return=metadata_source_page_to_return,
    URLs=URLs, reranker_confidence=reranker_confidence)
