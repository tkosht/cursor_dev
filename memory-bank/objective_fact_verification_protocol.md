# 客観的事実確認プロトコル

**作成日**: 2025-06-11  
**更新日**: 2025-06-11  
**適用範囲**: tmux階層組織でのClaude Agent運用・問題判断  
**重要度**: 🚨**最重要（絶対遵守）**

## 目的

階層組織テストで発見された「推測による誤判断問題」の根絶を目的とする。客観的事実に基づく状況判断により、「技術的制約」等の安易な結論を防止し、正確な組織運営を実現する。

## 問題の背景

### 発見された重大な問題
- **事例**: Knowledge Manager(pane-3)が「技術的制約」と報告
- **実際**: Worker(pane-6,9,12)は全て挨拶タスクを完了し、報告も実施済み
- **原因**: Managerがtmux capture-paneによる推測的監視に依存
- **結果**: 完全に誤った状況判断と報告

### 誤判断の根本原因
1. **憶測判断**: 物理的確認なしの推測による結論
2. **不適切な監視手段**: tmux capture-paneの過信
3. **確認手順の不備**: 体系的な事実確認プロセスの欠如
4. **責任転嫁**: 安易な「技術的問題」への逃避

## 🚨 客観的事実確認の基本原則

### 根本原則
```
推測禁止 = 憶測・推定・想像による判断の絶対禁止
事実のみ = 客観的に検証可能な事実のみに基づく判断
確認優先 = 結論前に必ず物理的・直接的確認を実施
```

### 禁止事項（絶対遵守）
- ❌ **憶測による状況判断**: 「たぶん」「おそらく」による結論
- ❌ **推測による問題診断**: 根拠なき「技術的制約」判定
- ❌ **監視ツール過信**: tmux capture-pane結果のみでの判断
- ❌ **責任回避的判断**: 安易な外部要因への転嫁

## 事実確認プロトコル

### Level 1: 基本事実確認（必須）

#### 1.1 対象Agent応答確認
```bash
# 応答確認コマンド
tmux send-keys -t <target_pane> "echo 'response_check_$(date +%s)'"
tmux send-keys -t <target_pane> Enter

# 5秒待機後、応答確認
sleep 5
tmux capture-pane -t <target_pane> -p | tail -3
```

**判定基準**:
- ✅ **応答あり**: 5秒以内にecho結果が表示
- ⚠️ **応答遅延**: 5-30秒で応答
- ❌ **応答なし**: 30秒経過しても応答なし

#### 1.2 Agent状態確認
```bash
# プロセス状態確認
tmux list-panes -F "#{pane_index}: #{pane_current_command} #{pane_active}"

# セッション状態確認
tmux list-sessions | grep -v "no sessions"
```

**判定基準**:
- ✅ **正常**: プロセス実行中、セッション有効
- ⚠️ **注意**: 一部プロセス停止
- ❌ **異常**: プロセス停止、セッション無効

#### 1.3 最新活動履歴確認
```bash
# 最新20行の活動確認
tmux capture-pane -t <target_pane> -p | tail -20

# タイムスタンプ付き確認
tmux capture-pane -t <target_pane> -p | grep -E '\d{2}:\d{2}|\d{4}-\d{2}-\d{2}' | tail -5
```

**判定基準**:
- ✅ **活動中**: 過去10分以内の活動記録
- ⚠️ **非活動**: 10-30分前の最新活動
- ❌ **停止**: 30分以上活動記録なし

### Level 2: 詳細事実確認（問題疑い時）

#### 2.1 直接対話確認
```bash
# 直接応答要求
tmux send-keys -t <target_pane> "現在の状況を報告してください"
tmux send-keys -t <target_pane> Enter

# 3分間待機・応答確認
timeout 180 bash -c 'while true; do
    response=$(tmux capture-pane -t <target_pane> -p | tail -5)
    if echo "$response" | grep -qE "(報告|状況|完了)"; then
        echo "✅ 応答確認"
        break
    fi
    sleep 5
done'
```

#### 2.2 タスク実行状況確認
```bash
# タスク履歴の確認
tmux capture-pane -t <target_pane> -S -50 -E -1 | grep -iE "(完了|success|done|finished)"

# エラー履歴の確認
tmux capture-pane -t <target_pane> -S -50 -E -1 | grep -iE "(error|fail|exception|timeout)"
```

#### 2.3 システムリソース確認
```bash
# CPU・メモリ使用量確認
top -bn1 | head -5

# ディスク容量確認
df -h | grep -E "(/$|/tmp|/var)"

# ネットワーク接続確認
ping -c 3 8.8.8.8 > /dev/null && echo "✅ Network OK" || echo "❌ Network NG"
```

### Level 3: 最終事実確認（技術的問題疑い時）

#### 3.1 システム診断
```bash
# システムログ確認
journalctl --since "5 minutes ago" --priority=err

# プロセス詳細確認
ps aux | grep -E "(claude|python|node)" | head -10

# メモリ・スワップ確認
free -h
```

#### 3.2 外部依存確認
```bash
# API接続確認（該当する場合）
curl -I https://api.anthropic.com/v1/health 2>/dev/null | head -1

# Docker状態確認（該当する場合）
docker ps --format "table {{.Names}}\t{{.Status}}"

# tmux詳細状態確認
tmux show-options -g | grep -E "(default-shell|default-command)"
```

## 判定基準と対応

### 正常判定（技術的問題なし）
**条件**: 以下全てを満たす場合
- [ ] Agent応答が5秒以内
- [ ] プロセス・セッション正常
- [ ] 過去10分以内の活動記録
- [ ] エラーメッセージなし
- [ ] システムリソース正常

**対応**: 
- Workerに直接状況確認要求
- 報告義務の再確認
- 監視方法の見直し

### 注意判定（潜在的問題）
**条件**: 以下いずれかに該当
- [ ] Agent応答が5-30秒
- [ ] 活動記録が10-30分前
- [ ] 軽微なエラーメッセージ
- [ ] システムリソース使用率80%以上

**対応**: 
- 継続監視（15分間隔）
- 予防的対策の検討
- 状況改善の確認

### 異常判定（技術的問題あり）
**条件**: 以下いずれかに該当
- [ ] Agent応答が30秒以上なし
- [ ] プロセス停止・セッション無効
- [ ] 30分以上活動記録なし
- [ ] 重大なエラーメッセージ
- [ ] システムリソース不足

**対応**: 
- 即座に技術的問題と判定
- Project Managerへのエスカレーション
- 復旧手順の実行
- 根本原因の調査

## 事実確認チェックリスト

### 問題判定前の必須確認項目

#### 基本確認（必須）
- [ ] **Agent応答確認**: echo コマンドでの応答テスト
- [ ] **プロセス状態確認**: tmux list-panes での状態確認
- [ ] **活動履歴確認**: 過去20行の活動ログ確認
- [ ] **エラー有無確認**: エラーメッセージの存在確認

#### 詳細確認（問題疑い時）
- [ ] **直接対話確認**: 状況報告の直接要求
- [ ] **タスク実行確認**: 完了・エラー履歴の詳細確認
- [ ] **システム確認**: CPU・メモリ・ディスク・ネットワーク確認

#### 最終確認（技術的問題疑い時）
- [ ] **システム診断**: ログ・プロセス・リソースの総合確認
- [ ] **外部依存確認**: API・Docker・tmux設定の確認

### 結論記録フォーマット

#### 正常判定時
```
事実確認結果: 正常 ✅
確認項目: Agent応答○、プロセス状態○、活動履歴○、エラーなし
結論: 技術的問題なし。Worker報告待機継続。
実施時刻: [YYYY-MM-DD HH:MM:SS]
```

#### 異常判定時
```
事実確認結果: 異常 ❌
確認項目: Agent応答×、プロセス状態×、エラー: [具体的エラー内容]
結論: 技術的問題あり。即座にエスカレーション実施。
実施時刻: [YYYY-MM-DD HH:MM:SS]
```

## 教育・訓練プログラム

### Manager向け訓練

#### 必須スキル
1. **事実確認コマンド**: tmux操作・システム確認コマンドの習得
2. **判定基準理解**: 正常・注意・異常の明確な判定基準
3. **記録・報告**: 確認結果の正確な記録・報告スキル

#### 訓練手順
1. **理論学習**: 本プロトコルの完全理解
2. **実技練習**: 模擬問題での事実確認実践
3. **判定テスト**: 様々なシナリオでの判定テスト
4. **継続評価**: 月次での判定精度評価

### 組織全体訓練

#### 定期実施項目
- **週次**: 事実確認スキルの確認
- **月次**: 判定精度の測定・分析
- **四半期**: プロトコルの見直し・改善

## 効果測定

### 測定指標
- **誤判定率**: (誤判定数 / 全判定数) × 100
- **確認時間**: 事実確認完了までの平均時間
- **判定精度**: 正確な判定の割合
- **エスカレーション適正性**: 適切なエスカレーションの割合

### 目標値
- **誤判定率**: 0%（完全な事実ベース判定）
- **確認時間**: 3分以内（基本確認）
- **判定精度**: 100%（客観的基準による）
- **エスカレーション適正性**: 100%（適切な判断）

## 関連文書・参考資料

### 必読文書
- [worker_reporting_mandatory_rules.md](worker_reporting_mandatory_rules.md) - Worker報告義務
- [claude_agent_hierarchical_organization_rules.md](claude_agent_hierarchical_organization_rules.md) - 基本組織ルール
- [tmux_claude_interaction_troubleshooting.md](tmux_claude_interaction_troubleshooting.md) - tmuxトラブルシューティング

### 参考資料
- [enter_key_prevention_critical_rules.md](enter_key_prevention_critical_rules.md) - tmux操作ルール
- [critical_review_framework.md](critical_review_framework.md) - 批判的レビュー手法

## 改版履歴

| 版数 | 日付 | 変更内容 | 担当者 |
|------|------|----------|--------|
| 1.0 | 2025-06-11 | 初版作成 | Claude Agent |

---

**重要警告**: 安易な「技術的制約」判定は組織運営の重大な誤りである。必ず本プロトコルに従い、客観的事実に基づく正確な判断を実施すること。推測・憶測による判定は絶対禁止である。

**🚨 階層構造違反警告**: 本プロトコルはProject ManagerによるWorker直接確認を含んでおり、階層構造違反である。正しくは [hierarchical_fact_verification_protocol.md](hierarchical_fact_verification_protocol.md) の階層遵守版を使用すること。本プロトコルは参考・理論的基準としてのみ使用し、実際の運用では階層遵守版を必ず使用すること。