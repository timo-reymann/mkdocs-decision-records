from typing import Any


class MetaModel:
    _data: list[tuple[str, Any]]

    def __init__(self):
        self._data = []

    def add(self, key: str, value: Any):
        self._data.append((key, value))

    def get(self, key: str) -> str | None:
        for k, v in self._data:
            if k == key:
                return v
        return None

    def get_all(self) -> list[tuple[str, Any]]:
        return self._data