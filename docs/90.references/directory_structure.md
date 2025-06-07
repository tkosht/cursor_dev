# プロジェクト ディレクトリ構造規約

最終更新: 2025-06-07 (worker/ディレクトリ、dev-tools/ディレクトリ追加)

## 📋 概要

このドキュメントは、プロジェクトのディレクトリ構造を定義し、その維持を保証するための規約です。
すべての開発者はこの構造を厳守し、新しいファイルを作成する際は適切な場所に配置してください。

## 🗂️ ディレクトリ構造

```
./
├── .cursor/            # Cursor AI 設定
│   └── rules/          # ルールファイル (*.mdc)
├── .devcontainer/      # Dev Container 設定
├── .vscode/            # VSCode 設定
├── app/                # ソースコード (Pythonパッケージ)
│   ├── a2a/            # A2Aプロトコル実装
│   │   ├── agents/     # エージェント実装
│   │   ├── core/       # コアタイプと例外
│   │   ├── server/     # FastAPIサーバー
│   │   ├── skills/     # スキル実装
│   │   └── storage/    # ストレージ層
│   └── __init__.py
├── bin/                # 実行ファイル、スクリプト
├── docker/             # Dockerfile群
├── docs/               # ドキュメント
│   ├── 01.requirements/        # 要件定義書
│   ├── 02.basic_design/        # 基本設計書
│   ├── 03.detail_design/       # 詳細設計書
│   ├── 04.implementation_reports/  # 実装報告書
│   ├── 05.articles/            # 技術記事・Note記事
│   ├── 90.references/          # 参考資料・ガイド
│   └── 91.notes/               # メモ・下書き
├── memory-bank/        # AIの記憶領域 (プロジェクトコンテキスト)
│   └── knowledge/      # 汎用的な技術知識
├── output/             # 作業結果・生成物 (git無視)
│   ├── coverage/       # テストカバレッジレポート
│   ├── reports/        # 各種分析レポート
│   ├── artifacts/      # ビルド成果物
│   └── logs/           # 実行ログ
├── scripts/            # ユーティリティスクリプト
├── tests/              # テストコード
│   ├── unit/           # ユニットテスト
│   ├── integration/    # 統合テスト
│   └── e2e/            # E2Eテスト
├── .cursor_dev.code-workspace  # ワークスペース設定
├── pyproject.toml      # Poetry設定ファイル
├── LICENSE             # ライセンス
└── README.md           # プロジェクトREADME
```

## 📁 ディレクトリ別ガイドライン

### `/app/`
- **用途**: プロダクションコード
- **ルール**: 
  - 新機能は適切なサブディレクトリに配置
  - パッケージ名は小文字とアンダースコアのみ使用
  - 各ディレクトリに`__init__.py`を配置

### `/docs/`
- **用途**: プロジェクトドキュメント
- **ルール**:
  - `01.requirements/`: 要件定義、ユースケース
  - `02.basic_design/`: アーキテクチャ、システム設計
  - `03.detail_design/`: 実装設計、API仕様
  - `04.implementation_reports/`: 実装レポート、分析結果
  - `05.articles/`: 公開用記事、チュートリアル
  - `90.references/`: 設定ガイド、テンプレート
  - `91.notes/`: 一時的なメモ、下書き

### `/tests/`
- **用途**: テストコード
- **ルール**:
  - テストファイルは`test_`で開始
  - ソースコードと同じ構造を維持
  - フィクスチャは`conftest.py`に配置

### `/memory-bank/`
- **用途**: AI開発支援のためのコンテキスト情報
- **ルール**:
  - プロジェクト固有の知識を記録
  - ルール、パターン、教訓を文書化
  - `/knowledge/`: 汎用的な技術知識を配置

### `/output/`
- **用途**: 作業結果・生成物の出力先
- **ルール**:
  - Git管理対象外（`.gitignore`で除外）
  - `/coverage/`: テストカバレッジレポート
  - `/reports/`: 品質・セキュリティ分析結果
  - `/artifacts/`: ビルド・配布成果物
  - `/logs/`: 各種実行ログ

### `/scripts/`
- **用途**: 開発・運用スクリプト
- **ルール**:
  - 実行可能ファイルには実行権限を付与
  - 用途が明確なファイル名を使用

### `/worker/`
- **用途**: Git worktreeによる並列開発ワークスペース
- **ルール**:
  - Git管理対象外（`.gitignore`で除外）
  - Claude CLI並列実行時のファイル競合回避用
  - Worktreeディレクトリの物理的分離による安全な並列開発
- **構造例**:
  ```
  worker/
  ├── worktree_01/    # 機能A開発用worktree
  ├── worktree_02/    # 機能B開発用worktree
  └── worktree_03/    # 機能C開発用worktree
  ```
- **参考文書**: [memory-bank/git_worktree_parallel_development_verified.md](../../memory-bank/git_worktree_parallel_development_verified.md)

### `/dev-tools/`
- **用途**: 開発ツール・外部リポジトリ（Docker永続化用）
- **ルール**:
  - Git管理対象外（`.gitignore`で除外）
  - Dockerコンテナ再作成時もデータ保持のためworkspace内に配置
  - MCPサーバや外部ツールのインストール先
- **構造**:
  ```
  dev-tools/
  ├── mcp-servers/      # MCPサーバインストール先
  ├── external-repos/   # 外部リポジトリクローン先
  └── knowledge-base/   # 開発ナレッジ・メモ保存先
  ```
- **使用例**:
  ```bash
  # MCPサーバのインストール
  cd dev-tools/mcp-servers
  git clone https://github.com/modelcontextprotocol/servers.git
  ```

## 🚫 禁止事項

1. **ルートディレクトリへの直接ファイル配置禁止**
   - 例外: README.md, LICENSE, pyproject.toml, .gitignore等の設定ファイル

2. **既存ディレクトリ構造の変更禁止**
   - 変更が必要な場合は、チームで議論し、このドキュメントを更新

3. **一時ファイルのコミット禁止**
   - `.tmp`, `.log`, `.cache`等は`.gitignore`に追加

## ✅ ベストプラクティス

1. **新しいファイルを作成する前に**:
   - このドキュメントを確認
   - 適切な配置場所を決定
   - 不明な場合はチームに相談

2. **ドキュメント作成時**:
   - 番号付きディレクトリの用途を理解
   - 実装前は`01-03`、実装後は`04-05`を使用
   - 参考資料は`90-91`を使用

3. **コード作成時**:
   - モジュールの責務を明確に
   - 適切なレイヤーに配置
   - テストを同時に作成

## 🔧 検証ツール

ディレクトリ構造の検証は以下のスクリプトで実施:
```bash
python scripts/check_directory_structure.py
```

## 📝 更新履歴

- 2025-06-04: 初版作成、ディレクトリ構造を標準化
- 2025-06-07: `/worker/`ディレクトリ追加（Git worktree用）
- 2025-06-07: `/dev-tools/`ディレクトリ追加（Docker永続化用）