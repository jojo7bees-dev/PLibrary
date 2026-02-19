import json
import os
import hashlib
from typing import Any, Optional, Dict

class DiskCache:
    def __init__(self, cache_dir: str = ".cache"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)

    def _get_path(self, key: str) -> str:
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{key_hash}.json")

    def get(self, key: str) -> Optional[Any]:
        path = self._get_path(key)
        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f)
        return None

    def set(self, key: str, value: Any):
        path = self._get_path(key)
        with open(path, "w") as f:
            json.dump(value, f)

    def clear(self):
        for f in os.listdir(self.cache_dir):
            os.remove(os.path.join(self.cache_dir, f))
