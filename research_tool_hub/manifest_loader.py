from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from research_tool_hub.models import AppManifest, ManifestError


@dataclass(slots=True)
class ManifestLoadIssue:
    path: Path
    message: str


def load_manifest(path: Path) -> AppManifest:
    try:
        raw = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ManifestError(f"JSONを読み込めません: {exc}") from exc
    if not isinstance(raw, dict):
        raise ManifestError("マニフェストのルートはオブジェクトである必要があります")
    return AppManifest.from_dict(path, raw)


def discover_manifests(directory: Path) -> tuple[list[AppManifest], list[ManifestLoadIssue]]:
    apps: list[AppManifest] = []
    issues: list[ManifestLoadIssue] = []
    if not directory.exists():
        return apps, issues
    for path in sorted(directory.glob("*.json")):
        try:
            apps.append(load_manifest(path))
        except ManifestError as exc:
            issues.append(ManifestLoadIssue(path, str(exc)))
    seen: set[str] = set()
    duplicates: set[str] = set()
    for app in apps:
        if app.id in seen:
            duplicates.add(app.id)
        seen.add(app.id)
    if duplicates:
        for duplicate in sorted(duplicates):
            issues.append(ManifestLoadIssue(directory, f"重複したアプリID: {duplicate}"))
        apps = [app for app in apps if app.id not in duplicates]
    return apps, issues
