from typing import List, Optional
from pydantic import BaseModel

class OptimizationSuggestion(BaseModel):
    category: str # clarity, efficiency, structure
    original: str
    suggested: str
    explanation: str

class OptimizationResult(BaseModel):
    prompt_id: str
    original_content: str
    optimized_content: str
    suggestions: List[OptimizationSuggestion]
    token_reduction: Optional[int] = None
    efficiency_score: float # 0.0 to 1.0
