import os
import pickle
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class CacheMemory:
    def __init__(self, cache_file: str):
        self.cache_file = cache_file
        self.cache: Dict[str, Dict[str, Any]] = self._load_cache()

    def _load_cache(self) -> Dict[str, Dict[str, Any]]:
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "rb") as f:
                    cache = pickle.load(f)
                    if not isinstance(cache, dict):
                        raise ValueError("Invalid cache format.")
                    return cache
            except Exception as e:
                logger.warning(f"Failed to load cache ({e}), deleting corrupted cache file.")
                os.remove(self.cache_file)
        return {}

    def save(self):
        with open(self.cache_file, "wb") as f:
            pickle.dump(self.cache, f)

    def get(self, key: str) -> Dict[str, Any] | None:
        return self.cache.get(key)

    def set(self, key: str, value: Dict[str, Any]):
        self.cache[key] = value
        self.save()
