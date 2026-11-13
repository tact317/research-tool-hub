from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


class ManifestError(ValueError):
    pass


@dataclass(slots=True)
class DependencySpec:
    kind: str
    value: str
    label: str = ""
    required: bool = True

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "DependencySpec":
        kind = str(raw.get("kind", "")).strip()
        value = str(raw.get("value", "")).strip()
        if not kind or not value:
            raise ManifestError("dependency.kind と dependency.value は必須です")
        return cls(
            kind=kind,
            value=value,
            label=str(raw.get("label", "")),
            required=bool(raw.get("required", True)),
        )


@dataclass(slots=True)
class ProcessStep:
    id: str
    name: str
    executable: str
    arguments: list[str] = field(default_factory=list)
    working_directory: str = "."
    environment: dict[str, str] = field(default_factory=dict)
    shell: bool = False

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "ProcessStep":
        step_id = str(raw.get("id", "")).strip()
        executable = str(raw.get("executable", "")).strip()
        if not step_id or not executable:
            raise ManifestError("process.id と process.executable は必須です")
        args = raw.get("arguments", [])
        if not isinstance(args, list):
            raise ManifestError("process.arguments は配列で指定してください")
        env = raw.get("environment", {})
        if not isinstance(env, dict):
            raise ManifestError("process.environment はオブジェクトで指定してください")
        return cls(
            id=step_id,
            name=str(raw.get("name", step_id)),
            executable=executable,
            arguments=[str(item) for item in args],
            working_directory=str(raw.get("working_directory", ".")),
            environment={str(k): str(v) for k, v in env.items()},
            shell=bool(raw.get("shell", False)),
        )


@dataclass(slots=True)
class ReadyCheck:
    kind: str
    target: str
    timeout_seconds: float = 30.0

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "ReadyCheck":
        kind = str(raw.get("kind", "")).strip()
        target = str(raw.get("target", "")).strip()
        if not kind or not target:
            raise ManifestError("ready_check.kind と ready_check.target は必須です")
        return cls(kind, target, float(raw.get("timeout_seconds", 30.0)))


@dataclass(slots=True)
class LaunchProfile:
    id: str
    name: str
    processes: list[ProcessStep] = field(default_factory=list)
    ready_checks: list[ReadyCheck] = field(default_factory=list)
    open_url: str | None = None
    open_path: str | None = None

    @classmethod
    def from_dict(cls, profile_id: str, raw: dict[str, Any]) -> "LaunchProfile":
        processes_raw = raw.get("processes", [])
        checks_raw = raw.get("ready_checks", [])
        if not isinstance(processes_raw, list) or not isinstance(checks_raw, list):
            raise ManifestError("processes と ready_checks は配列で指定してください")
        profile = cls(
            id=profile_id,
            name=str(raw.get("name", profile_id)),
            processes=[ProcessStep.from_dict(item) for item in processes_raw],
            ready_checks=[ReadyCheck.from_dict(item) for item in checks_raw],
            open_url=str(raw["open_url"]) if raw.get("open_url") else None,
            open_path=str(raw["open_path"]) if raw.get("open_path") else None,
        )
        if not profile.processes and not profile.open_url and not profile.open_path:
            raise ManifestError(f"profile '{profile_id}' に起動対象がありません")
        return profile


@dataclass(slots=True)
class AppManifest:
    source_path: Path
    schema_version: str
    id: str
    name: str
    version: str
    category: str
    description: str
    application_root: str
    profiles: dict[str, LaunchProfile]
    default_profile: str
    tags: list[str] = field(default_factory=list)
    icon: str | None = None
    documentation: str | None = None
    dependencies: list[DependencySpec] = field(default_factory=list)

    @classmethod
    def from_dict(cls, source_path: Path, raw: dict[str, Any]) -> "AppManifest":
        app_id = str(raw.get("id", "")).strip()
        name = str(raw.get("name", "")).strip()
        if not app_id or not name:
            raise ManifestError("id と name は必須です")
        profiles_raw = raw.get("profiles", {})
        if not isinstance(profiles_raw, dict) or not profiles_raw:
            raise ManifestError("profiles を1件以上指定してください")
        profiles = {
            str(profile_id): LaunchProfile.from_dict(str(profile_id), profile_raw)
            for profile_id, profile_raw in profiles_raw.items()
        }
        default_profile = str(raw.get("default_profile", next(iter(profiles))))
        if default_profile not in profiles:
            raise ManifestError("default_profile が profiles 内に存在しません")
        dependencies_raw = raw.get("dependencies", [])
        if not isinstance(dependencies_raw, list):
            raise ManifestError("dependencies は配列で指定してください")
        tags_raw = raw.get("tags", [])
        if not isinstance(tags_raw, list):
            raise ManifestError("tags は配列で指定してください")
        return cls(
            source_path=source_path,
            schema_version=str(raw.get("schema_version", "1.0")),
            id=app_id,
            name=name,
            version=str(raw.get("version", "")),
            category=str(raw.get("category", "その他")),
            description=str(raw.get("description", "")),
            application_root=str(raw.get("application_root", ".")),
            profiles=profiles,
            default_profile=default_profile,
            tags=[str(tag) for tag in tags_raw],
            icon=str(raw["icon"]) if raw.get("icon") else None,
            documentation=str(raw["documentation"]) if raw.get("documentation") else None,
            dependencies=[DependencySpec.from_dict(item) for item in dependencies_raw],
        )
