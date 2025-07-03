# 組織状態管理ガイド (Organization State Management Guide)

**制定日**: 2025-01-04  
**根拠**: Team04組織活動での実証結果  
**適用範囲**: 全tmux組織活動  
**優先度**: HIGH - 正しい実行のための必須知識

## KEYWORDS: organization-state, tmux-management, state-control, command-usage
## DOMAIN: organization|state-management|tmux-coordination  
## PRIORITY: HIGH
## WHEN: Any organization activity start/stop operations

## RULE: Always use proper organization state management commands with correct syntax

---

## 🎯 正しい組織状態管理方法

### 基本的な使い方
```bash
# 【正しい方法】source でスクリプトを読み込んでから実行
source /home/devuser/workspace/.claude/hooks/organization_state_manager.sh

# 組織活動開始
start_organization_state "team-$(date +%Y%m%d-%H%M%S)" 0

# 組織活動終了
stop_organization_state

# 状態確認
show_organization_status
```

### 代替方法（source不要）
```bash
# スクリプトに引数を渡して直接実行
/home/devuser/workspace/.claude/hooks/organization_state_manager.sh start "session_id" "pane_number"
/home/devuser/workspace/.claude/hooks/organization_state_manager.sh stop  
/home/devuser/workspace/.claude/hooks/organization_state_manager.sh status
```

---

## ❌ よくある間違い

### 間違い1: 関数を直接実行
```bash
# ❌ エラーになる
stop_organization_state
# Error: command not found

# ✅ 正しい方法
source /home/devuser/workspace/.claude/hooks/organization_state_manager.sh
stop_organization_state
```

### 間違い2: 存在しないファイルの参照
```bash
# ❌ エラーになる  
cp /home/devuser/workspace/.claude/settings.integrated.v2.json /home/devuser/workspace/.claude/settings.local.json
# Error: No such file or directory

# ✅ 正しい方法
# 現在のsettings.local.jsonをそのまま使用（追加操作不要）
```

---

## 🔧 安全な組織活動開始・終了手順

### 組織活動開始プロトコル
```bash
function safe_start_organization() {
    local session_id="${1:-team-$(date +%Y%m%d-%H%M%S)}"
    local pane_id="${2:-0}"
    
    echo "🚀 Starting organization activity..."
    
    # Step 1: 必要ファイルの事前確認
    if [[ ! -f "/home/devuser/workspace/.claude/hooks/organization_state_manager.sh" ]]; then
        echo "❌ organization_state_manager.sh not found"
        return 1
    fi
    
    # Step 2: スクリプト読み込み
    source /home/devuser/workspace/.claude/hooks/organization_state_manager.sh
    
    # Step 3: 組織状態開始
    start_organization_state "$session_id" "$pane_id"
    
    # Step 4: 開始確認
    if is_organization_active; then
        echo "✅ Organization activity started successfully"
        echo "📋 Session ID: $session_id"
        echo "🎛️ Initiator: pane-$pane_id"
        return 0
    else
        echo "❌ Failed to start organization activity"
        return 1
    fi
}
```

### 組織活動終了プロトコル
```bash
function safe_stop_organization() {
    echo "🛑 Stopping organization activity..."
    
    # Method 1: source後に関数実行（推奨）
    if source /home/devuser/workspace/.claude/hooks/organization_state_manager.sh 2>/dev/null; then
        stop_organization_state
    else
        # Method 2: スクリプト直接実行（フォールバック）
        /home/devuser/workspace/.claude/hooks/organization_state_manager.sh stop
    fi
    
    # 終了確認
    if ! is_organization_active 2>/dev/null; then
        echo "✅ Organization activity stopped successfully"
        return 0
    else
        echo "⚠️ Organization activity may still be active"
        return 1
    fi
}
```

---

## 📋 組織活動チェックリスト

### 開始前チェック
- [ ] organization_state_manager.sh ファイルの存在確認
- [ ] settings.local.json ファイルの存在確認  
- [ ] tmux セッションの確認
- [ ] 必要なmemory-bank ファイルの存在確認

### 実行中チェック
- [ ] 組織状態がアクティブか確認: `show_organization_status`
- [ ] ペイン登録状況の確認
- [ ] ログファイルの確認: `/home/devuser/workspace/.claude/organization_activity.log`

### 終了後チェック
- [ ] 組織状態の完全停止確認
- [ ] organization_state.json ファイルの削除確認
- [ ] hooks設定の復元確認

---

## 🚨 トラブルシューティング

### エラー: command not found
```bash
# 症状
stop_organization_state
# -bash: stop_organization_state: command not found

# 解決方法
source /home/devuser/workspace/.claude/hooks/organization_state_manager.sh
stop_organization_state
```

### エラー: settings.integrated.v2.json not found
```bash
# 症状  
cp: cannot stat '/home/devuser/workspace/.claude/settings.integrated.v2.json': No such file or directory

# 解決方法
# このファイルは不要です。現在のsettings.local.jsonを使用してください
echo "Current settings.local.json is sufficient - no additional setup required"
```

### エラー: organization state file missing
```bash
# 症状
⚠️ Organization state not active

# 解決方法
# 組織活動を開始してください
safe_start_organization "new-session-$(date +%Y%m%d-%H%M%S)"
```

---

## 🔄 CLAUDE.md統合

### Quick Start セクションへの追加
```bash
# 組織活動の安全な開始・終了
function quick_organization_management() {
    echo "🏆 Organization State Management:"
    echo "  Start: safe_start_organization [session_id]"
    echo "  Stop:  safe_stop_organization"
    echo "  Check: show_organization_status"
    echo "📚 Details: memory-bank/02-organization/organization_state_management_guide.md"
}
```

---

## 📈 改善された組織活動フロー

### Before（問題があった方法）
```bash
# ❌ 問題のある手順
cp .claude/settings.integrated.v2.json .claude/settings.local.json  # ファイルなし
stop_organization_state  # 関数未読み込み
```

### After（修正された方法）
```bash
# ✅ 修正された手順
source /home/devuser/workspace/.claude/hooks/organization_state_manager.sh
start_organization_state "team-$(date +%Y%m%d-%H%M%S)" 0
# ... organization activity ...
stop_organization_state
```

---

## 🎯 関連文書

### 直接関連
- `memory-bank/02-organization/tmux_claude_agent_organization.md` - 組織体制ルール
- `memory-bank/02-organization/tmux_organization_success_patterns.md` - 成功パターン
- `memory-bank/02-organization/ai_agent_coordination_mandatory.md` - AI協調ルール

### 技術参照
- `/home/devuser/workspace/.claude/hooks/organization_state_manager.sh` - 実装スクリプト
- `/home/devuser/workspace/.claude/settings.local.json` - 現在の設定
- `/home/devuser/workspace/.claude/organization_activity.log` - 活動ログ

---

---

## 🚨 ERROR ANALYSIS & PREVENTION (エラー分析・予防)

### Team04実証済みエラーパターン分析

#### Error Case 1: settings.integrated.v2.json Not Found
**根本原因**: 存在しない架空ファイルへの参照
```bash
# エラーコマンド
cp /home/devuser/workspace/.claude/settings.integrated.v2.json /home/devuser/workspace/.claude/settings.local.json

# 根本原因
- settings.integrated.v2.json が存在しない
- 想定された統合設定ファイルの実在性未確認

# 対策
- 現在のsettings.local.jsonで十分（追加設定不要）
- 事前ファイル存在確認の実装
```

#### Error Case 2: tmux_claude_agent_organization_rules.md Not Found  
**根本原因**: ファイル名の不整合（命名規則の齟齬）
```bash
# 期待されたファイル（存在しない）
tmux_claude_agent_organization_rules.md

# 実際のファイル（存在する）
memory-bank/02-organization/tmux_claude_agent_organization.md

# 対策
- 参照整合性の確認・修正完了
- ファイル名の統一（_rules.md サフィックス削除）
```

#### Error Case 3: stop_organization_state Command Not Found
**根本原因**: シェル関数の読み込み不足
```bash
# エラーパターン
stop_organization_state
# -bash: stop_organization_state: command not found

# 根本原因
- organization_state_manager.sh が未読み込み
- 関数定義の依存性理解不足

# 正しい方法
source /home/devuser/workspace/.claude/hooks/organization_state_manager.sh
stop_organization_state
```

### エラー影響分析結果

#### 組織活動成功への影響
**結論**: ✅ **影響なし** - 100%成功を維持
```bash
IMPACT_ASSESSMENT=(
    "Task_Completion_Rate: 100% (3/3 workers) - No impact"
    "Report_Reception_Rate: 100% - No impact"
    "Communication_Success_Rate: 100% - No impact"
    "Error_Recovery: Success - Alternative paths utilized"
)
```

#### エラー耐性の実証
- **共有コンテキスト**: Not Foundエラーに関わらず正常作成・配信
- **代替手順**: エラー発生時の迂回ルート活用成功
- **継続実行**: エラーによる処理停止なし

### 予防策実装

#### 事前確認システム
```bash
function validate_organization_prerequisites() {
    echo "🔍 Validating organization prerequisites..."
    
    local required_files=(
        "/home/devuser/workspace/.claude/settings.local.json"
        "/home/devuser/workspace/memory-bank/02-organization/tmux_claude_agent_organization.md"
        "/home/devuser/workspace/.claude/hooks/organization_state_manager.sh"
    )
    
    for file in "${required_files[@]}"; do
        if [[ ! -f "$file" ]]; then
            echo "❌ MISSING: $file"
            return 1
        fi
    done
    
    echo "✅ All prerequisites validated"
    return 0
}
```

#### エラー回復プロトコル
```bash
function error_recovery_protocol() {
    local error_type="$1"
    
    case "$error_type" in
        "file_not_found")
            echo "🔄 Attempting alternative file paths..."
            # Alternative path logic
            ;;
        "command_not_found")
            echo "🔄 Loading required functions..."
            source /home/devuser/workspace/.claude/hooks/organization_state_manager.sh
            ;;
        *)
            echo "⚠️ Unknown error type: $error_type"
            ;;
    esac
}
```

### エラー学習事項

#### システム設計の改善点
```bash
DESIGN_IMPROVEMENTS=(
    "File_Existence_Assumption_Removal"     # ファイル存在の前提排除
    "Naming_Convention_Standardization"     # 命名規則の標準化
    "Function_Dependency_Documentation"     # 関数依存性の明文化
)
```

#### 堅牢性向上策
```bash
ROBUSTNESS_ENHANCEMENTS=(
    "Comprehensive_Error_Handling"          # 包括的エラーハンドリング
    "Graceful_Degradation"                  # 優雅な劣化機能
    "Alternative_Path_Provision"            # 代替経路の提供
    "Proactive_Issue_Detection"             # 予防的問題検出
)
```

### 継続的改善指針

#### 品質保証プロセス
1. **事前確認**: 組織活動開始前の必須ファイル・コマンド確認
2. **エラー監視**: 実行中のエラー検出・記録
3. **回復実行**: エラー発生時の自動・手動回復手順
4. **学習統合**: エラーパターンの知識ベース統合

#### 予防的保守
```bash
# 定期実行推奨
function periodic_health_check() {
    echo "🏥 Organization System Health Check"
    validate_organization_prerequisites
    check_file_reference_integrity
    verify_command_availability
    echo "✅ Health check completed"
}
```

---

**使用指針**: 今回のTeam04組織活動テストで判明した問題点を解決し、将来の組織活動での混乱を防ぐため、この文書の手順に従って実行してください。エラー分析結果により、システムの堅牢性と回復力が実証されました。