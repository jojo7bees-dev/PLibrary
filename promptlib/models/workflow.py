from typing import List, Dict, Any, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field

class WorkflowStep(BaseModel):
    id: str
    prompt_id: UUID
    input_mapping: Dict[str, str] = Field(default_factory=dict) # maps workflow variables to prompt variables
    output_key: Optional[str] = None # where to store the result in workflow context

class Workflow(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    description: Optional[str] = None
    steps: List[WorkflowStep] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
