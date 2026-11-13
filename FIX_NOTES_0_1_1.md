# Research Tool Hub MVP 0.1.1 fix

This revision fixes Windows PowerShell 5.1 parsing failures caused by UTF-8 text without a BOM.

Changes:

- Added UTF-8 BOM to all `.ps1` files.
- Changed PowerShell and batch status messages to ASCII-only text.
- Added `inbox`, `staging`, and `archive` handling to `import_uploaded_apps.ps1`.
- ZIP files are extracted in `staging` first, so failed extraction does not leave a partial app in `apps-local`.
- Added `-ReplaceExisting` to archive an existing imported app before replacement.
- Reuses an existing Hub `.venv` during setup.

Normal import:

```powershell
.\import_uploaded_apps.ps1
```

Import ZIPs from another directory:

```powershell
.\import_uploaded_apps.ps1 -SourceDir "C:\Users\user\Downloads"
```

Replace existing imported folders while preserving old versions:

```powershell
.\import_uploaded_apps.ps1 -SourceDir "C:\Users\user\Downloads" -ReplaceExisting
```
