import sys
sys.path.append('..')

from api.upload import Upload
from fastapi import FastAPI, HTTPException
from orchestrator.manage_docs import upload_docs, _get_SQL_query, get_SQL_VARS
import logging
from fastapi import UploadFile, File

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

@app.post("/get_sql_results/")
async def get_sql_results(query: str):
    try:
        response =  _get_SQL_query(query)        
        return response
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail="Error in SQL query")

@app.post("/get_sql_vars/")
async def _get_sql_vars():

    server, database, username, password = get_SQL_VARS()
    return {"server": server, 
            "database": database, "username": username,
              "password": password}

    
    


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)