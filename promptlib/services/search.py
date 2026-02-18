import difflib
from typing import List, Optional
from promptlib.models.prompt import Prompt
from promptlib.storage.base import BaseRepository

class SearchService:
    def __init__(self, repository: BaseRepository):
        self.repository = repository

    def search(self, query: str, fuzzy: bool = True, threshold: float = 0.5) -> List[Prompt]:
        # 1. Get results from repository (indexed search or simple scan)
        results = self.repository.search(query)

        if not fuzzy:
            return results

        # 2. Perform fuzzy ranking/filtering if requested
        # We can also pull all prompts and fuzzy match names if the initial search was too narrow
        if not results:
            all_prompts = self.repository.list_all()
            for p in all_prompts:
                # Compare query with name and content
                name_score = difflib.SequenceMatcher(None, query.lower(), p.name.lower()).ratio()
                content_score = difflib.SequenceMatcher(None, query.lower(), p.content.lower()).ratio()
                if max(name_score, content_score) >= threshold:
                    results.append(p)

            # Rank by score
            results.sort(key=lambda x: max(
                difflib.SequenceMatcher(None, query.lower(), x.name.lower()).ratio(),
                difflib.SequenceMatcher(None, query.lower(), x.content.lower()).ratio()
            ), reverse=True)

        return results

    def filter_by_tags(self, tags: List[str]) -> List[Prompt]:
        return self.repository.list_all(tags=tags)

    def filter_by_category(self, category: str) -> List[Prompt]:
        return self.repository.list_all(category=category)
