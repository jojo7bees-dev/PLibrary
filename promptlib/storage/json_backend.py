import json
import os
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from promptlib.models.prompt import Prompt
from promptlib.models.version import PromptVersion
from promptlib.storage.base import BaseRepository

class JSONRepository(BaseRepository):
    def __init__(self, storage_dir: str = "prompts_json"):
        self.storage_dir = storage_dir
        self.prompts_dir = os.path.join(storage_dir, "prompts")
        self.versions_dir = os.path.join(storage_dir, "versions")
        os.makedirs(self.prompts_dir, exist_ok=True)
        os.makedirs(self.versions_dir, exist_ok=True)

    def _get_path(self, prompt_id: UUID) -> str:
        return os.path.join(self.prompts_dir, f"{prompt_id}.json")

    def save(self, prompt: Prompt) -> None:
        path = self._get_path(prompt.id)
        with open(path, 'w') as f:
            f.write(prompt.model_dump_json(indent=2))

    def get_by_id(self, prompt_id: UUID) -> Optional[Prompt]:
        path = self._get_path(prompt_id)
        if not os.path.exists(path):
            return None
        with open(path, 'r') as f:
            data = json.load(f)
            return Prompt(**data)

    def get_by_name(self, name: str) -> Optional[Prompt]:
        # Linear scan for name search in JSON files
        for filename in os.listdir(self.prompts_dir):
            if filename.endswith(".json"):
                with open(os.path.join(self.prompts_dir, filename), 'r') as f:
                    data = json.load(f)
                    if data.get("name") == name:
                        return Prompt(**data)
        return None

    def delete(self, prompt_id: UUID) -> None:
        path = self._get_path(prompt_id)
        if os.path.exists(path):
            os.remove(path)

    def list_all(self, category: Optional[str] = None, tags: Optional[List[str]] = None) -> List[Prompt]:
        prompts = []
        for filename in os.listdir(self.prompts_dir):
            if filename.endswith(".json"):
                with open(os.path.join(self.prompts_dir, filename), 'r') as f:
                    data = json.load(f)
                    p = Prompt(**data)
                    if category and p.category != category:
                        continue
                    if tags and not all(t in p.tags for t in tags):
                        continue
                    prompts.append(p)
        return prompts

    def search(self, query: str) -> List[Prompt]:
        prompts = []
        for filename in os.listdir(self.prompts_dir):
            if filename.endswith(".json"):
                with open(os.path.join(self.prompts_dir, filename), 'r') as f:
                    data = json.load(f)
                    if query.lower() in data.get("name", "").lower() or query.lower() in data.get("content", "").lower():
                        prompts.append(Prompt(**data))
        # Usage-based ranking
        prompts.sort(key=lambda x: x.usage_count, reverse=True)
        return prompts

    def save_version(self, version: PromptVersion) -> None:
        v_dir = os.path.join(self.versions_dir, str(version.prompt_id))
        os.makedirs(v_dir, exist_ok=True)
        path = os.path.join(v_dir, f"{version.version}.json")
        with open(path, 'w') as f:
            f.write(version.model_dump_json(indent=2))

    def get_versions(self, prompt_id: UUID) -> List[PromptVersion]:
        v_dir = os.path.join(self.versions_dir, str(prompt_id))
        if not os.path.exists(v_dir):
            return []
        versions = []
        for filename in os.listdir(v_dir):
            if filename.endswith(".json"):
                with open(os.path.join(v_dir, filename), 'r') as f:
                    data = json.load(f)
                    versions.append(PromptVersion(**data))
        return versions

    def update_usage(self, prompt_id: UUID) -> None:
        prompt = self.get_by_id(prompt_id)
        if prompt:
            prompt.usage_count += 1
            prompt.last_used = datetime.now()
            self.save(prompt)
