from pydantic import BaseModel
from typing import List

class FilesResponse(BaseModel):
    file_list: List[str]
    category_list: List[str]
    status_list: List[str]

class CategoryUserRequest(BaseModel):
    user_id:str
