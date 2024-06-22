import os
from dotenv import load_dotenv
from dotenv import dotenv_values

load_dotenv()
values_env = dotenv_values("../.env")


server = values_env["SERVER"]
database = values_env["DATABASE"]
username = values_env["USERNAME"]
password = values_env["PASSWORD"]

AZURE_OPENAI_ENDPOINT = values_env["AZURE_OPENAI_ENDPOINT"]
AZURE_OPENAI_KEY = values_env["AZURE_OPENAI_API_KEY"]
AZURE_OPENAI_DEPLOYMENT_ID = values_env["AZURE_OPENAI_DEPLOYMENT_ID"]

AZ_ST_ACC_NAME = values_env["AZ_ST_ACC_NAME"]
AZ_ST_ACC_KEY = values_env["AZ_ST_ACC_KEY"]
AZ_ST_CONTAINER_NAME = values_env["AZ_ST_CONTAINER_NAME"]

AZURE_SEARCH_SERVICE_ENDPOINT=values_env["AZURE_SEARCH_SERVICE_ENDPOINT"]
AZURE_SEARCH_INDEX_NAME=values_env["AZURE_SEARCH_INDEX_NAME"]
AZURE_SEARCH_ADMIN_KEY=values_env["AZURE_SEARCH_ADMIN_KEY"]
AZURE_SEARCH_SEMANTIC_CONFIG_NAME=values_env["AZURE_SEARCH_SEMANTIC_CONFIG_NAME"]
MODEL_NAME = values_env["MODEL_NAME"]
NUMBER_OF_RESULTS_TO_RETURN=values_env["NUMBER_OF_RESULTS_TO_RETURN"]
NUMBER_OF_NEAR_NEIGHBORS=values_env["NUMBER_OF_NEAR_NEIGHBORS"]
EMBEDDING_FIELD_NAME=values_env["EMBEDDING_FIELD_NAME"]




