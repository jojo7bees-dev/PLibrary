import faiss
import numpy as np
import os
from typing import List, Tuple, Optional

class VectorIndex:
    def __init__(self, dimension: int, index_path: Optional[str] = None):
        self.dimension = dimension
        self.index_path = index_path
        self.index = faiss.IndexFlatL2(dimension)
        self.ids: List[str] = [] # List of prompt IDs corresponding to index positions

        if index_path and os.path.exists(index_path):
            self.load(index_path)

    def add(self, prompt_id: str, vector: List[float]):
        vec_np = np.array([vector]).astype('float32')
        self.index.add(vec_np)
        self.ids.append(prompt_id)

    def search(self, vector: List[float], k: int = 5) -> List[Tuple[str, float]]:
        if self.index.ntotal == 0:
            return []

        vec_np = np.array([vector]).astype('float32')
        distances, indices = self.index.search(vec_np, k)

        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx != -1 and idx < len(self.ids):
                results.append((self.ids[idx], float(dist)))
        return results

    def save(self, path: Optional[str] = None):
        target_path = path or self.index_path
        if not target_path:
            return
        faiss.write_index(self.index, target_path)
        # We also need to save the IDs mapping
        with open(target_path + ".ids", "w") as f:
            f.write("\n".join(self.ids))

    def load(self, path: str):
        self.index = faiss.read_index(path)
        if os.path.exists(path + ".ids"):
            with open(path + ".ids", "r") as f:
                self.ids = f.read().splitlines()

    def reset(self):
        self.index = faiss.IndexFlatL2(self.dimension)
        self.ids = []
