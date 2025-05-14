\
---
description: プロジェクト固有ルール
globs: 
alwaysApply: true
---
# プロジェクト固有ルール

このファイルは、本プロジェクト特有の環境設定、技術スタック、ディレクトリ構成、Python開発ルール、セキュリティガイドラインなどを定義します。
`core.mdc` に定義された普遍的なルールを前提とし、それを補完・具体化します。

## 1. 開発環境

### 1.1 VSCode Dev Container環境
- すでにVSCode Dev Container内で作業中
- コンテナ設定は .devcontainer で管理
- 新規Dockerfile作成は禁止（Dev Container使用のため）
- 作業ディレクトリ: ~/workspace

### 1.2 コンテナ環境詳細
- ベースイメージ: python:3.12-slim （詳細は [techContext.md](mdc:memory-bank/techContext.md) 参照）
- 公開ポート: 7860（Gradio用）（詳細は [techContext.md](mdc:memory-bank/techContext.md) 参照）
- Git操作はコンテナ内で実施
- 環境変数は.devcontainer経由で管理（詳細は [techContext.md](mdc:memory-bank/techContext.md) 参照）

## 2. Python 開発ルール (本プロジェクト固有)

### 2.1 Python環境
- Pythonバージョン: 3.10～3.12
    - Python 3.10～3.12 を使用する
    - 実装も、3.10以上を前提とする
        - 3.9等下位バージョンへの互換性考慮は不要
- 依存関係管理: Poetry
    - ライブラリは Poetry でのみ管理する
- 仮想環境: /.venv（Poetry により管理）
- flake8, black, isort, pytest を使用

### 2.2 プロジェクト設定
- **プロジェクト名:** `pyproject.toml` 内の `tool.poetry.name` は `"cursor_dev"` とする。

### 2.3 コードスタイル & パターン
- Type Hint は必ず使用する
    - typing ライブラリ・モジュールの利用は、必要最小限とする
- フォーマッターは、black を使う
    - 実行コマンド: `black .`
- リンターチェックは、flake8 を使う
    - 実行コマンド: `flake8  --exclude .venv`
    - flake8 のLintエラーを全消去する
- 変数名は snake_case を使用する
- クラス名は PascalCase を使用する
- 定数は UPPER_SNAKE_CASE を使用する
- プライベートには先頭アンダースコアを付加する
- docstring は Google スタイル、typing モジュールを使わない型ヒントを積極利用する
- 1行79文字以内、インデント4スペースとする
- 特に、VSCode 上の `blank line contains whitespace` という Lint エラーに必ず対応する

### 2.4 テストコード
- テストコードは tests/ に置き、pytest を使用する ([test_strategy.md](mdc:memory-bank/test_strategy.md) 参照)

## 3. ディレクトリ構成

下記構成を厳守し、新ディレクトリ追加時はREADME.mdを作成・説明を追記します。

```
./
├── LICENSE
├── Makefile
├── README.md
├── app/
├── bin/
├── docs/
│   ├── 01.requirements/
│   ├── 02.basic_design/
│   ├── 03.detail_design/
│   ├── 11.errors/
│   ├── 12.fixes/
│   ├── 31.progress/
│   ├── 90.references/
│   └── 91.notes/
├── knowledge/
├── memory-bank/
├── tests/
└── pyproject.toml
```

上記以外のフォルダ構成、ファイル構成は禁止

## 4. 作業ディレクトリ

コンテナ内の ~/workspace とします。変更禁止

## 5. セキュリティ

### 5.1 機密ファイル

以下のファイルを **読んだり変更したりしない** こと：

- .env ファイル
- \*_/config/secrets._
- \*_/_.pem
- APIキー、トークン、または認証情報を含むファイル全般

### 5.2 セキュリティ対策

- 機密ファイルをコミットしない
- シークレット情報には環境変数を使用する ([techContext.md](mdc:memory-bank/techContext.md) 参照)
- 認証情報をログや出力に含めない
- コンテナ内での機密情報は環境変数経由で管理

### 5.3 機密情報チェックツール (`bin/security_check.py`) の運用
- **検知漏れ発生時の対応:** 本ツールで検知・マスク漏れが発覚した場合、まずツールの検知ロジックやマスク処理方法を見直し、改善する。
- **ツール改善優先:** ツール改善が完了し、再チェックで問題ないことを確認してから、漏洩した可能性のあるコミットの修正や再プッシュ等の後続対応を行う。

## 6. プロジェクトガイドライン

### 6.1 ドキュメント要件
- 機能を変更する際は、/docs 内の関連ドキュメントを更新する
- README.md を新しい機能に合わせて更新する
- 具体的には、[documentation_strategy.md](mdc:memory-bank/documentation_strategy.md) に従う

### 6.2 アーキテクチャの決定記録（ADR）
以下の変更を行う際は /docs/adr にADRを作成する：
- 主要な依存関係の変更
- アーキテクチャパターンの変更
- 新しい統合パターンの導入
- データベーススキーマの変更
    /docs/adr/template.md のテンプレートに従うこと

### 6.3 テスト
テストドリブンで開発する (i.e. テストを仕様とする)
詳細は、[test_strategy.md](mdc:memory-bank/test_strategy.md) に従う

### 6.4 エラー解析
障害時は対象部分と周辺を調査し、アブダクションで原因を特定し、解消する
詳細は、[error_analysis.md](mdc:memory-bank/error_analysis.md) に従う

### 6.5 設計および実装原則
[design_principles.md](mdc:memory-bank/design_principles.md) に従う

### 6.6 Git 操作ルール
- **Push Protection 等による Push 拒否時の対応:**
  - `git push` がリモートリポジトリのルール（例: GitHub Push Protection）によって拒否された場合、エラーメッセージをよく読み、要因（例: 機密情報の混入）を特定する。
  - 特定した要因とエラーメッセージをユーザーに報告する。
  - **ユーザーの指示があるまで、コミット履歴の修正 (`git rebase`, `git filter-repo` 等）や強制プッシュ (`git push --force`) などの対処は行わない。**

## 7. リポジトリの初期化/クリーンアップ

本プロジェクトリポジトリを空にする場合は、以下コマンドを実行することでのみ行う

```bash
make clean-repository
``` 