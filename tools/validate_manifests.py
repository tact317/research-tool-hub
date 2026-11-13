from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_tool_hub.manifest_loader import discover_manifests
from research_tool_hub.paths import manifests_dir


def main() -> int:
    apps, issues = discover_manifests(manifests_dir())
    for app in apps:
        print(f"OK  {app.id:30} {app.name}")
    for issue in issues:
        print(f"NG  {issue.path}: {issue.message}")
    print(f"\nvalid={len(apps)} invalid={len(issues)}")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
