from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from research_tool_hub.paths import data_dir


class JsonStore:
    def __init__(self, filename: str, default: Any) -> None:
        self.path = data_dir() / filename
        self.default = default

    def load(self) -> Any:
        if not self.path.exists():
            return self.default.copy() if hasattr(self.default, "copy") else self.default
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return self.default.copy() if hasattr(self.default, "copy") else self.default

    def save(self, value: Any) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(self.path.suffix + ".tmp")
        temporary.write_text(
            json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        temporary.replace(self.path)


class AppStateStore:
    def __init__(self) -> None:
        self._root_store = JsonStore("app_roots.json", {})
        self._favorite_store = JsonStore("favorites.json", [])
        self._recent_store = JsonStore("recent.json", [])

    def app_roots(self) -> dict[str, str]:
        value = self._root_store.load()
        return value if isinstance(value, dict) else {}

    def set_app_root(self, app_id: str, root: Path) -> None:
        roots = self.app_roots()
        roots[app_id] = str(root.resolve())
        self._root_store.save(roots)

    def favorites(self) -> set[str]:
        value = self._favorite_store.load()
        return set(value) if isinstance(value, list) else set()

    def toggle_favorite(self, app_id: str) -> bool:
        favorites = self.favorites()
        if app_id in favorites:
            favorites.remove(app_id)
            enabled = False
        else:
            favorites.add(app_id)
            enabled = True
        self._favorite_store.save(sorted(favorites))
        return enabled

    def recent(self) -> list[str]:
        value = self._recent_store.load()
        return [str(item) for item in value] if isinstance(value, list) else []

    def mark_recent(self, app_id: str, maximum: int = 12) -> None:
        recent = [item for item in self.recent() if item != app_id]
        recent.insert(0, app_id)
        self._recent_store.save(recent[:maximum])
