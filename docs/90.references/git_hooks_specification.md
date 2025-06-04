# Git フック仕様書

最終更新: 2025-06-04

## 📋 概要

このドキュメントは、プロジェクトで使用されているGitフック（pre-commit hooks）の詳細仕様と設定方法を定義します。

## 🔧 フック構成

### フックファイルの場所
```
.git/hooks/pre-commit
```

### 実行順序
1. **セキュリティチェック** (`scripts/security_check.py`)
2. **構造チェック** (`scripts/simple_structure_check.py`) ※軽量版
3. **ドキュメント正確性検証** (`scripts/verify_accuracy.py`)
4. **批判的レビュー** (`scripts/critical_documentation_review.py`) ※条件付き

## 🛡️ 1. セキュリティチェック

### 目的
ステージングされたファイルから機密情報を検出し、意図しない情報漏洩を防止する。

### 実行コマンド
```bash
python3 scripts/security_check.py
```

### チェック対象
- **ファイル拡張子**: `.md`, `.py`, `.txt`
- **対象**: ステージングされたファイルのみ
- **除外パターン**:
  - `docs/.*/examples?/.*`
  - `docs/.*/sample.*`
  - `tests/.*test_.*\.py`
  - `memory-bank/.*/example.*`
  - `templates/.*`
  - `.*\.md\.template`

### 検出パターン

#### 特定パターン（高精度）
```python
# OpenAI APIキー
r"(sk-[a-zA-Z0-9]{48})"

# GitHubトークン
r"\b(ghp_[a-zA-Z0-9]{36}|gho_[a-zA-Z0-9]{36}|...)\b"

# Slackトークン
r"(?i)(xox[baprs]-\d+-\d+-[a-zA-Z0-9]+)"
```

#### 汎用パターン（コンテキスト考慮）
```python
# APIキー（引用符で囲まれた値のみ）
r'(?i)(api[_-]?key|apikey|api[_-]?token)["\']?\s*[:=]\s*["\']...'

# アクセストークン
r'(?i)(access[_-]?token|auth[_-]?token)["\']?\s*[:=]\s*["\']...'

# その他機密情報
r'(?i)(password|secret|key)["\']?\s*[:=]\s*["\']...'
```

### コンテキスト認識機能

#### Markdownコードブロック除外
```python
# フェンスコードブロック
r"```[\s\S]*?```"

# インデントコードブロック
r"^    .*$"

# インラインコード
r"`[^`\n]*`"
```

#### ドキュメント例の検出
```python
# ファイル名による判定
['example', 'sample', 'template', 'demo', 'tutorial']

# 行内容による判定
['# 例:', 'Example:', 'placeholder', 'dummy', 'fake-', 'mock-']
```

### エラーレベル分類

| レベル | 条件 | 動作 |
|--------|------|------|
| **エラー** | 実際の機密情報 | コミットブロック |
| **警告** | ドキュメント例・サンプル | 警告表示のみ |

### 実行結果例
```bash
✅ ステージングされたファイルに機密情報（エラーレベル）は見つかりませんでした。

# または

⚠️  docs/example.md で潜在的な機密情報が見つかりました（例/サンプル）:
  - APIキー (行 42) [警告のみ]

❌ src/config.py で機密情報が見つかりました:
  - OpenAI APIキー (行 15)
```

### バイパス方法
```bash
# 緊急時のみ使用（警告レベルのみの場合）
git commit --no-verify -m "message"
```

## 🏗️ 2. 構造チェック（軽量版）

### 目的
新規ディレクトリ作成のみをチェックし、プロジェクト構造の一貫性を保つ。

### 実行コマンド
```bash
python3 scripts/simple_structure_check.py
```

### チェック項目

#### A. 新規ディレクトリ作成の検出
- ステージングされたファイルから新規ディレクトリを検出
- 許可リストとの照合

#### B. 許可ディレクトリリスト
```python
allowed_dirs = {
    'app', 'tests', 'docs', 'scripts', 'memory-bank', 
    'knowledge', 'templates', 'docker', 'bin', 'node_modules',
    'htmlcov', '.git', '.venv', '__pycache__', '.pytest_cache',
    '.mypy_cache', '.specstory'  # 自動生成ディレクトリも許可
}
```

#### C. 軽量化による改善
- **誤検出の削減**: 根拠なき主張チェックを廃止（誤検出率100%のため）
- **開発効率向上**: `--no-verify`が不要
- **保守性向上**: 100行未満のシンプルな実装

### 実行結果例
```bash
# 正常時
✅ 構造チェック完了: 問題なし

# 新規ディレクトリ検出時
🚨 新規ディレクトリが検出されました
============================================================
1. 新規ディレクトリ作成: experimental (事前にユーザー許可が必要)

💡 対処方法:
1. ユーザーに許可を申請する
2. 既存ディレクトリ内に配置する
3. 一時的スキップ: git commit --no-verify
```

### 環境変数による制御
```bash
# スキップオプション
SKIP_STRUCTURE_CHECK=1 git commit -m "message"

# 完全スキップ
git commit --no-verify -m "message"
```

## 📋 3. ドキュメント正確性検証

### 目的
ドキュメント内のコマンド、ファイル参照、コード例の実在性と正確性を検証する。

### 実行コマンド
```bash
python scripts/verify_accuracy.py
```

### チェック項目

#### A. Makefileターゲット検証
```python
# ドキュメント内の `make <command>` コマンドを抽出
# Makefileに実在するターゲットかを確認
makefile_targets = extract_makefile_targets()
doc_make_commands = extract_make_commands_from_docs()
```

#### B. ファイル参照の検証
```python
# ドキュメント内のファイルパス参照を抽出
# 実際にファイルが存在するかを確認
r"[`「]([^`」\s]+\.(py|md|txt|json|yml|yaml))[`」]"
```

#### C. コマンド実行可能性
```python
# 記載されたコマンドが実行可能かを確認
r"`([a-zA-Z0-9_-]+(\s+[a-zA-Z0-9_.-]+)*)`"
```

#### D. 数値データの検証
```python
# カバレッジ、テスト数などの数値が実測値と一致するか
pytest_coverage = run_coverage_check()
documented_coverage = extract_coverage_from_docs()
```

### 実行結果例
```bash
🔍 Verifying Makefile targets...
# Note: 以下は存在しないターゲットの検出例
❌ ERROR: docs/setup.md:15 - Makefile target not found: 'make test'
   Available targets: up, down, bash, clean

🔍 Verifying file references...
⚠️  WARNING: README.md:42 - File not found: 'scripts/missing_script.py'

🔍 Verifying command executability...
✅ All documented commands are executable

🔍 Verifying numerical data...
❌ ERROR: README.md:67 - Coverage mismatch: documented 95%, actual 91.77%
```

## 🔬 4. 批判的レビュー (条件付き)

### 実行条件
```bash
# README.mdが変更された場合のみ実行
if git diff --cached --name-only | grep -q "README.md"; then
    python scripts/critical_documentation_review.py --target README.md
fi
```

### 目的
README.mdの変更に対するゼロベースでの客観的・批判的レビュー。

### 実行コマンド
```bash
python scripts/critical_documentation_review.py --target README.md
```

### レビュー観点

#### A. 正確性 (ACCURACY)
- コマンドの実行可能性
- ファイル参照の正確性
- 数値データの検証

#### B. 明確性 (CLARITY)
- 説明の理解しやすさ
- 曖昧な表現の検出
- 専門用語の適切な使用

#### C. 完全性 (COMPLETENESS)
- 必要な情報の不足
- セットアップ手順の網羅性
- エラーケースの考慮

#### D. 一貫性 (CONSISTENCY)
- 他ドキュメントとの整合性
- 表記揺れの検出
- 構造の統一性

### ユーザー確認
```bash
⚠️  Review completed. Errors must be fixed, warnings are advisory.
🤔 Continue with commit? (y/N)
```

レビュー完了後、ユーザーに継続確認を求める。

## ⚙️ フック管理

### フックの有効化/無効化

#### 無効化（緊急時）
```bash
# 一時的無効化
git config core.hooksPath /dev/null

# 元に戻す
git config --unset core.hooksPath
```

#### 個別スクリプトのスキップ
```bash
# セキュリティチェックのみスキップ（環境変数）
SKIP_SECURITY_CHECK=1 git commit -m "message"

# 完全スキップ
git commit --no-verify -m "message"
```

### フックのカスタマイズ

#### 設定ファイル
各スクリプトは設定ファイルに対応:
```
scripts/config/
├── security_check.yml      # セキュリティパターン設定
├── user_auth.yml          # 認証チェック設定
└── accuracy_verify.yml    # 正確性検証設定
```

#### 環境変数による制御
```bash
# 開発環境では警告のみ
export DEV_MODE=1

# CI環境では厳格チェック
export CI_MODE=1

# 特定チェックの無効化
export SKIP_USER_AUTH=1
export SKIP_ACCURACY_CHECK=1
```

## 🚨 トラブルシューティング

### よくある問題と解決方法

#### 1. セキュリティチェックの誤検出
```bash
# 問題: ドキュメント例がエラーになる
# 解決: ファイルパスまたは行内容で例外指定

# コード例マーカーを追加
# Example:
api_key = "your-api-key-here"  # ← 自動的に警告レベル
```

#### 2. ユーザー認証チェックの過剰反応
```bash
# 問題: 履歴ファイルの古い記述も検証される
# 解決: 除外パスの追加

# 一時的回避
SKIP_USER_AUTH=1 git commit -m "fix"
```

#### 3. 正確性検証の失敗
```bash
# 問題: ドキュメント更新後の数値不整合
# 解決: 実測値の再取得

python scripts/verify_accuracy.py --update-metrics
```

#### 4. フック全体の問題
```bash
# 緊急時の完全バイパス
git commit --no-verify -m "emergency fix"

# フック再設定
git config core.hooksPath .git/hooks
```

### デバッグ方法

#### 個別スクリプトのテスト
```bash
# セキュリティチェック
python scripts/security_check.py --debug

# ユーザー認証チェック
python scripts/check_user_authorization.py --verbose

# 正確性検証
python scripts/verify_accuracy.py --dry-run

# 批判的レビュー
python scripts/critical_documentation_review.py --target README.md --debug
```

#### ログ出力
```bash
# フック実行ログの保存
git commit -m "test" 2>&1 | tee hook_debug.log
```

## 📈 改善計画

### 短期改善 (1-2週間)
- [ ] ユーザー認証チェックの誤検出削減
- [ ] セキュリティチェックの除外パターン拡充
- [ ] 設定ファイルによるカスタマイズ機能
- [ ] より詳細なエラーメッセージ

### 中期改善 (1-2ヶ月)
- [ ] 機械学習による誤検出削減
- [ ] インタラクティブな設定ウィザード
- [ ] 段階的チェック（警告→エラー）
- [ ] パフォーマンス最適化

### 長期改善 (3-6ヶ月)
- [ ] IDE統合（VSCode拡張）
- [ ] リアルタイムチェック
- [ ] チーム設定の共有機能
- [ ] AIによる自動修正提案

## 📚 関連ドキュメント

- [プロジェクト品質管理システム](../../memory-bank/quality_management_system.md)
- [開発ワークフロー](../../memory-bank/development_workflow_rules.md)
- [セキュリティパターン](../../memory-bank/knowledge/security_patterns.md)
- [TDD実装知識](../../memory-bank/tdd_implementation_knowledge.md)

---

**注意**: このフック仕様は継続的に改善されています。問題や改善提案がある場合は、Issue作成またはプルリクエストを提出してください。