from config import *
from api.document_comparator import *
import os

from langchain_community.retrievers import AzureAISearchRetriever

from langchain.agents import AgentType, initialize_agent
from langchain.chains import RetrievalQA
from langchain_core.tools import Tool
from langchain_core.pydantic_v1 import BaseModel, Field

from langchain.chat_models import AzureChatOpenAI

import logging

logging.basicConfig(level=logging.INFO)

class DocumentInput(BaseModel):
    question: str = Field()

os.environ["AZURE_AI_SEARCH_SERVICE_NAME"] = AZURE_SEARCH_SERVICE_ENDPOINT
os.environ["AZURE_AI_SEARCH_INDEX_NAME"] = AZURE_SEARCH_INDEX_NAME
os.environ["AZURE_AI_SEARCH_API_KEY"] = AZURE_SEARCH_ADMIN_KEY
os.environ["AZURE_OPENAI_API_KEY"] =AZURE_OPENAI_KEY
os.environ["AZURE_OPENAI_ENDPOINT"] =AZURE_OPENAI_ENDPOINT
os.environ["OPENAI_API_VERSION"] = "2023-05-15"

def compare_documents(compare_request:DocumentComparatorRequest):
    files_list = compare_request.files_list
    action_input = compare_request.query

    tools = []
    llm = AzureChatOpenAI(azure_deployment=AZURE_OPENAI_DEPLOYMENT_GPT_4O_ID,
                        temperature=0)

    for file in files_list:
        file_name = file.split('.')[0]
        retriever = AzureAISearchRetriever(
        content_key="content", top_k=3, index_name=AZURE_SEARCH_INDEX_NAME,
        filter="sourcepage eq '{}'".format(file_name))
        
        tool = Tool(
        args_schema=DocumentInput,
                name=file_name,
                description=f"useful when you want to answer questions about {file_name}",
                func=RetrievalQA.from_chain_type(llm=llm, retriever=retriever),
            )
        tools.append(tool)

    agent = initialize_agent(
        agent=AgentType.OPENAI_FUNCTIONS,
        tools=tools,
        llm=llm,
        verbose=True,
    )
    action_input_prompt = "Compare and highlight the differences " + action_input + " in "
    for file in files_list:
        file_name = file.split('.')[0]
        action_input_prompt += file_name + ","   

    action_input_prompt += " Provide the answer in plain text only."
    
    logging.info("Action input prompt: " + action_input_prompt)
    results = agent({"input": action_input_prompt})

    print(results["output"])
    logging.info("Results: " + results["output"])

    return DocumentComparatorResponse(reply=results["output"])

