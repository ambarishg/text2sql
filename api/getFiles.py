from pydantic import BaseModel
from typing import List

class FilesResponse(BaseModel):
    file_list: List[str]
