# 定型承認パターン自動化ルール

## KEYWORDS: approval-automation, decision-patterns, workflow-optimization, ai-agent-efficiency
## DOMAIN: automation|workflow|decision-making
## PRIORITY: HIGH  
## WHEN: File modifications, task execution, workflow decisions
## NAVIGATION: CLAUDE.md → smart_knowledge_load() → automation rules → this file

## RULE: 定型的な承認パターンを自動化し、重要な判断にのみ集中する

## 🎯 自動化戦略概要

### 効果期待値
- **時間短縮**: 定型承認90%削減（30秒 → 3秒）
- **集中力向上**: 重要判断にのみリソース集中
- **エラー削減**: 人為的承認ミス防止

### 3層承認システム
1. **AUTO_APPROVE**: 安全な操作の自動承認
2. **CONFIRM_REQUIRED**: 慎重確認が必要な操作  
3. **MANDATORY_REVIEW**: 絶対確認が必要な操作

## 📋 自動承認ルール定義

### ✅ AUTO_APPROVE パターン（自動承認）

```bash
# ドキュメント更新（安全性：高）
AUTO_APPROVE_PATTERNS=(
    "*.md"                    # Markdown文書更新
    "memory-bank/**/*.md"     # ナレッジベース更新
    "docs/**/*.md"           # ドキュメント更新
    "README.md"              # README更新
    "**/progress/*.md"       # 進捗記録更新
    "**/session_*.md"        # セッション記録
)

# テスト関連（安全性：高）
AUTO_APPROVE_TEST_PATTERNS=(
    "tests/**/*.py"          # テストファイル修正
    "**/test_*.py"          # テスト実装
    "pytest.ini"           # テスト設定（非破壊的）
)

# ログ・出力ファイル（安全性：高）
AUTO_APPROVE_OUTPUT_PATTERNS=(
    "output/**/*"           # ビルド出力
    "logs/**/*"            # ログファイル
    "*.log"                # ログファイル
    ".coverage"            # カバレッジレポート
)
```

### ⚠️ CONFIRM_REQUIRED パターン（慎重確認）

```bash
# 設定ファイル（影響度：中）
CONFIRM_REQUIRED_PATTERNS=(
    "*.json"               # 設定ファイル
    "*.yaml" "*.yml"       # YAML設定
    "*.toml"              # TOML設定
    "pyproject.toml"      # プロジェクト設定
    "Dockerfile*"         # Docker設定
    "docker-compose*.yml" # Compose設定
)

# スクリプト・実行ファイル（影響度：中）
CONFIRM_SCRIPT_PATTERNS=(
    "*.py"                # Python実行ファイル
    "*.sh"                # シェルスクリプト
    "scripts/**/*"        # スクリプトディレクトリ
    "Makefile"           # ビルド定義
)

# 依存関係（影響度：中）
CONFIRM_DEPENDENCY_PATTERNS=(
    "poetry.lock"         # 依存関係ロック
    "requirements*.txt"   # Python依存関係
    "package*.json"       # Node.js依存関係
)
```

### 🚨 MANDATORY_REVIEW パターン（絶対確認）

```bash
# セキュリティ関連（影響度：極高）
MANDATORY_REVIEW_PATTERNS=(
    ".env*"               # 環境変数ファイル
    "*key*" "*keys*"      # 認証キー
    "*secret*"           # シークレット
    "*token*"            # アクセストークン
    "*password*"         # パスワード
    "*.pem" "*.key"      # 証明書・秘密鍵
)

# システム設定（影響度：極高）  
MANDATORY_SYSTEM_PATTERNS=(
    ".git/**/*"          # Git設定
    ".github/**/*"       # GitHub Actions
    "ci/**/*"           # CI/CD設定
)
```

## 🤖 自動判断ロジック

### 判断フロー
```bash
function auto_approval_check() {
    local file_path="$1"
    local operation="$2"  # create|modify|delete
    
    # Phase 1: MANDATORY_REVIEW check (最優先)
    for pattern in "${MANDATORY_REVIEW_PATTERNS[@]}"; do
        if [[ "$file_path" == $pattern ]]; then
            echo "MANDATORY_REVIEW: 🚨 Security/System file detected"
            echo "Reason: File contains sensitive information or system configuration"
            return 3  # 絶対確認要求
        fi
    done
    
    # Phase 2: AUTO_APPROVE check
    for pattern in "${AUTO_APPROVE_PATTERNS[@]}" "${AUTO_APPROVE_TEST_PATTERNS[@]}" "${AUTO_APPROVE_OUTPUT_PATTERNS[@]}"; do
        if [[ "$file_path" == $pattern ]]; then
            echo "AUTO_APPROVE: ✅ Safe operation detected"
            echo "Reason: Documentation, testing, or output file"
            return 0  # 自動承認
        fi
    done
    
    # Phase 3: CONFIRM_REQUIRED (デフォルト)
    echo "CONFIRM_REQUIRED: ⚠️ Manual confirmation needed"
    echo "Reason: Configuration, script, or dependency file"
    return 1  # 確認要求
}
```

### 使用例
```bash
# ファイル操作前の自動判断
auto_approval_check "memory-bank/session_notes.md" "modify"
# → AUTO_APPROVE: ✅ Safe operation detected

auto_approval_check "app/config.json" "modify"  
# → CONFIRM_REQUIRED: ⚠️ Manual confirmation needed

auto_approval_check ".env.local" "create"
# → MANDATORY_REVIEW: 🚨 Security/System file detected
```

## 🔧 実装ガイドライン

### 1. 統合ポイント
```bash
# pre_action_check.py との統合
python scripts/pre_action_check.py --approval-auto "$file_path" "$operation"

# CLAUDE.md でのクイック判断
if auto_approval_check "$file" "modify"; then
    echo "✅ Proceeding with auto-approved operation"
else
    echo "⚠️ Manual confirmation required"
fi
```

### 2. 設定可能性
```bash
# プロジェクト固有パターンの追加
PROJECT_AUTO_APPROVE_PATTERNS=(
    "src/data/*.json"     # プロジェクト固有の安全パターン
)

# ユーザー設定での調整
AUTO_APPROVAL_LEVEL="conservative|standard|aggressive"
```

### 3. 学習機能（将来拡張）
```bash
# 承認履歴の記録
echo "$(date): AUTO_APPROVE: $file_path" >> .approval_history.log

# パターン改善の提案
# 「この操作は常に安全でしたが確認を求めました。自動承認に追加しますか？」
```

## 📊 期待効果測定

### 効果指標
- **承認時間削減**: 平均承認時間の測定（前後比較）
- **判断精度**: 自動承認された操作の問題発生率
- **ユーザー満足度**: 開発フロー改善実感

### 安全性確保
- **保守的設定**: 不明なパターンは必ず確認要求
- **ログ記録**: 全自動承認操作の記録
- **無効化オプション**: 自動承認機能の簡単な無効化

## 🔗 関連ファイル

### 直接関連
- **CLAUDE.md**: 基本ワークフローでの統合ポイント
- **scripts/pre_action_check.py**: セキュリティチェックとの統合
- **memory-bank/00-core/user_authorization_mandatory.md**: 承認ルールの基盤

### 実装参照
- **memory-bank/03-patterns/ai_agent_delegation_patterns.md**: 自動化パターンの応用
- **memory-bank/08-automation/ci_cd_optimization_rules.md**: 自動化のベストプラクティス

---

**重要**: この自動化ルールは開発効率向上のための支援ツールです。セキュリティや品質に疑いがある場合は、必ず手動確認を行ってください。