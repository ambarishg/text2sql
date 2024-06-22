from pathlib import Path

from azure_blob.azure_blob_helper import AzureBlobHelper
from azure_blob.read_pdf import PDFHelper
from config import *
from azure_ai_search.azure_ai_vector_search import CustomAzureSearch
from azureopenaimanager.azureopenai_helper import AzureOpenAIManager

search = CustomAzureSearch(AZURE_SEARCH_SERVICE_ENDPOINT,
                            AZURE_SEARCH_ADMIN_KEY,
                            AZURE_SEARCH_INDEX_NAME,
                            NUMBER_OF_RESULTS_TO_RETURN,
                            NUMBER_OF_NEAR_NEIGHBORS,
                            MODEL_NAME,
                            EMBEDDING_FIELD_NAME,
                            AZURE_SEARCH_SEMANTIC_CONFIG_NAME)

azure_blob_helper = AzureBlobHelper(AZ_ST_ACC_NAME, 
                                    AZ_ST_ACC_KEY, 
                                    AZ_ST_CONTAINER_NAME)

azure_open_ai_manager = AzureOpenAIManager(
                    endpoint=AZURE_OPENAI_ENDPOINT,
                    api_key=AZURE_OPENAI_KEY,
                    deployment_id=AZURE_OPENAI_DEPLOYMENT_ID,
                    api_version="2023-05-15"
                )


def upload_docs(SAVED_FOLDER, FILE_NAME):

    """
    Uploads the document to Azure Blob Storage and Azure Search
    :param SAVED_FOLDER: The folder where the document is saved
    :param FILE_NAME: The name of the file to be uploaded
    :return: None

    
    """
   
    save_path = Path(SAVED_FOLDER, FILE_NAME)
    
    file_name = FILE_NAME
    full_path = os.path.join(SAVED_FOLDER, FILE_NAME)
    pdf_helper = PDFHelper(full_path,
                            azure_blob_helper)
    pdf_helper.write_pdf()
    page_map = pdf_helper.get_document_text(full_path)
    sections = pdf_helper.create_sections(file_name, page_map)
    batch = []
    for section in sections:
        section_embeddings = search.get_embedding_query_vector(section['content'])
        section[EMBEDDING_FIELD_NAME] = section_embeddings.tolist()
        batch.append(section)  
    search.upload_documents(batch)

def get_reply(user_input, content):
    conversation=[{"role": "system", "content": "Assistant is a great language model formed by OpenAI."}]
    reply = azure_open_ai_manager.generate_reply_from_context(user_input, content, conversation)
    return reply

def search_docs(query):
    """
    Searches for documents in Azure Search
    :param query: The query to search for
    :return: The search results
    
    """
    results, \
                metadata_source_filename_to_return, \
                metadata_source_page_to_return =  search.get_results_semantic_search(query)
    
    context = "\n".join(results)
    reply = get_reply(query, context)

    URLs = []

    for page in metadata_source_page_to_return:
       URLs.append(azure_blob_helper.generate_sas_url(page))

    return reply,metadata_source_page_to_return,URLs