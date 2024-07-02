import logging.config
from pathlib import Path

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


async def upload_docs(file_data: UploadFile = File(...)):

    """
    Uploads the document to Azure Blob Storage and Azure Search
    :param SAVED_FOLDER: The folder where the document is saved
    :param FILE_NAME: The name of the file to be uploaded
    :return: None

    
    """
   
    logging.basicConfig(level=logging.INFO)

    azure_blob_helper_datasource = AzureBlobHelper(AZ_ST_ACC_NAME,
                                                AZ_ST_ACC_KEY,
                                                AZ_ST_DATASOURCE_CONTAINER_NAME)
    queue_service = azure_queue_helper.AzureQueueService(AZURE_QUEUE_STORAGE_ACCOUNT,
                                                        AZURE_QUEUE_STORAGE_KEY,
                                                        AZURE_QUEUE_NAME)
    
    content = await file_data.read()
    file_name = file_data.filename
    azure_blob_helper_datasource.upload_blob(content, file_name)
    message = {"full_path": 
    f"https://{AZ_ST_ACC_NAME}.blob.core.windows.net/{AZ_ST_DATASOURCE_CONTAINER_NAME}/{file_name}",}

    # Convert the dictionary to a JSON string
    import json
    message_str = json.dumps(message)
    queue_service.send_message(message_str)

    logging.info(f"File {file_name} sent to queue for indexing.")


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

def search_docs(query):
    """
    Searches for documents in Azure Search
    :param query: The query to search for
    :return: The search results
    
    """

    search = CustomAzureSearch(AZURE_SEARCH_SERVICE_ENDPOINT,
                            AZURE_SEARCH_ADMIN_KEY,
                            AZURE_SEARCH_INDEX_NAME,
                            NUMBER_OF_RESULTS_TO_RETURN,
                            NUMBER_OF_NEAR_NEIGHBORS,
                            MODEL_NAME,
                            EMBEDDING_FIELD_NAME,
                            AZURE_SEARCH_SEMANTIC_CONFIG_NAME)
    results, \
                metadata_source_filename_to_return, \
                metadata_source_page_to_return, \
                    reranker_score =  search.get_results_semantic_search(query)
    
    context = "\n".join(results)
    reply = get_reply(query, context)

    URLs = []
    
    reranker_confidence = get_reranker_confidence(reranker_score)

    for page in metadata_source_page_to_return:
       URLs.append(azure_blob_helper.generate_sas_url(page))

    return reply,metadata_source_page_to_return,URLs,reranker_confidence

def get_reranker_confidence(reranker_score):
    """
    Get the confidence level of the reranker
    :param reranker_score: The score from the reranker
    :return: The confidence level
    
    """
    if reranker_score[0] < 2.6:
        reranker_confidence = "Low"
    elif reranker_score[0] < 3:
        reranker_confidence = "Medium"
    else:
        reranker_confidence = "High"
    return reranker_confidence

# Open the image file and encode it as a base64 string
def encode_image(data):
    return base64.b64encode(data).decode("utf-8")

def get_image_analysis(image_data):
    """
    Get image analysis from Azure Open AI
    :param image_data: The image data
    :return: The image analysis response
    
    """
    azure_open_ai_manager_4o = AzureOpenAIManager(
                    endpoint=AZURE_OPENAI_ENDPOINT,
                    api_key=AZURE_OPENAI_KEY,
                    deployment_id=AZURE_OPENAI_DEPLOYMENT_GPT_4O_ID,
                    api_version="2023-05-15"
                )

    prompt = "Provide all the form values"
    image_base64 = encode_image(image_data)
    response = azure_open_ai_manager_4o.get_image_analysis(prompt,image_base64)
    return response

def get_indexed_files():
    """
    Get the uploaded files to index
    :return: The uploaded files
    
    """

    cosmos_db_manager = CosmosDBManager(COSMOSDB_ENDPOINT, 
                                    COSMOSDB_KEY, 
                                    COSMOSDB_DATABASE_NAME, COSMOSDB_CONTAINER_NAME)




    query = "SELECT * FROM c WHERE c.processed = true"

    uploaded_files = cosmos_db_manager.read_items(query)

    li = []

    for row in uploaded_files:
        li.append(row["filename"])

    df_indexed_files = pd.DataFrame(li, columns=["filename"])
    return df_indexed_files
  