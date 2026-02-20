from typing import List
from promptlib.models.optimization import OptimizationResult, OptimizationSuggestion
from promptlib.models.prompt import Prompt

class AutomatedOptimizer:
    def optimize(self, prompt: Prompt) -> OptimizationResult:
        content = prompt.content
        suggestions = []
        optimized_content = content

        # 1. Structural Analysis (Check for common patterns)
        if "Role:" not in content and "You are a" not in content:
            suggestions.append(OptimizationSuggestion(
                category="structure",
                original="",
                suggested="You are an expert [role].",
                explanation="Assigning a persona/role often improves LLM performance."
            ))
            optimized_content = "You are an expert assistant.\n" + optimized_content

        # 2. Redundancy removal (Simple example: repeated words)
        import re
        if re.search(r'\b(\w+)\s+\1\b', content):
            suggestions.append(OptimizationSuggestion(
                category="efficiency",
                original="repeated words",
                suggested="remove duplicates",
                explanation="Redundant words waste tokens and can confuse the model."
            ))

        # 3. Token Efficiency (Check for long unnecessary phrases)
        if "Please provide a detailed response" in content:
            optimized_content = optimized_content.replace("Please provide a detailed response", "Be detailed.")
            suggestions.append(OptimizationSuggestion(
                category="efficiency",
                original="Please provide a detailed response",
                suggested="Be detailed.",
                explanation="Concise instructions are often more effective."
            ))

        # Calculate efficiency score
        original_len = len(content)
        optimized_len = len(optimized_content)
        efficiency_score = min(1.0, optimized_len / max(1, original_len))

        return OptimizationResult(
            prompt_id=str(prompt.id),
            original_content=content,
            optimized_content=optimized_content,
            suggestions=suggestions,
            token_reduction=max(0, original_len - optimized_len),
            efficiency_score=efficiency_score
        )
