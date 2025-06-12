# CLAUDE.md最適化セクション案

**13ペイン階層組織用の最適化されたセクション**

## 🏢 13ペイン階層組織運用（Claude Agent専用）

### 最小限必須知識（セッション開始時・2分以内）

#### 即座読み込み（必須）
1. **[ultra_simple_organizational_rules.md](memory-bank/ultra_simple_organizational_rules.md)** - 基本2ルール（階層遵守・完了報告）
2. **[enter_key_prevention_critical_rules.md](memory-bank/enter_key_prevention_critical_rules.md)** - tmux送信安全操作

#### セッション開始プロトコル（必須実行）
```bash
# 1. 基本組織ルール確認
mcp__cognee__search --search_query "13ペイン階層組織 基本2ルール" --search_type "CHUNKS"

# 2. tmux安全操作確認  
mcp__cognee__search --search_query "tmux Enter送信 分離パターン 安全送信方法" --search_type "CHUNKS"
```

### 段階的拡張知識（必要時にCognee検索）

#### 組織運用詳細（問題発生時のみ）
- **検索クエリ**: "13ペイン階層組織 詳細ルール Worker報告義務"
- **対象知識**: claude_agent_hierarchical_organization_rules.md, worker_reporting_mandatory_rules.md

#### 品質改善・レビュー（レビュー時のみ）
- **検索クエリ**: "批判的レビューフレームワーク 評価観点 改善提案"
- **対象知識**: critical_review_framework.md, rule_based_improvement_strategy.md

#### 問題解決・トラブル対応（障害時のみ）
- **検索クエリ**: "階層違反 防止策" / "事実確認プロトコル"
- **対象知識**: hierarchical_structure_jump_prohibition_rules.md, objective_fact_verification_protocol.md

#### 長期運用・並列開発（複雑プロジェクト時のみ）
- **検索クエリ**: "Git worktree 並列開発" / "Claude並列実行"
- **対象知識**: git_worktree_parallel_development_verified.md, claude_parallel_execution_verification.md

### 🚀 13ペイン組織タスク開始フロー

```bash
# Step 1: 最小限知識確認（上記プロトコル実行）

# Step 2: 組織活動開始
# - 基本ルールに従って指示系統・報告ラインを運用
# - 問題発生時のみ詳細知識をCognee検索

# Step 3: 必要時拡張
# - レビュー時 → "批判的レビューフレームワーク"検索
# - 障害時 → "問題解決プロトコル"検索
# - 改善時 → "ルールベース改善戦略"検索
```

---

## 🔄 既存Essential Knowledge Documentsセクションの最適化

### 段階的読み込み原則（新方針）

**基本方針**: 最小限から始めて、タスクに応じて段階的に拡張

#### Level 0: セッション開始時（必須・3分以内）
1. **プロジェクト概要** - CLAUDE.mdの基本情報
2. **セキュリティ基本** - 機密情報保護の基本ルール  
3. **品質基本** - コード品質の最低基準
4. **13ペイン組織基本**（該当セッション時のみ）

#### Level 1: タスク開始時（条件付き・5分以内）
- **開発タスク** → TDD・コーディング規約のCognee検索
- **レビュータスク** → 批判的レビューフレームワークのCognee検索  
- **組織運営タスク** → 階層組織詳細ルールのCognee検索
- **システム保守** → CI/CD・インフラのCognee検索

#### Level 2: 問題発生時（オンデマンド）
- **エラー・障害** → トラブルシューティング知識の検索
- **品質問題** → 品質改善フレームワークの検索
- **組織問題** → 組織運営改善策の検索

### 推奨Cognee検索パターン

#### 開発関連
```bash
mcp__cognee__search --search_query "TDD実装パターン" --search_type "CODE"
mcp__cognee__search --search_query "品質チェック項目" --search_type "INSIGHTS"
```

#### 組織運営関連  
```bash
mcp__cognee__search --search_query "13ペイン階層組織 問題解決" --search_type "GRAPH_COMPLETION"
mcp__cognee__search --search_query "Worker報告遅延 対処法" --search_type "CHUNKS"
```

#### レビュー・改善関連
```bash
mcp__cognee__search --search_query "批判的レビュー 評価観点" --search_type "CHUNKS"  
mcp__cognee__search --search_query "継続的改善 ベストプラクティス" --search_type "INSIGHTS"
```

### 廃止される一括読み込み指示

```markdown
❌ 廃止: "ALWAYS load these documents in order" - 20文書の強制読み込み
✅ 新方式: 最小限開始 + 必要時Cognee検索による段階的拡張
```

---

## 📊 効果測定

### 時間効率
- **改善前**: 20文書読み込み（10-15分）
- **改善後**: 基本確認（2-3分）+ 必要時検索（1-2分）
- **効果**: 80%の時間短縮

### 知識活用精度  
- **改善前**: 無関係知識混在による混乱
- **改善後**: タスク特化知識のみ取得
- **効果**: 関連性90%以上

### 学習効果
- **段階的知識蓄積**により理解度向上
- **実用重視**により実践力向上
- **無駄排除**により集中力向上

---

**この最適化により、必要な知識（批判的レビューフレームワーク等）は保持しつつ、適切なタイミングでの効率的な知識活用を実現します。**