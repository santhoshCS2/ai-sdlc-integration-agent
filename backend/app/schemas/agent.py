from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class AgentBase(BaseModel):
    model_config = {"protected_namespaces": ()}
    
    name: str
    description: Optional[str] = None
    system_prompt: str
    model_version: str = "gpt-4"
    is_active: bool = True

class AgentCreate(AgentBase):
    model_config = {"protected_namespaces": ()}

class AgentUpdate(BaseModel):
    model_config = {"protected_namespaces": ()}
    
    name: Optional[str] = None
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    model_version: Optional[str] = None
    is_active: Optional[bool] = None

class Agent(AgentBase):
    model_config = {"protected_namespaces": (), "from_attributes": True}
    
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime
