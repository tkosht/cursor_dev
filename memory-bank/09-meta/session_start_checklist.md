# セッション開始チェックリスト（必須実行）

## 🚨 BEFORE ANY WORK: 3-STEP PROTOCOL

### Step 1: セッション初期化（30秒以内）

```bash
# === SESSION INITIALIZATION ===
今日の作業: [具体的な作業内容を1行で記述]
作業タイプ: [Cognee/Git/TDD/A2A/品質チェック/エラー対処]
予想作業時間: [XX分]
```

### Step 2: 知識インデックス確認（60秒以内）

| 作業タイプ | 必須参照先 | 確認済み |
|-----------|------------|----------|
| **Progress Recording** | memory-bank/09-meta/progress_recording_mandatory_rules.md | [ ] |
| **Memory Management** | memory-bank/01-cognee/memory_resource_management_critical_lessons.md | [ ] |
| **Cognee Expansion** | memory-bank/01-cognee/cognee_expansion_progress.md | [ ] |
| **Cognee関連** | memory-bank/01-cognee/knowledge_operations_manual.md | [ ] |
| **Git操作** | memory-bank/08-automation/git_worktree_parallel_development.md | [ ] |
| **TDD実装** | memory-bank/00-core/tdd_implementation_knowledge.md | [ ] |
| **A2A開発** | memory-bank/05-architecture/a2a_protocol_implementation_rules.md | [ ] |
| **品質チェック** | memory-bank/04-quality/critical_review_framework.md | [ ] |
| **エラー対処** | memory-bank/09-meta/knowledge_utilization_failure_analysis.md | [ ] |

### Step 3: 3秒ルール実装（作業前毎回）

**行動前の必須自問**:
1. ⚡ これは事実か推測か？
2. 📚 関連ナレッジを確認したか？
3. 🎯 より確実な方法はないか？

---

## 📋 作業中の継続チェック

### 推測検出警告システム

#### ❌ 使用禁止フレーズ（即停止）
- "たぶん" "おそらく" "思われる" "かもしれない"
- "だと思う" "推測すると" "恐らく" "多分"
- "なんとなく" "感覚的に" "経験上" "予想では"

#### ✅ 推奨表現パターン
- "事実確認が必要です"
- "追加調査を実行します"
- "検証後に判断します"
- "ドキュメント確認済み"
- "実測値に基づき"

### 知識参照トラッキング

```bash
# 参照したファイル（セッション中に更新）
REFERENCED_FILES=""

# 使用例
echo "memory-bank/cognee_knowledge_operations_manual.md" >> $REFERENCED_FILES
echo "確認完了: $(date)"
```

---

## 🎯 セッション終了プロトコル

### 必須レポート作成（5分以内）

```bash
echo "=== セッション終了レポート ==="
echo "作業内容: [完了した作業の要約]"
echo "参照ファイル数: [数値]"
echo "推測ベース判断: [回数] (目標: 0回)"
echo "事前確認実行率: [%] (目標: 100%)"
echo "新たに発見した知識: [あれば記述]"
echo "改善点: [次回のための教訓]"
```

### 品質確認チェック

- [ ] 推測ベース判断は0回だったか？
- [ ] 関連する全てのmemory-bankファイルを確認したか？
- [ ] 解決方法は事実に基づいているか？
- [ ] 同種問題の再発防止策は明確か？

### 知識アップデート（必要時のみ）

```bash
# 新しい知見があった場合
echo "新規知見: [発見内容]" >> memory-bank/session_insights_$(date +%Y%m%d).md
echo "適用先: [該当ファイル名]"
echo "更新理由: [なぜ重要か]"
```

---

## 🚨 緊急時プロトコル

### 推測表現を使ってしまった場合

1. **即座停止**: 現在の思考・作業を中断
2. **事実確認**: 関連するmemory-bankファイルを確認
3. **再実行**: 事実に基づいて思考・作業を再開
4. **記録**: 推測の内容と正しい事実を記録

### 事前確認をスキップしてしまった場合

1. **作業中断**: 現在の作業を一時停止
2. **チェックリスト実行**: Step 1-2を完全実行
3. **作業再開**: 知識確認完了後に作業継続
4. **原因分析**: なぜスキップしたかを記録

### 同種問題が再発した場合

1. **全作業停止**: セッション全体を一時中断
2. **根本原因分析**: knowledge_utilization_failure_analysis.mdを参照
3. **手順見直し**: 何が不足していたかを特定
4. **システム改善**: 再発防止策を実装

---

## 📊 効果測定（週次レビュー）

### 定量指標
- 推測フレーズ使用回数/週（目標: 0回）
- 事前確認実行率（目標: 100%）
- 問題解決時間の短縮率（目標: 30%向上）
- memory-bank活用ファイル数/セッション（目標: 3+）

### 定性指標
- 知識活用による新たな発見
- 効率性向上の実感
- 推測ベース行動の減少実感
- 問題解決精度の向上実感

---

**このチェックリストを毎セッション実行することで、知識活用の習慣化と推測ベース行動の根絶を実現します。**