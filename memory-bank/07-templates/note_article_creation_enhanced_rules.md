# Note記事作成強化ルール - AI間協調型コンテンツ制作システム

---
**KEYWORDS**: note記事, AI間協調, コンテンツ制作, 品質保証, テンプレート化
**DOMAIN**: content_creation|ai_coordination|quality_assurance
**PRIORITY**: MANDATORY
**WHEN**: Note記事作成プロジェクト実行時、AI間協調コンテンツ制作時
**LAST_UPDATED**: 2025-06-23

## 概要

本ルールセットは、Note記事作成における効率的なAI間協調プロセスと品質保証体制を定義する。今回のプロジェクト実証実験から得られた知見を体系化し、再現可能なフレームワークとして確立する。

## 🎯 RULE-001: 役割分散型記事制作プロトコル

### Trigger
- Note記事作成プロジェクトの開始時
- 複数のAIエージェントによる協調作業が必要な場合
- 品質・効率・創造性の同時最適化が求められる案件

### Scope
**Includes:**
- 企画、リサーチ、執筆、レビュー、最適化の全工程
- 複数の専門領域（マーケティング、ライティング、品質保証）
- AI間のコミュニケーション・進捗管理・最終統合

**Excludes:**
- 単発の短記事（1000文字未満）
- 緊急性が高く協調作業の時間がない案件
- 個人的な日記やエッセイ形式の記事

### Prerequisites
- tmux環境が利用可能
- 各専門分野のAIエージェントが配置可能
- プロジェクト管理・品質保証体制が整備済み

### Exceptions
**緊急時例外:**
- システム障害対応記事（速報性優先）
- トレンド対応記事（24時間以内公開必須）

**シンプル記事例外:**
- 定型フォーマット記事（商品レビュー等）
- 既存記事の更新・修正作業

### Action Protocol

#### Phase 1: 企画・戦略立案 (15分)
```bash
# 1. プロジェクト管理者による全体統括開始
tmux new-session -d -s "note-project-$(date +%Y%m%d)"
tmux send-keys "echo 'Note記事制作プロジェクト開始: $(date)'" Enter

# 2. 市場分析・ターゲット設定
tmux new-window -t note-project -n "market-research"
# → Market Research Specialistによる市場分析実行

# 3. コンテンツ戦略策定
tmux new-window -t note-project -n "content-strategy" 
# → Content Strategistによる記事企画・構成案作成
```

#### Phase 2: 協調執筆・制作 (45分)
```bash
# 4. 複数エージェントによる並列執筆
tmux new-window -t note-project -n "writing-team"
tmux split-window -h  # Writing Specialist
tmux split-window -v  # SEO Specialist
tmux select-pane -t 0
tmux split-window -v  # Visual Content Creator

# 5. リアルタイム進捗共有システム
# → memory-bank/09-meta/session_continuity_task_management.md への逐次更新
```

#### Phase 3: 品質保証・最適化 (30分)
```bash
# 6. 多角的品質レビュー
tmux new-window -t note-project -n "quality-review"
# → Quality Assurance Managerによる総合品質チェック

# 7. 最終統合・公開準備
tmux new-window -t note-project -n "final-integration"
# → Project Coordinatorによる最終取りまとめ
```

## 🚀 RULE-002: AI間コミュニケーション最適化プロトコル

### Trigger
- AI間での情報共有・意思決定が必要な時
- 作業の重複・矛盾を防ぐ必要がある時
- 進捗の透明性確保が必要な時

### Communication Standards

#### 必須報告フォーマット
```markdown
**報告元**: [pane-X(役職名)] - [担当タスク名]
**状態**: [完了/進行中/課題発生]
**成果物**: [具体的な成果物・ファイル名]
**次のアクション**: [具体的な次のステップ]
**他チームへの影響**: [他の担当者への影響・依存関係]
```

#### 情報共有ルール
1. **状況変化報告**: 作業開始・完了・課題発生時の即座報告
2. **相互依存確認**: 他エージェントの作業に依存する場合の事前確認
3. **品質基準共有**: 統一品質基準の全エージェント間での共有
4. **最終確認**: 各段階完了時の相互レビュー実施

## 🎯 RULE-003: 段階的品質保証システム

### Quality Gates Definition

#### Gate 1: 企画品質 (Planning Quality)
- [ ] ターゲット読者の明確な定義
- [ ] 競合記事分析の実施
- [ ] 独自価値提案の明確化
- [ ] SEOキーワード戦略の策定

#### Gate 2: コンテンツ品質 (Content Quality)
- [ ] 構成の論理性・一貫性
- [ ] 情報の正確性・最新性
- [ ] 読みやすさ・エンゲージメント要素
- [ ] ビジュアル要素の効果的活用

#### Gate 3: 技術品質 (Technical Quality)
- [ ] SEO最適化の実装
- [ ] レスポンシブデザイン対応
- [ ] アクセシビリティ配慮
- [ ] 表示速度・パフォーマンス

#### Gate 4: 公開前最終品質 (Pre-Publication Quality)
- [ ] 全体整合性の確認
- [ ] 法的リスクの確認
- [ ] ブランドガイドライン準拠
- [ ] 効果測定設定の完了

### Quality Metrics
```yaml
品質評価指標:
  読みやすさ: Flesch Reading Ease Score ≥ 60
  SEO品質: 基本SEO要素 100%実装
  オリジナリティ: コピペチェック 95%以上オリジナル
  エンゲージメント予測: 予想滞在時間 ≥ 3分
```

## 📊 RULE-004: 効果測定・継続改善システム

### Pre-Publication Setup
- [ ] Google Analytics設定
- [ ] note標準アナリティクス活用準備
- [ ] A/Bテスト要素の設定（可能な範囲で）
- [ ] エンゲージメント追跡指標の定義

### Post-Publication Analysis
- [ ] 公開後24時間以内の初期反応分析
- [ ] 1週間後の詳細パフォーマンス分析
- [ ] 月次での長期トレンド分析
- [ ] 改善点の抽出・次回記事への反映

### Success Criteria
```yaml
成功基準:
  アクセス数: 目標値に対する達成率
  エンゲージメント率: スキ率・ストック率
  読了率: 最後まで読まれた割合
  コンバージョン: フォロー・シェア・コメント
```

## 🔧 RULE-005: テンプレート・フレームワーク活用

### 記事構成テンプレート
```markdown
# [魅力的なタイトル] - [具体的ベネフィット]

## 導入部 (Hook)
- 読者の課題・関心への共感
- 記事で得られる価値の明示
- 読み進める動機の創出

## 本文 (構造化コンテンツ)
### セクション1: [基本概念・背景]
### セクション2: [具体的方法・ステップ]  
### セクション3: [実例・ケーススタディ]
### セクション4: [応用・発展的活用]

## 結論 (まとめ・行動喚起)
- 重要ポイントの再確認
- 読者への行動提案
- 継続的な価値提供の約束
```

### チェックリストテンプレート
- [ ] タイトル最適化（5つの法則適用）
- [ ] 見出し構造の整理
- [ ] ビジュアル要素の配置
- [ ] 内部・外部リンクの設置
- [ ] CTA（Call to Action）の配置
- [ ] メタデータ最適化

## 🎯 実装ガイドライン

### プロジェクト開始時の必須手順
1. **専門チーム編成**: 5-7名の専門AIエージェント配置
2. **作業環境設定**: tmux session・git branch・進捗管理ファイル
3. **品質基準共有**: 全チームメンバーでの品質基準・目標の確認
4. **タイムライン設定**: 各フェーズの明確な締切・マイルストーン

### 成功のキーファクター
- **専門性の活用**: 各分野のエキスパートによる高品質作業
- **透明性の確保**: 全プロセスの可視化・追跡可能性
- **反復改善**: 各プロジェクトでの学習・ルール更新
- **品質への妥協なし**: スピードよりも品質を重視する姿勢

## 関連リソース

- **テンプレート**: memory-bank/07-templates/note_article_template.md
- **チェックリスト**: memory-bank/07-templates/note_quality_checklist.md  
- **AI協調プロトコル**: memory-bank/02-organization/ai_agent_coordination_mandatory.md
- **品質評価システム**: memory-bank/04-quality/competitive_quality_evaluation_framework.md

## 継続的改善

本ルールは実践結果に基づいて継続的に更新される。各プロジェクト完了後、以下の観点で見直しを実施：

- 効率性の改善余地
- 品質向上のための追加要素
- AI間協調プロセスの最適化
- 新技術・新手法の導入可能性

---

*作成日: 2025-06-23*  
*根拠: Note記事制作プロジェクト実証実験結果*  
*適用範囲: AI間協調型コンテンツ制作全般*