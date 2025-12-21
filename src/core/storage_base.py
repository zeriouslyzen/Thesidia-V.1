from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import json
import os

class StorageBackend(ABC):
    @abstractmethod
    def read_json(self, path: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def write_json(self, path: str, data: Dict[str, Any]) -> bool:
        pass

    @abstractmethod
    def ensure_path(self, path: str) -> bool:
        pass

    @abstractmethod
    def exists(self, path: str) -> bool:
        pass

    @abstractmethod
    def list_files(self, path: str) -> list:
        pass

class FileSystemBackend(StorageBackend):
    def __init__(self, root: Optional[str] = None):
        self.root = root

    def _get_full_path(self, path: str) -> str:
        if self.root:
            return os.path.join(self.root, path)
        return path

    def read_json(self, path: str) -> Optional[Dict[str, Any]]:
        full_path = self._get_full_path(path)
        try:
            if not os.path.exists(full_path):
                return None
            with open(full_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None

    def write_json(self, path: str, data: Dict[str, Any]) -> bool:
        full_path = self._get_full_path(path)
        try:
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False

    def ensure_path(self, path: str) -> bool:
        full_path = self._get_full_path(path)
        try:
            os.makedirs(full_path, exist_ok=True)
            return True
        except Exception:
            return False

    def exists(self, path: str) -> bool:
        return os.path.exists(self._get_full_path(path))

    def list_files(self, path: str) -> list:
        full_path = self._get_full_path(path)
        try:
            if not os.path.exists(full_path):
                return []
            return os.listdir(full_path)
        except Exception:
            return []
