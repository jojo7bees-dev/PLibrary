import hashlib
import difflib
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from promptlib.models.prompt import Prompt
from promptlib.models.version import PromptVersion
from promptlib.storage.base import BaseRepository
from promptlib.services.rendering import RenderingService
from promptlib.utils.linter import PromptLinter, LinterResult
from promptlib.core.exceptions import PromptNotFoundError, ValidationError

class PromptService:
    def __init__(self, repository: BaseRepository, rendering_service: RenderingService, linter: PromptLinter = None):
        self.repository = repository
        self.rendering_service = rendering_service
        self.linter = linter or PromptLinter()

    def _calculate_checksum(self, content: str) -> str:
        return hashlib.sha256(content.encode()).hexdigest()

    def create_prompt(self, name: str, content: str, **kwargs) -> Prompt:
        checksum = self._calculate_checksum(content)
        variables = self.rendering_service.extract_variables(content)

        prompt = Prompt(
            name=name,
            content=content,
            checksum=checksum,
            variables=variables,
            **kwargs
        )
        self.repository.save(prompt)

        # Save initial version
        version = PromptVersion(
            prompt_id=prompt.id,
            version=prompt.version,
            content=prompt.content,
            checksum=checksum,
            change_log="Initial version"
        )
        self.repository.save_version(version)

        return prompt

    def update_prompt(self, prompt_id: UUID, content: Optional[str] = None, **kwargs) -> Prompt:
        prompt = self.repository.get_by_id(prompt_id)
        if not prompt:
            raise PromptNotFoundError(f"Prompt {prompt_id} not found")

        content_changed = False
        if content is not None and content != prompt.content:
            prompt.content = content
            prompt.checksum = self._calculate_checksum(content)
            prompt.variables = self.rendering_service.extract_variables(content)
            content_changed = True

        for key, value in kwargs.items():
            if hasattr(prompt, key):
                setattr(prompt, key, value)

        prompt.updated_at = datetime.now()

        if content_changed:
            # Increment version
            v_parts = prompt.version.split('.')
            v_parts[-1] = str(int(v_parts[-1]) + 1)
            prompt.version = ".".join(v_parts)

            # Save new version
            version = PromptVersion(
                prompt_id=prompt.id,
                version=prompt.version,
                content=prompt.content,
                checksum=prompt.checksum,
                change_log=kwargs.get("change_log", "Content update")
            )
            self.repository.save_version(version)

        self.repository.save(prompt)
        return prompt

    def render_prompt(self, prompt_id: UUID, variables: Dict[str, Any]) -> str:
        prompt = self.repository.get_by_id(prompt_id)
        if not prompt:
            raise PromptNotFoundError(f"Prompt {prompt_id} not found")

        final_vars = self.rendering_service.validate_variables(
            prompt.content,
            variables,
            getattr(prompt, "variable_definitions", [])
        )
        rendered = self.rendering_service.render(prompt.content, final_vars)

        self.repository.update_usage(prompt_id)
        return rendered

    def get_prompt(self, prompt_id: UUID) -> Prompt:
        prompt = self.repository.get_by_id(prompt_id)
        if not prompt:
            raise PromptNotFoundError(f"Prompt {prompt_id} not found")
        return prompt

    def list_prompts(self, category: Optional[str] = None, tags: Optional[List[str]] = None) -> List[Prompt]:
        return self.repository.list_all(category, tags)

    def search_prompts(self, query: str) -> List[Prompt]:
        return self.repository.search(query)

    def delete_prompt(self, prompt_id: UUID) -> None:
        self.repository.delete(prompt_id)

    def get_versions(self, prompt_id: UUID) -> List[PromptVersion]:
        return self.repository.get_versions(prompt_id)

    def rollback(self, prompt_id: UUID, version_str: str) -> Prompt:
        versions = self.repository.get_versions(prompt_id)
        target_version = next((v for v in versions if v.version == version_str), None)
        if not target_version:
            raise ValidationError(f"Version {version_str} not found for prompt {prompt_id}")

        return self.update_prompt(prompt_id, content=target_version.content, change_log=f"Rollback to {version_str}")

    def lint_prompt(self, prompt_id: UUID) -> List[LinterResult]:
        prompt = self.get_prompt(prompt_id)
        other_prompts = self.repository.list_all()
        return self.linter.lint(prompt, other_prompts)

    def compare_versions(self, prompt_id: UUID, v1: str, v2: str) -> str:
        versions = self.repository.get_versions(prompt_id)
        ver1 = next((v for v in versions if v.version == v1), None)
        ver2 = next((v for v in versions if v.version == v2), None)

        if not ver1 or not ver2:
            raise ValidationError(f"One or both versions ({v1}, {v2}) not found")

        diff = difflib.unified_diff(
            ver1.content.splitlines(),
            ver2.content.splitlines(),
            fromfile=f"v{v1}",
            tofile=f"v{v2}",
            lineterm=""
        )
        return "\n".join(diff)

    def get_stats(self) -> Dict[str, Any]:
        all_prompts = self.repository.list_all()
        total_prompts = len(all_prompts)
        total_usage = sum(p.usage_count for p in all_prompts)
        categories = {}
        for p in all_prompts:
            cat = p.category or "Uncategorized"
            categories[cat] = categories.get(cat, 0) + 1

        return {
            "total_prompts": total_prompts,
            "total_usage": total_usage,
            "categories": categories
        }
