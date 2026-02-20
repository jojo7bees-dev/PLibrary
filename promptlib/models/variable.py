from typing import Any, Optional
from pydantic import BaseModel

class VariableDefinition(BaseModel):
    name: str
    description: Optional[str] = None
    default_value: Optional[Any] = None
    required: bool = True
    validation_regex: Optional[str] = None
    type: str = "string" # e.g., string, number, boolean
