# 【緊急】Enter送信忘れ防止の絶対ルール

## 問題の深刻性
- tmux send-keys でメッセージ送信後、Enter送信を忘れる問題が繰り返し発生
- 既存ナレッジ（tmux_claude_interaction_troubleshooting.md）があるにも関わらず、実践で活用されていない
- 組織化実験で同じ失敗を繰り返している
- **これは品質管理の根本的な失敗である**

## 絶対遵守ルール（例外なし）

### 1. 必須パターン
```bash
# ❌ 絶対禁止：一行でのメッセージ+Enter送信
tmux send-keys -t <pane> '<message>' Enter

# ✅ 必須：分離送信パターン
tmux send-keys -t <pane> '<message>'
tmux send-keys -t <pane> Enter
```

### 2. 実行前チェックリスト（毎回必須）
- [ ] メッセージ内容確認
- [ ] 対象ペイン番号確認
- [ ] 分離送信パターンで実行
- [ ] Enter送信を忘れていないか確認

### 3. 実行後確認リスト（毎回必須）
- [ ] 受信側でメッセージ表示確認
- [ ] Thinking表示またはプロンプト待ち確認
- [ ] 応答開始確認（3秒以内）

### 4. 自動化関数（強制採用）
```bash
function safe_send() {
    local pane=$1
    local message="$2"
    
    echo "=== SAFE SEND to pane $pane ==="
    echo "Message: $message"
    
    # 1. メッセージ送信
    tmux send-keys -t $pane "$message"
    echo "✓ Message sent"
    
    # 2. Enter送信
    tmux send-keys -t $pane Enter
    echo "✓ Enter sent"
    
    # 3. 確認
    sleep 2
    echo "=== Verification ==="
    tmux capture-pane -t $pane -p | tail -5
}
```

### 5. Cogneeナレッジ活用の教訓（2025-06-11追加）
- **問題発生時は過去ナレッジ検索を最優先**: `mcp__cognee__search`で関連知見を即座検索
- **分離送信パターンはCogneeに既に記録済み**: tmux_claude_interaction_troubleshooting.mdに詳細手順あり
- **既存ナレッジを読まずに同じ失敗を繰り返すのは重大な品質管理違反**
- **Cogneeから学んだ正しい手順**: メッセージ送信 → Enter送信（別々に実行）

## 緊急修正手順

### 現在の組織化実験での即座修正
1. 各Managerペインの状態確認
2. Enter送信忘れの箇所を特定
3. 即座にEnter送信実行
4. 応答確認

### 標準化された送信プロセス
```bash
# Project Manager → Manager指示の標準フロー
function send_manager_instruction() {
    local manager_pane=$1
    local role_name="$2"
    local instruction="$3"
    
    local full_message="あなたは${role_name} (tmux-pane-${manager_pane})です。Project Managerより指示: ${instruction} <super-ultrathink/>"
    
    safe_send $manager_pane "$full_message"
}
```

## 品質管理への統合

### 1. コミット前チェック
- tmux送信関連のコードレビュー必須
- 分離送信パターンの確認

### 2. ドキュメント記載時
- tmux関連の手順は必ず分離送信で記載
- 一行送信の記載を禁止

### 3. 実験・検証時
- 送信確認を工程に組み込み
- 失敗時の即座修正プロセス確立

## 関連ドキュメント
- [tmux-Claude間インタラクション・トラブルシューティング](tmux_claude_interaction_troubleshooting.md)
- [Claude Agent組織化実験報告書](claude_agent_organizational_experiment_report.md)

---
**重要**: この問題は技術的な問題ではなく、プロセス遵守の問題である。既存ナレッジの実践活用を徹底すること。