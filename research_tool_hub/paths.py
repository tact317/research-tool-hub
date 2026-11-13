from __future__ import annotations

import os
import sys
from pathlib import Path


def hub_root() -> Path:
    """Return the writable portable root for source and PyInstaller builds."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[1]


def manifests_dir() -> Path:
    return hub_root() / "manifests"


def data_dir() -> Path:
    path = hub_root() / "data"
    path.mkdir(parents=True, exist_ok=True)
    return path


def logs_dir() -> Path:
    path = hub_root() / "logs"
    path.mkdir(parents=True, exist_ok=True)
    return path


def expand_environment(value: str) -> str:
    return os.path.expandvars(os.path.expanduser(value))
