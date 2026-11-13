# Research Tool Hub MVP 0.1

研究・開発で作成したWindowsアプリ、Pythonアプリ、Webアプリを一つの画面から起動・停止・管理する統合ランチャーです。

## MVP 0.1で実装済み

- `manifests/*.json`からアプリを自動登録
- アプリ名、説明、タグの検索
- カテゴリ表示
- お気に入り
- 最近使用したアプリ
- アプリごとの配置先上書き
- Windows EXE起動
- `.bat`、Python、npmなどのコマンド起動
- FastAPI＋Next.jsなどの複数プロセス同時起動
- HTTP・TCP・ファイルによる起動確認
- Webアプリのブラウザ自動表示
- 起動、停止、再試行
- 標準出力・エラー出力のログ保存
- 依存環境の確認
- マニフェスト追加

## 初期登録済み

1. Tape Reel Designer 3D 3.1.0
2. 周期構造テープ成形デザイナ 5.0.0-rc1
3. Radia to Python Studio 0.9.0
4. Model Interpreter 1.0.0
5. Paper Translator 0.1.0

アプリ本体はこのZIPには含めていません。既存ZIPを展開し、カードの「場所を設定」からルートフォルダを選択します。

## Windowsでの起動

PowerShellで次を実行します。

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\setup_windows.ps1
```

セットアップ後は次をダブルクリックします。

```text
start_hub.bat
```

Python 3.11以上が必要です。推奨はPython 3.12です。

## 既存アプリの登録

1. Hubを起動します。
2. アプリカードの「場所を設定」を押します。
3. 対象アプリのルートフォルダを選択します。
4. 「詳細」で依存環境がすべてOKか確認します。
5. 「起動」を押します。

具体的な選択フォルダは `docs/current_apps.md` を参照してください。

## フォルダ構成

```text
ResearchToolHub_MVP_0_1/
├─ research_tool_hub/       Hub本体
├─ manifests/               アプリ定義
├─ data/                    配置先・お気に入り・履歴
├─ logs/                    各アプリの実行ログ
├─ apps-local/              任意の標準配置先
├─ docs/
├─ setup_windows.ps1
├─ start_hub.bat
└─ build_windows.ps1
```

## EXE化

セットアップ後に実行します。

```powershell
.\build_windows.ps1
```

出力先:

```text
dist\ResearchToolHub\ResearchToolHub.exe
```

## 現時点の制限

- 起動プロファイルはマニフェストの`default_profile`を使用します。UIからの切替は次版で追加予定です。
- アプリ本体の自動更新・ZIP自動展開は未実装です。
- Ollamaモデルの存在確認は未実装で、Ollamaコマンドの存在だけ確認します。
- Hub終了時に、Hubが起動した子プロセスを終了するか選択します。
- 既に外部から起動されていた同一アプリの検出は未実装です。

## マニフェスト検証

```powershell
.\.venv\Scripts\python.exe tools\validate_manifests.py
```

## 5つのZIPを標準配置へ一括展開

5つの既存ZIPをResearch Tool Hubのフォルダへコピーしてから実行します。

```powershell
.\import_uploaded_apps.ps1
```

ZIPが別フォルダにある場合:

```powershell
.\import_uploaded_apps.ps1 -SourceDir "C:\Users\user\Downloads"
```
