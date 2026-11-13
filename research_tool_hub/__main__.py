from __future__ import annotations

import sys


def main() -> int:
    try:
        from research_tool_hub.ui.main_window import run_app
    except ImportError as exc:
        if exc.name == "PySide6" or "PySide6" in str(exc):
            print(
                "PySide6 がインストールされていません。\n"
                "Windowsでは setup_windows.ps1 を実行してください。",
                file=sys.stderr,
            )
            return 2
        raise
    return run_app()


if __name__ == "__main__":
    raise SystemExit(main())
