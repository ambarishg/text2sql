from pydantic import BaseModel
from typing import List, Dict


class ConversationHeaders(BaseModel):
    conversation_header: List[Dict[str, str]]


class ConversationHistory(BaseModel):
    conversation_history: List[Dict[str, str, str,str]]
