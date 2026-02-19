from typing import List, Dict, Any, Optional, Union
from uuid import UUID, uuid4
from pydantic import BaseModel, Field

class WorkflowCondition(BaseModel):
    variable: str
    operator: str # eq, neq, contains, etc.
    value: Any

class WorkflowStep(BaseModel):
    id: str
    prompt_id: Optional[UUID] = None
    agent_id: Optional[UUID] = None
    input_mapping: Dict[str, str] = Field(default_factory=dict)
    output_key: Optional[str] = None
    condition: Optional[WorkflowCondition] = None
    next_step_id: Optional[str] = None # For linear/branching
    on_true: Optional[str] = None
    on_false: Optional[str] = None

class Workflow(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    description: Optional[str] = None
    start_step_id: str
    steps: Dict[str, WorkflowStep] = Field(default_factory=dict) # Map ID to step
    metadata: Dict[str, Any] = Field(default_factory=dict)
