# Knowledge Access Principles - MANDATORY
# 知識アクセス根本原則 - 絶対遵守

**作成日**: 2025-06-22  
**重要度**: ★★★★★ CRITICAL  
**適用範囲**: 全ての知識管理作業、ドキュメント作成、最適化作業

## KEYWORDS: knowledge-access, navigation, context-management, meta-cognition, optimization
## DOMAIN: meta-knowledge|knowledge-management|system-design
## PRIORITY: MANDATORY
## WHEN: All knowledge management tasks, documentation, optimization work
## NAVIGATION: CLAUDE.md → smart_knowledge_load() → this file (auto-loaded)

## RULE: Knowledge optimization means improving accessibility, NOT deletion

---

## 🎯 FUNDAMENTAL PURPOSE (根本目的)

### 知識管理システムの本質的目標
```
✅ 必要なときに必要なナレッジ・ルールを参照できること
✅ AIエージェントが適切な知識を把握してタスク実行できること  
✅ コンテキストオーバーフローでも重要情報にアクセス可能
✅ メタ認識による関連知識の自動発見
```

### 誤った目標（避けるべき）
```
❌ ファイル行数の削減それ自体
❌ 情報量の単純な圧縮
❌ アクセス性を犠牲にした「整理」
❌ 必要情報の削除による「最適化」
```

---

## 🚨 OPTIMIZATION REDEFINITION (最適化の再定義)

### ❌ 間違った最適化概念
```
最適化 ≠ 行数削減・内容削除
最適化 ≠ ファイル数減少
最適化 ≠ 情報の簡素化
最適化 ≠ 「読みやすさ」のための削除
```

### ✅ 正しい最適化概念  
```
最適化 = アクセス性向上・導線改善
最適化 = 検索効率化・発見可能性向上
最適化 = 重複解消と情報保全の両立
最適化 = コンテキスト管理の改善
最適化 = メタ認識機能の強化
```

### 最適化の具体的手法
```bash
# ✅ 推奨手法
1. 中央ハブ方式による情報集約
2. cross-reference による関連知識リンク
3. キーワード・ドメイン・優先度による構造化
4. 重複情報の統合（削除ではなく）
5. 導線設計による効率的ナビゲーション

# ❌ 禁止手法  
1. 内容削除による圧縮
2. 必要情報の省略
3. アクセスパスの断絶
4. 関連知識の分離
5. ユーザー承認なき情報削減
```

---

## 📊 INFORMATION SUFFICIENCY (情報十分性原則)

### 必要十分性の基準
```markdown
## 十分性チェックリスト
- [ ] タスク実行に必要な全情報が含まれているか？
- [ ] 関連知識への参照パスが確立されているか？
- [ ] エラー対応・例外処理の情報が含まれているか？
- [ ] 背景・理由・根拠が説明されているか？
- [ ] 実行例・パターン・アンチパターンが示されているか？

## 過剰性チェックリスト
- [ ] 同一情報の不必要な重複はないか？
- [ ] 古い・無効な情報が混在していないか？
- [ ] 現在の目的に関係ない詳細が含まれていないか？
- [ ] 複数箇所で管理すべき情報が一箇所に集中していないか？
```

### 情報削減時の必須確認事項
```bash
# 削除前必須チェック
1. ユーザー明示的承認の取得
2. 削除情報の依存関係調査
3. 代替参照パスの確立
4. 影響範囲の完全把握
5. 復旧可能性の確保

# 削除可能な情報
- 完全に重複している情報（他で参照可能）
- 明確に無効・過時になった情報
- ユーザーが明示的に削除承認した情報
```

---

## 🧭 ACCESS METHODOLOGY (アクセス方法論)

### 基本アクセスフロー
```bash
# Primary Access Path
CLAUDE.md → smart_knowledge_load() → domain files → specific knowledge

# Secondary Access Paths  
1. Cognee search → mcp__cognee__search "keyword" GRAPH_COMPLETION
2. File pattern search → find memory-bank/ -name "*keyword*.md"
3. Content search → grep -r "pattern" memory-bank/
4. Cross-reference → Related sections in files
```

### メタ認識による知識発見
```bash
# Auto-Discovery Mechanisms
1. Domain-based loading: security → security_rules + related patterns
2. Context-sensitive search: error → error_analysis + troubleshooting  
3. Priority-based filtering: MANDATORY → critical rules first
4. Relationship mapping: A → B → C knowledge chain discovery
```

### 効率的検索戦略
```bash
# 3-Stage Search Optimization
Phase 1: Keywords + Domain (1-3 seconds)
Phase 2: Semantic relationships (5-10 seconds)  
Phase 3: Comprehensive context (10-20 seconds)

# Search Targets
- Filename patterns
- Header keywords
- DOMAIN classifications
- PRIORITY levels
- Cross-references
```

---

## 🔗 NAVIGATION DESIGN (導線設計原則)

### 中央ハブ方式
```markdown
## Hub Structure
Central Hub (CLAUDE.md) 
├── Domain Hubs (00-core/, 01-cognee/, etc.)
├── Functional Hubs (Essential Commands, Strategic Operations)
└── Reference Hubs (Most Used Commands, Emergency Protocols)

## Hub Characteristics
- Single source of truth for domain
- Comprehensive information集約
- Clear outbound references
- Consistent update procedures
```

### Cross-Reference システム
```bash
# Reference Format Standards
## RELATED:
- memory-bank/XX-domain/related_file.md
- SEE_ALSO: specific_section_name
- PREREQUISITE: required_knowledge.md
- FOLLOWUP: next_step_guide.md

# Reference Quality Standards
- Specific section references (not just filenames)
- Bidirectional linking where appropriate
- Context-aware relationship descriptions
- Maintenance procedures for link integrity
```

### 導線の品質基準
```markdown
## Navigation Quality Metrics
1. **Discoverability**: Can users find relevant information within 3 steps?
2. **Completeness**: Are all necessary related topics linked?
3. **Currency**: Are references up-to-date and valid?
4. **Context**: Do references provide sufficient context for decision-making?
5. **Efficiency**: Is the path to information optimized for common use cases?
```

---

## ⚡ IMPLEMENTATION GUIDELINES (実装ガイドライン)

### 知識作成時の原則
```bash
# New Knowledge Creation
1. Determine optimal location (domain + priority)
2. Establish cross-references to related knowledge
3. Include keywords, domain, priority metadata
4. Provide clear examples and anti-patterns
5. Test discoverability through multiple access paths
```

### 知識更新時の原則
```bash
# Knowledge Update Process
1. Preserve all essential information
2. Improve structure and accessibility
3. Update cross-references and metadata
4. Verify no access paths are broken
5. Document changes and rationale
```

### 最適化プロジェクト実行時
```bash
# Optimization Project Protocol
1. Define optimization goals (accessibility improvement)
2. Inventory current information architecture
3. Identify access bottlenecks and gaps
4. Design improved navigation structure
5. Implement incrementally with verification
6. User validation before information removal
```

---

## 🔍 COMPLIANCE VERIFICATION (遵守検証)

### セルフチェック項目
```markdown
## Before Any Knowledge Management Work
- [ ] 本来の目的（アクセス性向上）を理解しているか？
- [ ] 削除ではなく構造化で問題解決を試みているか？
- [ ] 必要十分な情報量を維持する計画か？
- [ ] 複数の アクセスパスを確保しているか？
- [ ] ユーザー承認が必要な変更を特定しているか？

## After Knowledge Management Work
- [ ] 全ての必要情報にアクセス可能か？
- [ ] 関連知識との導線が維持されているか？
- [ ] メタデータと検索性が改善されているか？
- [ ] Cross-referenceが正しく機能するか？
- [ ] 変更による情報損失がないか？
```

### 品質保証プロセス
```bash
# Quality Assurance Steps
1. Access path testing: Can all information be reached?
2. Cross-reference validation: Do all links work?
3. Search functionality verification: Keywords and patterns effective?
4. User workflow testing: Common tasks still efficient?
5. Information completeness audit: No essential details lost?
```

---

## 🚨 ENFORCEMENT PROCEDURES (強制手順)

### 違反時の対応
```bash
# Violation Response Protocol
1. Immediate halt of information deletion
2. Assessment of potential information loss
3. Recovery procedures if needed
4. Root cause analysis of violation
5. Process improvement to prevent recurrence
```

### 予防措置
```bash
# Prevention Measures
1. Mandatory review of this document before optimization work
2. User consultation for any substantial changes
3. Incremental implementation with validation
4. Backup and recovery procedures
5. Clear documentation of all changes and rationale
```

---

## 📚 RELATED KNOWLEDGE

### 直接関連
- memory-bank/09-meta/progress_recording_mandatory_rules.md (記録原則)
- CLAUDE.md → AI-OPTIMIZED KNOWLEDGE FORMAT (記録形式)
- memory-bank/09-meta/knowledge_classification_framework.md (分類体系)

### 実装関連
- CLAUDE.md → smart_knowledge_load() function (自動ロード機能)
- CLAUDE.md → WORK MANAGEMENT PROTOCOL (作業管理)
- memory-bank/01-cognee/cognee_effective_utilization_strategy.md (検索戦略)

### 品質関連
- memory-bank/00-core/value_assessment_mandatory.md (価値評価)
- memory-bank/00-core/user_authorization_mandatory.md (ユーザー承認)

---

**重要**: この原則は知識管理システムの根幹をなす。如何なる「効率化」「最適化」もこの原則に違反してはならない。アクセス性の向上こそが真の最適化である。