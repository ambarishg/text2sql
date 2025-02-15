from pydantic import BaseModel
from typing import List

class ChatResponse(BaseModel):
    reply: str
    metadata_source_page_to_return: List[str]
    URLs: List[str]
    reranker_confidence: str
    conversation_id: str
    search_results: List[str]

class SQLRequest(BaseModel):
    query: str
    conversation_id: str
    category: str
    user_id: str