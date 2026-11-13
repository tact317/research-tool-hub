@echo off
setlocal
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" -m research_tool_hub
) else (
  echo Virtual environment not found.
  echo Run setup_windows.ps1 first.
  pause
)
endlocal
