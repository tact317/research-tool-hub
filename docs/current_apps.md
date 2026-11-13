# 初期登録アプリ

## Tape Reel Designer 3D 3.1.0

`version_info_v3_1.zip`を展開し、ZIP直下をアプリルートとして指定します。

確認対象:

```text
dist/TapeReelDesigner3D/TapeReelDesigner3D.exe
```

## 周期構造テープ成形デザイナ 5.0.0-rc1

`TapeDesigner_Development_Migration_Recovery_Guide.zip`を展開し、ZIP直下を指定します。

確認対象:

```text
dist/TapeDesigner/TapeDesigner.exe
```

## Radia to Python Studio 0.9.0

`_patch_backups.zip`を展開し、`run_app.bat`、`app`、`requirements.txt`があるフォルダを指定します。

`.venv`がなければ`run_app.bat`はシステムのPythonを使用します。必要パッケージは対象アプリ側で準備してください。

## Model Interpreter 1.0.0

`vite.config.zip`を展開し、`package.json`と`vite.config.ts`があるフォルダを指定します。

既定起動:

```text
npm run dev -- --host 127.0.0.1 --port 5173
```

## Paper Translator 0.1.0

`PeperTranslator.zip`を展開し、`backend`、`backend_env`、`frontend`が入っている内側の`PeperTranslator`フォルダを指定します。

既定起動:

```text
backend_env/Scripts/python.exe -m uvicorn main:app --port 8000
npm run dev -- -p 3000
```

注意点:

- 同梱仮想環境は作成元PCのPython構成に依存する可能性があります。
- 起動できない場合は仮想環境を再作成し、FastAPI、uvicorn、ollama、PyMuPDF、python-multipartを導入してください。
- 採点機能にはOllamaと`qwen2.5:14b`が必要です。
