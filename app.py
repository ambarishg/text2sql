import sys
sys.path.append('..')
from config import *

from fastapi import FastAPI, HTTPException
from orchestrator.manage_docs import upload_docs, _get_SQL_query, \
    get_SQL_VARS, search_docs, get_image_analysis, get_indexed_files

import logging
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from orchestrator.manage_docs import \
upload_docs, _get_SQL_query, get_SQL_VARS, search_docs, \
get_image_analysis, get_indexed_files,get_simple_image_analysis
from api.chat import SQLRequest
from api.document_comparator import DocumentComparatorRequest
from orchestrator.document_comparator import compare_documents
from msal import ConfidentialClientApplication
import os
import json
from six.moves.urllib.request import urlopen
from functools import wraps
from jose import jwt
import requests
from orchestrator.manage_docs import get_recent_conversations
from api.conversation import ConversationHeaders, ConversationHistory
from orchestrator.manage_docs_qdrant import *

app = FastAPI()

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def get_current_user(request: Request):
    token = request.headers.get("Authorization")
    print(token)
    if not token:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    token = token.replace("Bearer ", "")
    jsonurl = urlopen("https://login.microsoftonline.com/" +
                    TENANT_ID + "/discovery/v2.0/keys")
    jwks = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)
    unverified_claims = jwt.get_unverified_claims(token)
    issuer = unverified_claims.get("iss")
    audience = unverified_claims.get("aud")
    rsa_key = {}
    for key in jwks["keys"]:
        if key["kid"] == unverified_header["kid"]:
            rsa_key = {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"]
            }
            break
    if rsa_key:
        try:
            payload = jwt.decode(token, 
                                rsa_key, 
                                algorithms=["RS256"], 
                                audience=audience, issuer=issuer)
            print("Signature verified")
            print(payload["given_name"])
        except jwt.ExpiredSignatureError:
            print("Token is expired")
        except jwt.JWTClaimsError:
            print("Incorrect claims, please check the audience and issuer")
        except jwt.JWTError as e:
            print("Error decoding token")
            print(e)
        
    return token
    


@app.post("/upload_docs/")
async def _upload_docs(file: UploadFile = File(...), user=Depends(get_current_user)):
    await upload_docs(file)

@app.post("/get_image_analysis/")
async def _get_image_analysis(file: UploadFile = File(...), 
                              ):
    try:
        
        response = await get_image_analysis(file)
        return response
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail="Error in image analysis")
    

@app.post("/get-simple-image-analysis/")
async def _get_simple_image_analysis(file: UploadFile = File(...), 
                              ):
    try:
        
        response = await get_simple_image_analysis(file)
        return response
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail="Error in image analysis")

@app.post("/get_sql_results/")
async def get_sql_results(query: SQLRequest, user=Depends(get_current_user)):
    try:
        query = query.query
        response = _get_SQL_query(query)
        return response
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=e.__traceback__)

@app.post("/get_sql_vars/")
async def _get_sql_vars(user=Depends(get_current_user)):
    server, database, username, password = get_SQL_VARS()
    return {"server": server, "database": database, "username": username, "password": password}

@app.post("/get_answer_from_question/")
async def get_answer_from_question(user_input: SQLRequest, user=Depends(get_current_user)):
    try:
        token = user
        if VECTOR_DB == "AZURE_SEARCH":
            response = search_docs(user_input.query, token , user_input.conversation_id)
        elif VECTOR_DB == "QDRANT":
            response =  search_docs_qdrant(user_input.query,token , user_input.conversation_id)
        return response
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail="Error in search")

@app.post("/get_files_indexed/")
async def _get_files_indexed(user=Depends(get_current_user)):
    try:
        logging.info(f"user: {user}")
        response = get_indexed_files()
        return response
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail="Error in search")

@app.post("/compare_docs/")
async def _compare_documents(user_input: DocumentComparatorRequest, user=Depends(get_current_user)):
    try:
        response = compare_documents(user_input)
        return response
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail="Error in Compare Documents")
    
@app.post("/get_conversation_headers/")
async def get_conversation_headers():
    try:
        response = get_recent_conversations(user =Depends(get_current_user) )
        return response
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail="Error in Get Conversation Headers")

@app.get("/hello/")
async def hello():
    try:
        response = {"message": "Hello"}
        return response
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail="Error in Hello")
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
