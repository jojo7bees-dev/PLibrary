from datetime import datetime
from typing import List, Dict, Any, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, ConfigDict
from promptlib.models.variable import VariableDefinition

class Prompt(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(default_factory=uuid4)
    name: str
    description: Optional[str] = None
    content: str
    variables: List[str] = Field(default_factory=list) # List of names extracted from content
    variable_definitions: List[VariableDefinition] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    category: Optional[str] = None
    version: str = "1.0.0"
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    usage_count: int = 0
    last_used: Optional[datetime] = None
    author: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    checksum: Optional[str] = None
    hash_signature: Optional[str] = None
