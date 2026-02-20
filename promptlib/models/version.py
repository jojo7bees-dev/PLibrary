from datetime import datetime
from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from typing import Optional

class PromptVersion(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    prompt_id: UUID
    version: str
    content: str
    checksum: str
    created_at: datetime = Field(default_factory=datetime.now)
    author: Optional[str] = None
    change_log: Optional[str] = None
