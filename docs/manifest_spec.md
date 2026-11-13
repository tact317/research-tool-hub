# Research Tool Hub マニフェスト仕様 v1.0

各アプリは `manifests/*.json` の1ファイルで登録します。アプリ本体をHubのフォルダへコピーする必要はありません。

## 最小例

```json
{
  "schema_version": "1.0",
  "id": "sample-app",
  "name": "Sample App",
  "version": "1.0.0",
  "category": "その他",
  "description": "説明",
  "application_root": "apps-local/SampleApp",
  "default_profile": "default",
  "profiles": {
    "default": {
      "name": "通常起動",
      "processes": [
        {
          "id": "main",
          "name": "Main process",
          "executable": "${APP_ROOT}/SampleApp.exe",
          "arguments": [],
          "working_directory": "${APP_ROOT}"
        }
      ]
    }
  }
}
```

## 置換変数

- `${APP_ROOT}`: そのアプリのルートフォルダ。UIの「場所を設定」で上書き可能
- `${HUB_ROOT}`: Research Tool Hub本体のフォルダ
- `%NAME%`: Windowsの環境変数

## profiles

同じアプリに複数の起動方法を定義できます。MVP 0.1の画面は `default_profile` を使用します。

### process

- `id`: プロセス識別子
- `name`: 表示名
- `executable`: EXE、Python、npm.cmd、batなど
- `arguments`: 引数の配列
- `working_directory`: 作業フォルダ
- `environment`: 追加環境変数
- `shell`: `.bat`などをシェル経由で起動する場合はtrue

### ready_checks

複数サービス型アプリで、ブラウザを開く前に起動を確認します。

```json
{
  "kind": "http",
  "target": "http://127.0.0.1:3000/",
  "timeout_seconds": 60
}
```

対応種別:

- `http`: HTTP応答を確認
- `tcp`: `127.0.0.1:8000`形式でTCP接続を確認
- `path`: ファイルまたはフォルダの生成を確認

### open_url / open_path

起動確認後にブラウザまたはファイルを開きます。

## dependencies

起動前に必要環境を検査します。

```json
{
  "kind": "command",
  "value": "npm.cmd",
  "label": "Node.js / npm",
  "required": true
}
```

対応種別:

- `path`: ファイル・フォルダの存在
- `command`: PATH上のコマンド
