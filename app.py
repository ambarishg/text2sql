import sys
sys.path.append('..')


from fastapi import FastAPI, HTTPException
from orchestrator.manage_docs import upload_docs, _get_SQL_query, \
    get_SQL_VARS, search_docs, get_image_analysis, get_indexed_files
import logging
from fastapi import UploadFile, File
from api.chat import SQLRequest
from api.document_comparator import *
from orchestrator.document_comparator import compare_documents


app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload_docs/")
async def _upload_docs(file: UploadFile = File(...),):
    await upload_docs(file)

@app.post("/get_image_analysis/")
async def _get_image_analysis(file: UploadFile = File(...)):
    try:
        response =  await get_image_analysis(file)
        return response
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail="Error in image analysis")

@app.post("/get_sql_results/")
async def get_sql_results(query: SQLRequest):
    try:
        query = query.query
        response =  _get_SQL_query(query)        
        return response
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=e.__traceback__)

@app.post("/get_sql_vars/")
async def _get_sql_vars():

    server, database, username, password = get_SQL_VARS()
    return {"server": server, 
            "database": database, "username": username,
              "password": password}

@app.post("/get_answer_from_question/")
async def get_answer_from_question(user_input: SQLRequest):
    try:
        response =  search_docs(user_input.query)
        return response
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail="Error in search")

@app.post("/get_files_indexed/")
async def _get_files_indexed():
    try:
        response =  get_indexed_files()
        return response
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail="Error in search")
    
@app.post("/compare_docs/")
async def _compare_documents(user_input: DocumentComparatorRequest):
    try:
        response =  compare_documents(user_input)
        return response
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail="Error in Compare Documents")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)