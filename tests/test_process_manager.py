from pathlib import Path

from research_tool_hub.manifest_loader import load_manifest
from research_tool_hub.process_manager import ProcessManager


def test_resolve_relative_root() -> None:
    root = Path(__file__).resolve().parents[1]
    manifest = load_manifest(root / "manifests" / "model-interpreter.json")
    manager = ProcessManager()
    resolved = manager.resolve_app_root(manifest)
    assert resolved == (root / "apps-local" / "ModelInterpreter").resolve()


def test_override_root() -> None:
    root = Path(__file__).resolve().parents[1]
    manifest = load_manifest(root / "manifests" / "tape-designer.json")
    manager = ProcessManager()
    override = root / "tests" / "fake-app"
    assert manager.resolve_app_root(manifest, str(override)) == override.resolve()


def test_launch_and_stop_single_process(tmp_path: Path) -> None:
    import json
    import sys
    import time

    manifest_path = tmp_path / "sleep.json"
    manifest_path.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "id": "sleep-test",
                "name": "Sleep Test",
                "application_root": str(tmp_path),
                "default_profile": "default",
                "profiles": {
                    "default": {
                        "processes": [
                            {
                                "id": "sleep",
                                "executable": sys.executable,
                                "arguments": ["-c", "import time; time.sleep(30)"],
                                "working_directory": str(tmp_path),
                            }
                        ]
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    manifest = load_manifest(manifest_path)
    manager = ProcessManager()
    manager.launch(manifest, tmp_path)
    assert manager.status(manifest.id) == "running"
    manager.stop(manifest.id)
    time.sleep(0.05)
    assert manager.status(manifest.id) == "stopped"
