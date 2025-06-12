# 階層型Claude Agent運用パターン

## 概要
tmux環境における階層型Claude Agent組織の設計・運用パターンを体系化。大規模タスクの効率的な分解・実行・品質管理を実現する。

## 基本パターン

### 1. 三層階層パターン（推奨）

```
Layer 1: Strategic (戦略層)
├─ Project Manager (全体統括・意思決定)

Layer 2: Tactical (戦術層) 
├─ Task Manager (実行系統管理)
├─ Review Manager (品質管理系統)

Layer 3: Operational (実行層)
├─ Specialist Workers (専門作業実行)
```

#### 適用ケース
- 複雑な開発プロジェクト
- 品質重視のタスク
- リスク管理が重要な作業

### 2. 扁平二層パターン

```
Layer 1: Coordination (調整層)
├─ Coordinator Agent

Layer 2: Execution (実行層)  
├─ Worker A, Worker B, Worker C
```

#### 適用ケース
- 単純な並列タスク
- 迅速な実行が優先
- オーバーヘッド最小化

## 組織設計原則

### 1. 単一責任の原則
- 各Agentは明確に定義された単一の責任を持つ
- 役割の重複を避け、責任境界を明確化
- 専門性に基づく最適な作業分担

### 2. 階層制御の原則
- 上位Agent → 下位Agentの一方向指示
- 下位Agent → 上位Agentの報告・確認要求
- 同レベルAgent間の直接通信は原則禁止

### 3. 分離検証の原則
- 実行系統と検証系統の独立性確保
- Task Manager ≠ Review Manager
- 客観的・批判的な品質評価体制

## 運用プロトコル

### 1. セッション開始プロトコル
```bash
# 1. 全ペインのコンテキストクリア
for i in {1..8}; do
    tmux send-keys -t $i '/clear' Enter
done

# 2. 組織図の確認・共有
# 3. タスクの初期分析・計画策定
# 4. 各層への役割説明・指示
```

### 2. タスク委譲プロトコル
```markdown
## Manager → Worker 指示テンプレート

**タスク概要**: [具体的なタスク内容]
**成果物**: [期待される具体的な成果物]
**制約条件**: [制限事項・注意点]
**報告先**: [完了報告の宛先]
**期限**: [完了予定時刻]

作業を開始してください。

<super-ultrathink/>
```

### 3. 品質確認プロトコル
```markdown
## Review Manager チェック項目

### Critical Issues (即座対応必要)
- [ ] セキュリティリスク
- [ ] データ喪失リスク  
- [ ] システム破壊リスク

### High Priority Issues (1-2時間以内)
- [ ] 機能仕様からの逸脱
- [ ] パフォーマンス問題
- [ ] 互換性問題

### Medium/Low Priority Issues (後日対応可)
- [ ] コードスタイル
- [ ] ドキュメント不備
- [ ] 軽微な改善提案
```

## 通信パターン

### 1. 指示送信パターン
```bash
# Step 1: コンテキストクリア (新タスク時)
tmux send-keys -t <target_pane> '/clear' Enter

# Step 2: メッセージ送信
tmux send-keys -t <target_pane> '<instruction_message>'

# Step 3: 送信実行
tmux send-keys -t <target_pane> Enter

# Step 4: 送信確認
tmux capture-pane -t <target_pane> -p | tail -10
```

### 2. 状態監視パターン
```bash
# 全ペイン状態の一括確認
function monitor_all_agents() {
    for i in {0..8}; do
        echo "=== Agent $i Status ==="
        tmux capture-pane -t $i -p | tail -5
        echo ""
    done
}
```

### 3. 緊急停止パターン
```bash
# 全Agentの作業停止
function emergency_stop() {
    for i in {1..8}; do
        tmux send-keys -t $i 'C-c'  # Ctrl+C
        tmux send-keys -t $i '/stop' Enter
    done
}
```

## エラーハンドリング

### 1. 通信エラー対処
```bash
# 送信失敗時の再試行
function retry_send() {
    local target_pane=$1
    local message=$2
    local max_retry=3
    
    for ((i=1; i<=max_retry; i++)); do
        tmux send-keys -t $target_pane "$message" Enter
        sleep 2
        
        # 応答確認
        local response=$(tmux capture-pane -t $target_pane -p | tail -5)
        if [[ $response == *"Thinking"* ]] || [[ $response == *">"* ]]; then
            echo "Send successful on attempt $i"
            return 0
        fi
    done
    
    echo "Send failed after $max_retry attempts"
    return 1
}
```

### 2. Agent無応答対処
```bash
# Agent無応答時の対処
function handle_unresponsive_agent() {
    local pane=$1
    
    # 1. 状態確認
    tmux capture-pane -t $pane -p | tail -20
    
    # 2. 強制リセット
    tmux send-keys -t $pane 'C-c' Enter
    tmux send-keys -t $pane '/clear' Enter
    
    # 3. 再開指示
    tmux send-keys -t $pane '## Agent Reset - Please report status' Enter
}
```

## 性能最適化

### 1. 並列処理の最大化
- 独立性の高いタスクの同時実行
- I/O待機時間の有効活用
- 依存関係を考慮した実行順序

### 2. 通信オーバーヘッドの最小化
- 不要な状態確認の削減
- バッチ処理による通信回数削減
- 効率的なメッセージフォーマット

### 3. リソース管理
- ペイン数とタスク複雑度のバランス
- メモリ使用量の監視
- CPU負荷の分散

## 応用パターン

### 1. プロジェクト開発パターン
```
Project Manager
├─ Architecture Agent (設計)
├─ Development Manager
│   ├─ Frontend Developer
│   ├─ Backend Developer  
│   └─ Database Developer
└─ QA Manager
    ├─ Test Engineer
    ├─ Security Tester
    └─ Performance Tester
```

### 2. 文書作成パターン
```
Editor-in-Chief
├─ Content Manager
│   ├─ Research Writer
│   ├─ Technical Writer
│   └─ Copy Writer
└─ Review Manager
    ├─ Technical Reviewer
    ├─ Language Reviewer
    └─ Fact Checker
```

### 3. データ処理パターン
```
Data Pipeline Manager
├─ Ingestion Manager
│   ├─ Source A Processor
│   ├─ Source B Processor
│   └─ Source C Processor
└─ Quality Manager
    ├─ Data Validator
    ├─ Format Checker
    └─ Integrity Verifier
```

## 成功要因

1. **明確な役割定義**: 各Agentの責任範囲の明確化
2. **効率的な通信**: 技術的制約を考慮した通信プロトコル
3. **品質保証**: 独立した検証体制の確立
4. **リスク管理**: 早期発見・対処の仕組み化
5. **継続改善**: 実行結果からの学習・最適化

## 制約・限界

1. **技術的制約**: tmux-Claude間通信の同期問題
2. **スケーラビリティ**: ペイン数増加に伴う管理複雑化
3. **状態管理**: 各Agentの状態把握の困難性
4. **エラー伝播**: 一部Agent障害の全体への影響

## 関連ドキュメント
- [Claude Agent組織化実験報告書](claude_agent_organizational_experiment_report.md)
- [tmux-Claude間インタラクション・トラブルシューティング](tmux_claude_interaction_troubleshooting.md)
- [AI Agent委託パターン](ai_agent_delegation_patterns.md)

---
**パターン検証**: 9ペイン階層組織での実証実験済み  
**適用実績**: ファイル整理タスク、品質管理プロセス  
**更新履歴**: 2025-06-11 初版作成