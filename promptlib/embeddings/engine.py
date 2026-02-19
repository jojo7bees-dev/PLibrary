from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer
import numpy as np
import hashlib
from promptlib.core.caching import DiskCache

class EmbeddingEngine:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", cache_dir: str = ".cache/embeddings"):
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        self.cache = DiskCache(cache_dir)

    def generate(self, text: str) -> List[float]:
        # Simple content-based caching
        cached = self.cache.get(text)
        if cached:
            return cached

        embedding = self.model.encode(text)
        embedding_list = embedding.tolist()
        self.cache.set(text, embedding_list)
        return embedding_list

    def generate_batch(self, texts: List[str]) -> List[List[float]]:
        embeddings = self.model.encode(texts)
        return embeddings.tolist()

    def get_dimension(self) -> int:
        return self.model.get_sentence_embedding_dimension()

    def clear_cache(self):
        self.cache.clear()
