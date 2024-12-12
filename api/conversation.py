from pydantic import BaseModel
from typing import List, Dict


class ConversationHeaderItem(BaseModel):
    conversation_id: str
    short_name: str

class ConversationHeaders(BaseModel):
    conversationsHeaders: List[ConversationHeaderItem]

class ConversationHistoryItem(BaseModel):
    conversation_id: str
    role: str
    message: str

class ConversationHistory(BaseModel):
    conversationHistory: List[ConversationHistoryItem]

