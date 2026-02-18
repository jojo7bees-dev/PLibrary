from typing import List, Dict, Any
from promptlib.models.prompt import Prompt
import difflib

class LinterResult:
    def __init__(self, message: str, level: str = "info", suggestion: str = None):
        self.message = message
        self.level = level # info, warning, error
        self.suggestion = suggestion

    def __repr__(self):
        return f"[{self.level.upper()}] {self.message} (Suggestion: {self.suggestion})"

class PromptLinter:
    def lint(self, prompt: Prompt, other_prompts: List[Prompt] = None) -> List[LinterResult]:
        results = []

        # 1. Structure analysis
        if not prompt.description:
            results.append(LinterResult("Prompt missing description", "info", "Add a description to help others understand this prompt."))

        if len(prompt.content) < 10:
            results.append(LinterResult("Prompt content is very short", "warning", "Short prompts might be too vague."))

        # 2. Duplicate detection
        if other_prompts:
            for other in other_prompts:
                if other.id == prompt.id:
                    continue
                similarity = difflib.SequenceMatcher(None, prompt.content, other.content).ratio()
                if similarity > 0.9:
                    results.append(LinterResult(f"Highly similar to existing prompt: {other.name}", "warning", "Consider merging or differentiating."))

        # 3. Variable analysis
        if "{{" in prompt.content and not prompt.variables:
             results.append(LinterResult("Potential unextracted variables", "warning", "Content contains '{{' but no variables are defined."))

        return results
