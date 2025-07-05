# 開発方法論統合ガイド

**作成日**: 2025-07-04  
**カテゴリ**: 方法論統合, ナビゲーション, 学習ガイド  
**問題領域**: methodology, navigation, learning  
**適用環境**: team, individual, ai-assisted  
**対象規模**: individual, team, organization  
**ライフサイクル**: all phases  
**成熟度**: validated  
**タグ**: `methodology`, `navigation`, `integration`, `learning-path`, `best-practices`

## 📋 概要

このプロジェクトで採用している開発方法論の統合ナビゲーションガイド。各方法論の特徴、適用場面、学習パスを体系的に整理し、最適な方法論の選択と組み合わせを支援します。

## 🎯 適用コンテキスト

### 適用場面
- **方法論選択**: タスクや状況に応じた最適な方法論の選択
- **学習計画**: 段階的な方法論習得の計画策定
- **統合活用**: 複数方法論の効果的な組み合わせ
- **オンボーディング**: 新メンバーの方法論理解支援

### 問題状況
- 複数の方法論が混在し選択に迷う状況
- 方法論の特徴と適用場面が不明確
- 学習順序や統合方法が分からない
- チーム内での方法論理解レベルの差

### 検索キーワード
`methodology guide`, `development methodology`, `best practices`, `learning path`, `methodology integration`

## 🚀 開発方法論マップ

### 📋 チェックリスト駆動実行（CDTE）
**概要**: TDD原則の拡張による体系的タスク実行管理  
**特徴**: MUST/SHOULD/COULD条件階層、Red-Green-Refactorサイクル拡張  
**適用**: 複雑タスク、品質保証、完了基準明確化  

**🎯 学習パス**:
1. **理解**: [フレームワーク概要](memory-bank/11-checklist-driven/checklist_driven_execution_framework.md)
2. **基礎**: [TDD拡張理解](memory-bank/11-checklist-driven/methodology_extension_from_tdd.md)
3. **実践**: [テンプレート活用](memory-bank/11-checklist-driven/templates_collection.md)
4. **応用**: [実装例研究](memory-bank/11-checklist-driven/implementation_examples.md)
5. **改善**: [検証システム](memory-bank/11-checklist-driven/verification_evaluation_mechanisms.md)

**🔗 統合リンク**:
- **Core**: [開発ワークフロー](memory-bank/00-core/development_workflow.md)
- **Quality**: [品質保証フレームワーク](memory-bank/04-quality/enhanced_review_process_framework.md)
- **Completion**: [タスク完了整合性](memory-bank/00-core/task_completion_integrity_mandatory.md)

---

### 🧪 テスト駆動開発（TDD）
**概要**: Red-Green-Refactorサイクルによるコード品質保証  
**特徴**: テストファースト、継続的リファクタリング  
**適用**: コード開発、設計改善、品質向上  

**🎯 学習パス**:
1. **基礎**: [TDD実装知識](memory-bank/00-core/tdd_implementation_knowledge.md)
2. **パターン**: [汎用TDDパターン](memory-bank/03-patterns/generic_tdd_patterns.md)
3. **実践**: [A2A TDD実装](docs/03.detail_design/a2a_tdd_implementation.md)
4. **統合**: [CDTEとの統合活用](memory-bank/11-checklist-driven/methodology_extension_from_tdd.md)

---

### 🤖 AI協調開発
**概要**: AI能力を活用した協働開発手法  
**特徴**: Claude Code活用、智能支援、自動化  
**適用**: AI支援プロジェクト、効率化、品質向上  

**🎯 学習パス**:
1. **基礎**: [CLAUDE.md](CLAUDE.md) - AI支援開発ガイド
2. **協調**: [AI協調ガイド](memory-bank/02-organization/ai_coordination_comprehensive_guide.md)
3. **制約**: [AI制約システム](memory-bank/03-patterns/ai_constraint_system_patterns.md)
4. **最適化**: [プロセス最適化](memory-bank/02-organization/tmux_organization_success_patterns.md)

---

### 🏆 競争的組織活動
**概要**: 複数チーム並列実行による高品質ソリューション創出  
**特徴**: 14役割体制、品質競争、多角評価  
**適用**: 重要課題、革新要求、最高品質実現  

**🎯 学習パス**:
1. **理解**: [競争的組織フレームワーク](memory-bank/02-organization/competitive_organization_framework.md)
2. **技術**: [tmux + git worktree](memory-bank/02-organization/tmux_git_worktree_technical_specification.md)
3. **役割**: [役割とワークフロー](memory-bank/02-organization/competitive_roles_workflows_specification.md)
4. **評価**: [品質評価フレームワーク](memory-bank/04-quality/competitive_quality_evaluation_framework.md)

## 🎲 方法論選択決定マトリクス

| 状況 | 複雑度 | 品質要求 | チーム規模 | 推奨方法論 |
|------|--------|----------|------------|------------|
| 新機能開発 | 中 | 高 | 1-5人 | **CDTE + TDD** |
| バグ修正 | 低-中 | 高 | 1-3人 | **CDTE テンプレート** |
| 重要課題 | 高 | 最高 | 5-15人 | **競争的組織活動** |
| 学習・研究 | 中 | 中 | 1-3人 | **CDTE + AI協調** |
| プロトタイプ | 低 | 中 | 1-2人 | **TDD + AI協調** |
| 大規模統合 | 高 | 高 | 10+人 | **CDTE + 競争的組織** |

## 📈 段階的学習ロードマップ

### 🔰 初心者向け（Week 1-2）
1. **TDD基礎**: Red-Green-Refactorサイクル理解
2. **CDTE入門**: チェックリスト駆動実行の基本概念
3. **AI協調基礎**: Claude Code基本活用
4. **実践**: 簡単なタスクでCDTEテンプレート使用

### ⚡ 中級者向け（Week 3-4）
1. **CDTE実装**: 複雑タスクでのフレームワーク適用
2. **統合活用**: TDD + CDTE統合パターン
3. **品質保証**: 検証システムとメトリクス活用
4. **チーム適用**: 小規模チームでの方法論導入

### 🏆 上級者向け（Week 5-8）
1. **カスタマイズ**: 組織固有のフレームワーク調整
2. **大規模適用**: 複数チーム・複雑プロジェクトでの活用
3. **競争的組織**: 最高品質要求時の高度な組織活動
4. **継続改善**: メトリクスベースの継続的最適化

## 🔧 実践的統合パターン

### Pattern 1: CDTE + TDD統合
```
1. CDTEでタスク全体設計
2. TDDで実装品質保証
3. CDTEで完了検証
4. 両方法論で学習統合
```

### Pattern 2: AI協調 + CDTE統合
```
1. AI支援でCDTEチェックリスト生成
2. AI協調でタスク実行加速
3. CDTEで品質保証維持
4. 統合学習でプロセス最適化
```

### Pattern 3: 競争的組織 + CDTE統合
```
1. CDTEで各チームの実行基準統一
2. 競争的環境で複数解決策開発
3. CDTEで解決策品質評価
4. 統合検証で最適解選択
```

## 📚 参考資料とリンク

### 核心ドキュメント
- **[CLAUDE.md](CLAUDE.md)**: AI支援開発のマスターガイド
- **[README.md](README.md)**: プロジェクト全体概要とナビゲーション
- **[開発ワークフロー](memory-bank/00-core/development_workflow.md)**: 統合開発フロー

### 方法論別詳細
- **CDTE**: [チェックリスト駆動実行](memory-bank/11-checklist-driven/README.md)
- **TDD**: [TDD実装知識](memory-bank/00-core/tdd_implementation_knowledge.md)
- **AI協調**: [AI協調ガイド](memory-bank/02-organization/ai_coordination_comprehensive_guide.md)
- **競争的組織**: [競争的組織フレームワーク](memory-bank/02-organization/competitive_organization_framework.md)

### 品質保証
- **[品質保証フレームワーク](memory-bank/04-quality/enhanced_review_process_framework.md)**
- **[タスク完了整合性](memory-bank/00-core/task_completion_integrity_mandatory.md)**
- **[コード品質ルール](memory-bank/00-core/code_quality_anti_hacking.md)**

---

## 🎯 まとめ

このプロジェクトの開発方法論は相互補完的に設計されており、状況に応じて最適な組み合わせを選択できます。初心者はTDD + CDTE基礎から始め、経験を積みながら高度な統合パターンや競争的組織活動に発展させることで、継続的な成長と品質向上を実現できます。

**Next Step**: 現在の状況に最適な方法論を選択し、対応する学習パスに従って実践を開始してください。