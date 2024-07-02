import sys
sys.path.append('..')

from api.upload import Upload
from fastapi import FastAPI, HTTPException
from orchestrator.manage_docs import upload_docs
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)