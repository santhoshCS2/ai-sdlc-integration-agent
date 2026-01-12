from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class MessageBase(BaseModel):
    content: str
    sender_type: str  # 'user' or 'agent'

class MessageCreate(MessageBase):
    conversation_id: int
    token_count: Optional[int] = 0

class Message(MessageBase):
    id: int
    conversation_id: int
    token_count: int
    timestamp: datetime

    class Config:
        from_attributes = True

class ConversationBase(BaseModel):
    agent_id: int

class ConversationCreate(ConversationBase):
    user_id: int

class Conversation(ConversationBase):
    id: int
    user_id: int
    started_at: datetime
    last_message_at: datetime
    messages: List[Message] = []

    class Config:
        from_attributes = True
