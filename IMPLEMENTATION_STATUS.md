# Implementation Status — MVP 0.1

## 完了

- 5アプリの初期マニフェスト
- Windows EXE起動
- バッチ・任意コマンド起動
- 単一／複数プロセス管理
- HTTP・TCP・パス起動確認
- ブラウザ自動表示
- プロセスツリー停止
- アプリ配置先の個別上書き
- 検索、カテゴリ、お気に入り、最近使用
- 依存環境表示
- ログ保存
- マニフェスト追加
- Windowsセットアップ／PyInstallerビルドスクリプト
- 5つの既存ZIPを標準配置へ展開するPowerShellスクリプト

## 検証結果

```text
manifest validation: valid=5 invalid=0
pytest: 5 passed
Python compileall: passed
```

GUIはPySide6を使用します。作成環境ではPySide6本体を導入していないため、GUI描画の実機検証はWindows側で`setup_windows.ps1`実行後に行う必要があります。コア部分のマニフェスト読込、パス解決、プロセス起動・停止は自動テスト済みです。

## 次版候補

1. UI上で起動プロファイルを切り替える
2. ZIPをドラッグ＆ドロップして自動判定・登録する
3. アプリごとのセットアップ／修復ボタン
4. 使用ポートの競合検出と自動割当
5. Ollamaモデル、Pythonパッケージ、Node.js版の詳細診断
6. アプリ更新履歴とバージョン比較
7. 各アプリのスクリーンショット・説明ページ
