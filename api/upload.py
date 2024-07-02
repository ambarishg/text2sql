from pydantic import BaseModel
from typing import Dict
from typing import List
from fastapi import UploadFile, File

class Upload(BaseModel):
    file_data: UploadFile = File(...)



