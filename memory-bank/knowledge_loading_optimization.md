# 知識読み込み最適化 - 13ペイン階層組織運用

**作成日**: 2025-06-11  
**目的**: 必要な知識の適切なタイミング読み込み  
**方針**: 最小限→必要時拡張

## 問題の分析

### 現状の課題
```
CLAUDE.mdの問題:
├── 20文書の一括読み込み指示
├── 関係ない知識の強制読み込み
├── 13ペイン組織運用に不要な知識混在
└── セッション開始時の過負荷
```

### 改善の方針
```
段階的読み込み:
├── Level 0: 最小限セット（即座読み込み）
├── Level 1: 基本セット（タスク開始時）
├── Level 2: 拡張セット（問題発生時）
└── Level 3: 専門セット（特定状況時）
```

## 知識分類と読み込みタイミング

### Level 0: 最小限セット（セッション開始時必須）

#### 1. 組織運用の基本
- `ultra_simple_organizational_rules.md`（新しいシンプル版）
- `enter_key_prevention_critical_rules.md`（tmux操作安全性）

#### 読み込みタイミング
```bash
# セッション開始時（1分以内）
mcp__cognee__search --search_query "13ペイン階層組織 基本ルール" --search_type "CHUNKS"
mcp__cognee__search --search_query "tmux Enter送信 分離パターン" --search_type "CHUNKS"
```

### Level 1: 基本セット（組織活動開始時）

#### 2. 組織運用詳細（必要時のみ）
- `claude_agent_hierarchical_organization_rules.md`（詳細ルール）
- `worker_reporting_mandatory_rules.md`（報告プロセス詳細）

#### 3. 問題解決支援（問題発生時のみ）
- `objective_fact_verification_protocol.md`（事実確認）
- `hierarchical_structure_jump_prohibition_rules.md`（階層違反対策）

#### 読み込みタイミング
```bash
# 組織活動開始時
mcp__cognee__search --search_query "Worker報告義務 詳細プロセス" --search_type "INSIGHTS"

# 問題発生時
mcp__cognee__search --search_query "階層違反 防止策" --search_type "GRAPH_COMPLETION"
```

### Level 2: 拡張セット（特定状況時のみ）

#### 4. 品質改善（レビュー時のみ）
- `critical_review_framework.md`（✅保持 - 有用）
- `rule_based_improvement_strategy.md`（改善戦略）

#### 5. プロジェクト管理（長期運用時のみ）
- `development_workflow_rules.md`（開発プロセス）
- `git_worktree_parallel_development_verified.md`（並列実行）

#### 読み込みタイミング
```bash
# レビュー・改善時
mcp__cognee__search --search_query "批判的レビューフレームワーク 評価観点" --search_type "CHUNKS"

# 長期プロジェクト時
mcp__cognee__search --search_query "並列開発 Git worktree" --search_type "INSIGHTS"
```

### Level 3: 専門セット（特殊状況時のみ）

#### 6. A2Aプロジェクト特有
- `a2a_protocol_implementation_rules.md`
- `a2a_critical_review.md`
- `tdd_implementation_knowledge.md`

#### 7. システム保守・運用
- `cognee_mandatory_utilization_rules.md`
- `ci_cd_optimization_rules.md`

#### 読み込みタイミング
```bash
# A2A開発時のみ
mcp__cognee__search --search_query "A2Aプロトコル実装" --search_type "CODE"

# システム保守時のみ
mcp__cognee__search --search_query "Cognee運用 ベストプラクティス" --search_type "GRAPH_COMPLETION"
```

## 最適化されたCLAUDE.md更新案

### 13ペイン階層組織セクション（新規追加）
```markdown
## 🏢 13ペイン階層組織運用（Claude Agent用）

### 最小限必須知識（セッション開始時）
- [ultra_simple_organizational_rules.md](memory-bank/ultra_simple_organizational_rules.md) - 基本2ルール
- [enter_key_prevention_critical_rules.md](memory-bank/enter_key_prevention_critical_rules.md) - tmux安全操作

### 詳細知識（必要時にCognee検索）
- 組織運用詳細: "13ペイン階層組織 詳細ルール"
- 問題解決: "階層違反 防止" / "報告義務 遵守"
- 品質改善: "批判的レビューフレームワーク"
- 長期運用: "並列開発 Git worktree"

### セッション開始プロトコル
```bash
# 1. 基本組織ルール確認（必須）
mcp__cognee__search --search_query "13ペイン階層組織 基本ルール" --search_type "CHUNKS"

# 2. tmux安全操作確認（必須）
mcp__cognee__search --search_query "tmux Enter送信 分離パターン" --search_type "CHUNKS"

# 3. 以降は必要時にCognee検索
```
```

### 既存セクションの最適化
```markdown
## 🚨 IMPORTANT: Essential Knowledge Documents

**段階的読み込み原則**: 最小限から始めて必要時に拡張

### セッション開始時（必須・2分以内）
1. プロジェクト概要の把握
2. セキュリティ・品質ルールの確認
3. 13ペイン組織基本ルール（該当セッションのみ）

### タスク開始時（条件付き）
- 開発タスク → TDD・コーディング規約
- レビュータスク → 批判的レビューフレームワーク
- 組織運営タスク → 階層組織詳細ルール

### 問題発生時（オンデマンド）
- Cognee検索による必要知識の取得
- 専門知識の段階的読み込み
```

## 実装方針

### 即座に実施すべき改善
1. **CLAUDE.mdの13ペイン組織セクション追加**
2. **段階的読み込みプロトコルの明記**
3. **不要な一括読み込み指示の削除**

### 保持すべき有用知識
- ✅ `critical_review_framework.md` - 汎用的に有用
- ✅ `rule_based_improvement_strategy.md` - 改善戦略
- ✅ `development_workflow_rules.md` - 開発プロセス
- ✅ 各種専門知識 - オンデマンド読み込み

### 削除対象（重複・不要）
- ❌ 過度に複雑なスクリプト群
- ❌ A2A専用かつ13ペイン無関係な知識
- ❌ 一括読み込み強制指示

## 期待される効果

### セッション開始時間
- 改善前: 20文書読み込み（10-15分）
- 改善後: 2文書読み込み（1-2分）
- **85%の時間短縮**

### 知識活用精度
- 改善前: 関係ない知識が混在
- 改善後: タスクに必要な知識のみ
- **関連性90%以上**

### 継続学習効果
- 必要時検索により段階的知識獲得
- 無駄な知識による混乱を防止
- 実用的な知識蓄積

---

**結論**: 批判的レビューフレームワークなど有用な知識は保持しつつ、読み込みタイミングを最適化。セッション開始時は最小限、必要時にCognee検索で拡張する段階的アプローチが最適。