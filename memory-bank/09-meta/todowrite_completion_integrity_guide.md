# TodoWrite + Task Completion Integrity 統合ガイド

**作成日**: 2025-06-22  
**重要度**: ★★★★☆ HIGH  
**適用範囲**: 全てのTodoWrite使用時

## 🎯 統合目的

TodoWriteツールとTask Completion Integrityプロトコルを統合し、Todo作成時から完了条件ドリフト防止を実現します。

## 📋 強化されたTodo記録フォーマット (TCI統合版)

### 基本情報
```json
{
  "id": "task-unique-id",
  "content": "タスクの簡潔な説明",
  "status": "pending|in_progress|completed",
  "priority": "high|medium|low",
  "completion_criteria": {
    "must_conditions": [
      "必須達成条件1",
      "必須達成条件2"
    ],
    "should_conditions": [
      "推奨達成条件1", 
      "推奨達成条件2"
    ],
    "could_conditions": [
      "理想的条件1",
      "理想的条件2"
    ],
    "acceptance_tests": [
      "受け入れテスト1",
      "受け入れテスト2"
    ],
    "user_agreement": true,
    "defined_at": "2025-06-22T23:35:00"
  }
}
```

### 進捗追跡拡張
```json
{
  "progress_tracking": {
    "25_percent": {
      "timestamp": "2025-06-22T23:40:00",
      "must_status": "2/3 completed",
      "notes": "基本機能実装完了"
    },
    "50_percent": {
      "timestamp": "2025-06-22T23:45:00", 
      "must_status": "3/3 completed",
      "should_status": "1/2 completed",
      "notes": "テスト実装開始"
    },
    "75_percent": {
      "timestamp": "2025-06-22T23:50:00",
      "must_status": "3/3 completed",
      "should_status": "2/2 completed", 
      "could_status": "0/2 completed",
      "notes": "品質チェック実行"
    }
  }
}
```

## 🔧 TodoWrite使用時のワークフロー

### Phase 1: Todo作成時 (必須実行)
```bash
# 1. 基本Todo情報の定義
task_name="your-task-name"
content="Task description"
priority="high|medium|low"

# 2. 完了条件の事前定義 (MANDATORY)
echo "📋 Task Completion Criteria Definition Required"
python scripts/task_completion_check.py --task "$task_name" --define-criteria

# 3. 完了条件付きTodoWriteの実行
# (以下のJSON形式で完了条件を含めてTodoWriteを実行)
```

### Phase 2: 進捗更新時 (継続的実行)
```bash
# 定期的完了条件確認 (25%, 50%, 75%時点)
function update_todo_with_progress() {
    local task_name="$1"
    local progress_percent="$2"
    
    echo "📊 Progress Update: $progress_percent% complete"
    
    # 完了条件確認
    python scripts/task_completion_check.py --task "$task_name" --mode check
    
    # 進捗記録
    echo "Progress at $progress_percent%: $(date)" >> "progress_log_$task_name.txt"
    
    # TodoWriteで進捗更新
    # (statusを適切に更新し、progress_trackingセクションを追加)
}
```

### Phase 3: 完了判定時 (厳格な基準適用)
```bash
# 最終完了確認
function complete_todo_with_verification() {
    local task_name="$1"
    
    echo "🎯 Final Completion Verification"
    
    # 厳格モードでの完了確認
    if python scripts/task_completion_check.py --task "$task_name" --mode strict; then
        echo "✅ All completion criteria satisfied"
        
        # TodoWriteでstatus="completed"に更新
        # 完了時刻の記録
        
        # 完了レポート生成
        python scripts/task_completion_check.py --task "$task_name" --mode report
        
        return 0
    else
        echo "❌ Completion criteria not satisfied - task remains in_progress"
        return 1
    fi
}
```

## 📝 実践例: TCI統合TodoWrite

### 例1: 新機能開発タスク
```bash
# Step 1: 完了条件定義
python scripts/task_completion_check.py --task "api-endpoint-creation" --define-criteria

# 対話式で以下を定義:
# MUST: APIエンドポイントが正常動作する
# MUST: セキュリティチェックに合格する  
# MUST: 全テストが合格する
# SHOULD: API仕様ドキュメントが存在する
# SHOULD: エラーハンドリングが適切
# COULD: パフォーマンス最適化
# TEST: POST /api/users でユーザー作成ができる
# TEST: 不正データで適切にエラーを返す

# Step 2: TodoWrite実行
```

TodoWriteで以下のようなTodoを作成:
```json
[
  {
    "id": "api-endpoint-1",
    "content": "API endpoint creation with user management",
    "status": "pending", 
    "priority": "high",
    "completion_criteria_defined": true,
    "criteria_file": "api-endpoint-creation",
    "must_conditions_count": 3,
    "should_conditions_count": 2,
    "could_conditions_count": 1,
    "acceptance_tests_count": 2
  }
]
```

### 例2: バグ修正タスク
```bash
# Step 1: 完了条件定義
python scripts/task_completion_check.py --task "auth-bug-fix" --define-criteria

# MUST: 認証エラーが解決される
# MUST: 既存機能が正常動作を維持
# MUST: リグレッションテストに合格
# SHOULD: バグの根本原因が文書化される
# TEST: 正常な認証フローが動作する
# TEST: 異常な認証フローで適切にエラーを返す

# Step 2: TodoWrite実行
```

## 🔄 継続的監視と改善

### 自動化スクリプト
```bash
#!/bin/bash
# todo_completion_monitor.sh

# 全Todo項目の完了条件確認
echo "📋 Todo Completion Status Monitor"
echo "=================================="

# アクティブなTodoを検索
active_todos=$(python -c "
import json
# TodoReadの結果をパースして、アクティブなTodoを抽出
# (実際の実装では適切なAPIまたはファイル読み取りを使用)
")

# 各Todoの完了条件チェック
for todo in $active_todos; do
    if [ -n "$todo" ]; then
        task_name=$(echo $todo | jq -r '.content' | sed 's/[^a-zA-Z0-9]/-/g')
        echo "Checking: $task_name"
        python scripts/task_completion_check.py --task "$task_name" --mode check
    fi
done
```

### 品質メトリクス追跡
```bash
# 完了条件ドリフトの統計
function analyze_completion_drift() {
    echo "📊 Completion Criteria Drift Analysis"
    echo "====================================="
    
    # 全タスクのドリフト状況確認
    find memory-bank/09-meta/ -name "criteria_changes_*.json" | while read file; do
        task_name=$(basename "$file" .json | sed 's/criteria_changes_//')
        drift_count=$(jq length "$file")
        echo "Task: $task_name - Drift events: $drift_count"
    done
}

# 完了品質の統計
function analyze_completion_quality() {
    echo "📈 Completion Quality Analysis"
    echo "=============================="
    
    # 完了したタスクの品質スコア分析
    find memory-bank/09-meta/ -name "completion_report_*.md" | while read file; do
        task_name=$(basename "$file" .md | cut -d'_' -f3)
        # レポートから品質メトリクスを抽出
        must_score=$(grep "MUST Conditions:" "$file" | grep -o "[0-9]*%" | head -1)
        should_score=$(grep "SHOULD Conditions:" "$file" | grep -o "[0-9]*%" | head -1)
        echo "Task: $task_name - MUST: $must_score, SHOULD: $should_score"
    done
}
```

## 🎯 ベストプラクティス

### Todo作成時の必須チェックリスト
- [ ] 完了条件が MUST/SHOULD/COULD で階層化されている
- [ ] 受け入れテストが具体的で検証可能
- [ ] ユーザーとの完了条件合意が取れている
- [ ] 完了条件ファイルが生成されている
- [ ] Todo内容と完了条件が整合している

### 進捗更新時の必須チェックリスト
- [ ] 25%, 50%, 75%時点で完了条件を確認
- [ ] MUST条件からの乖離がないか確認
- [ ] 完了条件変更時は明示的な理由を記録
- [ ] ユーザー承認が必要な変更を適切に処理

### 完了判定時の必須チェックリスト
- [ ] 全MUST条件が100%達成
- [ ] 受け入れテストが全て合格
- [ ] SHOULD条件が80%以上達成
- [ ] 品質ゲートが全て合格
- [ ] 完了条件の変更履歴が適切

## 🔗 関連ファイル・ツール統合

### 必須ファイル
- **task_completion_integrity_mandatory.md**: 基本プロトコル
- **scripts/task_completion_check.py**: 完了条件検証ツール
- **completion_criteria_tracker.md**: 完了条件追跡ファイル

### 自動実行統合
```bash
# CLAUDE.mdのPRE_TASK_PROTOCOLに統合済み:
# "3. Task Completion Integrity: Define MUST/SHOULD/COULD conditions"
# "4. Acceptance Test creation: Create tests BEFORE implementation"  
# "5. User agreement: Confirm completion criteria with user"
```

### Cognee検索統合
```bash
# Cogneeでの検索キーワード
mcp__cognee__search "task completion integrity todowrite" GRAPH_COMPLETION
mcp__cognee__search "completion criteria drift prevention" RAG_COMPLETION
mcp__cognee__search "must should could conditions" CHUNKS
```

---

## 🎯 期待される効果

### 短期効果 (1-2週間)
- 完了条件の明確化による作業品質向上
- 完了条件ドリフト現象の削減
- ユーザーとの認識齟齬の減少

### 中期効果 (1-2ヶ月)  
- 一貫した高品質のタスク完了
- 完了条件設定スキルの向上
- プロジェクト全体の予測可能性向上

### 長期効果 (3-6ヶ月)
- 組織全体の品質文化醸成
- 完了基準の標準化・最適化
- 継続的品質改善の仕組み確立

---

**IMPORTANT**: このガイドは、TodoWriteツールの使用を前提として、Task Completion Integrityプロトコルを実際の作業フローに統合するための実践的な指針です。全てのTodo作成時に適用してください。