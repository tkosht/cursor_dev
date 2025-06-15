# Cogneeナレッジ検索最適化戦略

**作成日**: 2025-06-15  
**作成者**: Claude Agent (Knowledge/Rule Manager)  
**目的**: 検討モレ・思慮の浅さを防ぐための体系的検索アプローチ  
**適用範囲**: 全Claude Agentのナレッジアクセス活動  

---

## 🎯 検索最適化の核心問題

### 典型的な失敗パターン
1. **単一キーワード依存**: 「TDD」だけで検索 → 関連概念を見逃す
2. **表層的検索**: 最初の結果で満足 → 深い洞察を逃す  
3. **文脈無視**: 状況に応じた検索戦略なし → 不適切な情報取得
4. **体系性欠如**: 場当たり的検索 → 全体像を見失う

---

## 🔍 カテゴリ・文脈・条件の活用戦略

### 1. カテゴリ活用による網羅的検索

#### 検索タイプ別の特性理解
```yaml
search_types:
  GRAPH_COMPLETION:
    特性: AIが文脈理解して包括的回答生成
    用途: 概念説明、手順解説、総合的理解
    カテゴリ活用: 暗黙的に関連カテゴリを含む
  
  INSIGHTS:
    特性: ノード間の関係性を可視化
    用途: 構造理解、依存関係把握、影響分析
    カテゴリ活用: カテゴリ階層構造を明示
  
  CHUNKS:
    特性: 生の情報チャンクを返す
    用途: 詳細確認、原文参照、包括収集
    カテゴリ活用: 同一カテゴリ内を横断検索
  
  CODE:
    特性: コード関連情報をJSON形式で返す
    用途: 実装詳細、コード構造、技術仕様
    カテゴリ活用: 技術カテゴリに特化
```

### 2. 文脈を考慮した検索クエリ設計

#### 効果的なクエリパターン
```bash
# ❌ 悪い例: 文脈なし単一キーワード
mcp__cognee__search --search_query "エラー" --search_type "GRAPH_COMPLETION"

# ✅ 良い例: 文脈を含む複合クエリ
mcp__cognee__search --search_query "pytest実行時のエラー対処方法 TDD開発" --search_type "GRAPH_COMPLETION"

# ✅ さらに良い例: 段階的文脈追加
mcp__cognee__search --search_query "TDD pytest エラー カバレッジ 品質基準" --search_type "INSIGHTS"
```

### 3. 条件に応じた検索戦略選択

#### 状況別最適戦略マトリクス
| 状況 | 第1選択 | 第2選択 | 理由 |
|------|---------|---------|------|
| **新規概念学習** | GRAPH_COMPLETION | INSIGHTS | 全体像→構造理解 |
| **実装詳細確認** | CODE | CHUNKS | 技術詳細→原文確認 |
| **問題解決** | INSIGHTS | GRAPH_COMPLETION | 関係性→解決策 |
| **ルール確認** | CHUNKS | GRAPH_COMPLETION | 正確な原文→解釈 |
| **影響分析** | INSIGHTS | CHUNKS | 依存関係→詳細確認 |

---

## 🛡️ 検討モレ防止の体系的アプローチ

### Phase 1: 探索的検索（全体像把握）
```bash
# 1. 広範な概念検索
mcp__cognee__search --search_query "対象概念 関連分野 類似概念" --search_type "GRAPH_COMPLETION"

# 2. 関係性マッピング  
mcp__cognee__search --search_query "対象概念" --search_type "INSIGHTS"

# 3. カテゴリ横断確認
mcp__cognee__search --search_query "対象概念 ルール 実装 テスト" --search_type "CHUNKS"
```

### Phase 2: 深堀り検索（詳細理解）
```bash
# 1. 発見した関連概念を追加
mcp__cognee__search --search_query "対象概念 [Phase1で発見した関連語]" --search_type "GRAPH_COMPLETION"

# 2. エッジケース・例外確認
mcp__cognee__search --search_query "対象概念 例外 制約 注意点" --search_type "CHUNKS"

# 3. 実装例・ベストプラクティス
mcp__cognee__search --search_query "対象概念 実装例 ベストプラクティス" --search_type "CODE"
```

### Phase 3: 検証的検索（漏れ確認）
```bash
# 1. 否定形検索
mcp__cognee__search --search_query "対象概念 禁止 やってはいけない アンチパターン" --search_type "GRAPH_COMPLETION"

# 2. 代替案検索
mcp__cognee__search --search_query "対象概念 代替 別の方法 比較" --search_type "INSIGHTS"

# 3. フォールバック確認
grep -r "対象概念" memory-bank/ | grep -v "一般的\|基本的" | head -20
```

---

## 🧠 思慮の深さを確保する検索習慣

### 1. 多角的視点の確保
```yaml
viewpoints:
  technical:
    - 実装方法は？
    - 技術的制約は？
    - パフォーマンス影響は？
  
  organizational:
    - 組織ルールとの整合性は？
    - 他チームへの影響は？
    - 承認プロセスは？
  
  quality:
    - 品質基準を満たすか？
    - テスト戦略は？
    - 保守性は？
  
  risk:
    - セキュリティリスクは？
    - 失敗時の影響は？
    - 回復手段は？
```

### 2. 検索前の自問自答チェックリスト
- [ ] 何を知りたいのか明確か？
- [ ] どのカテゴリに属する情報か？
- [ ] どんな文脈で使用するのか？
- [ ] 関連する概念は何か？
- [ ] 反対概念・対立概念は何か？

### 3. 検索後の検証プロセス
- [ ] 得られた情報は質問に答えているか？
- [ ] 矛盾する情報はないか？
- [ ] 実装に必要な詳細は揃っているか？
- [ ] エッジケースは考慮されているか？
- [ ] 追加調査が必要な点はないか？

---

## 📊 実践例: TDD実装の網羅的調査

### Step 1: 初期探索
```bash
# 広範な概念理解
mcp__cognee__search --search_query "TDD テスト駆動開発 Red Green Refactor 品質" --search_type "GRAPH_COMPLETION"
# 結果: TDDの基本概念、サイクル、利点を理解
```

### Step 2: 関係性分析
```bash
# 構造的理解
mcp__cognee__search --search_query "TDD" --search_type "INSIGHTS"
# 結果: TDD → カバレッジ基準、品質ゲート、CI/CDとの関係を発見
```

### Step 3: 詳細収集
```bash
# 実装詳細
mcp__cognee__search --search_query "TDD pytest カバレッジ フィクスチャ モック" --search_type "CHUNKS"
# 結果: 具体的な実装手法、ツール設定、ベストプラクティスを取得
```

### Step 4: リスク確認
```bash
# アンチパターン
mcp__cognee__search --search_query "TDD 失敗 アンチパターン 過剰テスト" --search_type "GRAPH_COMPLETION"
# 結果: 避けるべきパターン、バランスの取り方を理解
```

### Step 5: 統合理解
```bash
# 組織的影響
mcp__cognee__search --search_query "TDD 組織導入 文化 チーム開発" --search_type "INSIGHTS"
# 結果: 組織レベルでの導入戦略、文化的課題を把握
```

---

## 🚀 継続的改善

### 検索効果測定指標
1. **網羅性**: 関連情報の取得率
2. **精度**: 必要情報の的中率  
3. **効率**: 検索時間対成果比
4. **深度**: 洞察の質的評価

### 改善サイクル
1. 検索ログの定期レビュー
2. 見逃しパターンの分析
3. クエリテンプレートの更新
4. チーム内知見共有

---

**この戦略により、表層的な理解を超えた深い洞察と、検討モレのない包括的な知識獲得を実現します。**