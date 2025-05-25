# cursor_dev - AI Research & Development Project

AIエージェント技術の研究・開発プロジェクトです。安全で標準的なプロトコルとライブラリを使用した実装を行います。

## 🚨 セキュリティ注意事項

**重要**: このプロジェクトでは、**公式かつ信頼できるライブラリのみ**を使用します。
- 非公式のサードパーティライブラリは重大なセキュリティリスクを伴います
- 常に公式ドキュメントと公式リポジトリから提供されるライブラリを使用してください

## 🎯 プロジェクト概要

### 現在のステータス
- **⚠️ 実装見直し中**: セキュリティ上の理由により非公式ライブラリを削除
- **✅ 技術調査完了**: エージェント間通信プロトコルの調査完了
- **✅ コード品質確保**: Linter・型チェック完了

## 🚀 開発環境

### 必要な環境
- Python 3.10+
- Poetry
- VSCode Dev Container（推奨）

### 環境構築

```bash
# 環境構築
poetry install

# 依存関係追加
poetry add <package>
```

## 📁 プロジェクト構造

```
cursor_dev/
├── memory-bank/                # AIの記憶領域
├── docs/                       # プロジェクトドキュメント
├── .devcontainer/              # Dev Container設定
└── README.md
```

## 📖 ドキュメント

### 基本ドキュメント
- **[memory-bank/projectbrief.md](memory-bank/projectbrief.md)**: プロジェクト概要
- **[memory-bank/progress.md](memory-bank/progress.md)**: 現在の進捗状況

## 🧪 開発・テスト

### コード品質チェック

```bash
# linterチェック
flake8 app/

# 型チェック  
mypy app/ --ignore-missing-imports

# フォーマット
black app/
```

## 🔒 セキュリティポリシー

1. **公式ライブラリのみ使用**: 信頼できる公式ソースからのみライブラリをインストール
2. **定期的な依存関係チェック**: `poetry show --outdated` による脆弱性確認
3. **機密情報の管理**: 環境変数・.envファイルによる適切な管理
4. **コード品質の維持**: linter・型チェック・テストの継続的実行

## 🤝 開発プロセス

このプロジェクトでは、Memory Bank駆動の開発プロセスを採用しています：

1. **調査・計画**: memory-bank/に知識・計画を蓄積
2. **実装**: 段階的な実装とテスト
3. **文書化**: 実装結果をmemory-bankに反映
4. **品質管理**: linter・テストによる品質確保

---

**🔒 セキュリティファースト**: 安全で信頼できる開発を最優先に進めています。
