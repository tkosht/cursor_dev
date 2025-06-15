# ナレッジ分類フレームワーク - 汎用版

**作成日**: 2025-06-13  
**目的**: memory-bank/knowledge/ 配下の全ナレッジの統一的分類体系

## 🏗️ 7軸分類システム

### 1. Category（技術領域）
**目的**: 知識の技術的分野を特定
```markdown
- system-design: アーキテクチャ、設計パターン
- development: プログラミング、フレームワーク、ツール
- operations: デプロイ、監視、インフラ、保守
- management: プロジェクト管理、プロセス、ワークフロー
- quality: テスト、レビュー、品質保証
- security: セキュリティ、コンプライアンス、プライバシー
- data: データベース、分析、機械学習
- ui-ux: インターフェース、ユーザー体験
```

### 2. Problem（解決課題）
**目的**: どんな問題を解決するかを明確化
```markdown
- complexity: 複雑性管理、over-engineering, technical debt
- efficiency: パフォーマンス、生産性、リソース最適化
- quality: バグ、品質低下、信頼性問題
- collaboration: コミュニケーション、チーム連携、知識共有
- scalability: 拡張性、成長対応、負荷対策
- maintenance: 保守性、可読性、長期運用
- security: 脆弱性、コンプライアンス違反
- delivery: 納期遅延、リリース問題、デプロイ困難
```

### 3. Context（適用環境）
**目的**: どんな状況で使用するかを特定
```markdown
- ai-assisted: AI支援開発、自動化ツール使用
- traditional: 従来手法、人力中心
- legacy: レガシーシステム、既存資産活用
- greenfield: 新規開発、ゼロから構築
- team: チーム開発、協働環境
- solo: 個人開発、一人作業
- remote: リモートワーク、分散チーム
- enterprise: 大企業、規制環境、複雑な組織
- startup: スタートアップ、迅速な変化
- open-source: OSS開発、コミュニティ
```

### 4. Scale（規模）
**目的**: 適用対象の規模を明確化
```markdown
- individual: 個人作業、学習、プロトタイプ（1人）
- team: チーム作業、小規模プロジェクト（2-10人）
- organization: 部門、中規模システム（10-100人）
- enterprise: 大企業、複雑システム（100人以上）
```

### 5. Lifecycle（ライフサイクル段階）
**目的**: プロジェクト・システムのどの段階で適用するか
```markdown
- planning: 企画、要件定義、設計、計画策定
- implementation: 開発、構築、テスト、統合
- deployment: リリース、デプロイ、移行
- operation: 運用、監視、サポート、保守
- evolution: 改善、拡張、リファクタリング、移行
```

### 6. Maturity（成熟度）
**目的**: 知識の検証レベル・信頼性を示す
```markdown
- experimental: 実験的、アイデア段階、未検証
- validated: 検証済み、小規模適用、効果確認
- standard: 標準的手法、広く適用、安定運用
- best-practice: ベストプラクティス、業界標準、推奨
```

### 7. Keywords（検索タグ）
**目的**: 具体的な検索語での発見を支援
```markdown
形式: `keyword1`, `keyword2`, `keyword3`
- 技術用語: `docker`, `kubernetes`, `pytest`
- 手法名: `tdd`, `ci-cd`, `code-review`
- パターン名: `mvc`, `repository-pattern`, `factory`
- ツール名: `git`, `jenkins`, `slack`
```

## 📋 記載テンプレート

```markdown
# [ナレッジタイトル]

**作成日**: YYYY-MM-DD  
**カテゴリ**: [Category軸から選択]  
**問題領域**: [Problem軸から選択]  
**適用環境**: [Context軸から選択]  
**対象規模**: [Scale軸から選択]  
**ライフサイクル**: [Lifecycle軸から選択]  
**成熟度**: [Maturity軸から選択]  
**タグ**: `keyword1`, `keyword2`, `keyword3`

## 📋 概要
[知識の要約]

## 🎯 適用コンテキスト
### 適用場面
[具体的な使用場面]

### 問題状況  
[解決対象の問題]

### 検索キーワード
[検索時のキーワード例]

[以下、実際の内容...]
```

## 🔍 検索戦略例

### 課題ベース検索
```bash
# 「複雑性管理の問題をチーム環境で解決したい」
grep -r "complexity.*team" memory-bank/knowledge/
```

### 技術領域ベース検索  
```bash
# 「システム設計の実験的手法を探している」
grep -r "system-design.*experimental" memory-bank/knowledge/
```

### 規模・段階ベース検索
```bash
# 「個人レベルの実装段階で使える手法」
grep -r "individual.*implementation" memory-bank/knowledge/
```

## 🎯 運用ルール

### 新規ナレッジ作成時
1. 7軸すべてでの分類を必須とする
2. 複数軸での分類が可能な場合は併記
3. 検索キーワードは5-10個程度を推奨

### 既存ナレッジ更新時
1. 分類の見直し・追加を定期的に実施
2. 利用実績に基づく分類精度向上
3. 関連ナレッジとの整合性確認

### 分類体系の進化
1. 新しい技術・手法の出現に応じて軸を拡張
2. 利用パターンに基づく分類の最適化
3. 四半期ごとの分類体系レビュー

---

*この分類フレームワークにより、ナレッジの体系的管理と効率的な検索・活用が実現されます。*