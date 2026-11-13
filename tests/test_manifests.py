from pathlib import Path

from research_tool_hub.manifest_loader import discover_manifests


def test_all_bundled_manifests_are_valid() -> None:
    root = Path(__file__).resolve().parents[1]
    apps, issues = discover_manifests(root / "manifests")
    assert not issues
    assert {app.id for app in apps} == {
        "tape-reel-designer-3d",
        "tape-designer",
        "radia-to-python-studio",
        "model-interpreter",
        "paper-translator",
    }


def test_multi_process_manifest() -> None:
    root = Path(__file__).resolve().parents[1]
    apps, _ = discover_manifests(root / "manifests")
    paper = next(app for app in apps if app.id == "paper-translator")
    assert len(paper.profiles[paper.default_profile].processes) == 2
    assert paper.profiles[paper.default_profile].open_url == "http://127.0.0.1:3000/"
