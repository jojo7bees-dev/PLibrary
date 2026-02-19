from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from pydantic import BaseModel, Field

class AgentCapability(BaseModel):
    name: str
    description: Optional[str] = None

class Agent(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    role: str # executor, optimizer, analyzer, workflow
    capabilities: List[AgentCapability] = Field(default_factory=list)
    assigned_prompts: List[UUID] = Field(default_factory=list)
    execution_history: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
