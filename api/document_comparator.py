from pydantic import BaseModel
from typing import List

class DocumentComparatorResponse(BaseModel):
    reply: str

class DocumentComparatorRequest(BaseModel):
    query: str
    files_list: List[str]