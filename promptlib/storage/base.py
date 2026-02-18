from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from uuid import UUID
from promptlib.models.prompt import Prompt
from promptlib.models.version import PromptVersion

class BaseRepository(ABC):
    @abstractmethod
    def save(self, prompt: Prompt) -> None:
        pass

    @abstractmethod
    def get_by_id(self, prompt_id: UUID) -> Optional[Prompt]:
        pass

    @abstractmethod
    def get_by_name(self, name: str) -> Optional[Prompt]:
        pass

    @abstractmethod
    def delete(self, prompt_id: UUID) -> None:
        pass

    @abstractmethod
    def list_all(self, category: Optional[str] = None, tags: Optional[List[str]] = None) -> List[Prompt]:
        pass

    @abstractmethod
    def search(self, query: str) -> List[Prompt]:
        pass

    @abstractmethod
    def save_version(self, version: PromptVersion) -> None:
        pass

    @abstractmethod
    def get_versions(self, prompt_id: UUID) -> List[PromptVersion]:
        pass

    @abstractmethod
    def update_usage(self, prompt_id: UUID) -> None:
        pass
