# AMS-IG-005: アジャイル・TDDアプローチによる実装戦略

## 1. アジャイル開発プロセス

### 1.1 スプリント構成（2週間スプリント × 2回）

```
Sprint 1 (Week 1-2): 最小限の動作するペルソナ生成
Sprint 2 (Week 3-4): シミュレーションと可視化
```

### 1.2 デイリーサイクル
```
Morning:
- テストファースト（赤）
- 実装（緑）
- リファクタリング（青）

Afternoon:
- 統合テスト
- デモ準備
- 次の機能のテスト作成
```

## 2. TDD実装フロー

### 2.1 機能単位のTDDサイクル

```python
# Step 1: テストファースト（RED）
# tests/unit/test_persona_generator.py
class TestPersonaGenerator:
    def test_generate_single_persona_from_article(self):
        """記事から1体のペルソナを生成できる"""
        # Arrange
        article = "AIに関する技術記事..."
        generator = PersonaGenerator()
        
        # Act
        persona = generator.generate_single(article)
        
        # Assert
        assert persona is not None
        assert persona.id is not None
        assert persona.attributes is not None
        assert "interests" in persona.attributes
```

```python
# Step 2: 最小実装（GREEN）
# src/personas/generator.py
class PersonaGenerator:
    def generate_single(self, article: str) -> Persona:
        # 最小限の実装
        return Persona(
            id=str(uuid.uuid4()),
            attributes={"interests": []}
        )
```

```python
# Step 3: リファクタリング（REFACTOR）
# LLM統合を追加
class PersonaGenerator:
    def __init__(self, llm_client):
        self.llm = llm_client
    
    def generate_single(self, article: str) -> Persona:
        # 実際のLLM呼び出しを追加
        context = self.analyze_article(article)
        attributes = self.llm.generate_persona_attributes(context)
        return Persona(
            id=str(uuid.uuid4()),
            attributes=attributes
        )
```

### 2.2 垂直スライス開発

各スプリントで、エンドツーエンドの価値を提供：

**Sprint 1の垂直スライス**
```
1. 記事入力 → 単一ペルソナ生成 → 簡単な評価 → テキスト出力
   └─ 各ステップをTDDで開発
```

**Sprint 2の垂直スライス**
```
2. 複数ペルソナ → 相互作用 → シミュレーション → 可視化
   └─ Sprint 1の基盤上に構築
```

## 3. ユーザー設定 vs 動的生成の明確化

### 3.1 ユーザーが設定・指定できる項目

```python
@dataclass
class UserConfiguration:
    """ユーザーが制御可能な設定項目"""
    
    # === 必須設定 ===
    article: str                    # 評価対象の記事
    
    # === オプション設定（デフォルト値あり）===
    # ペルソナ関連
    population_size: int = 30       # ペルソナ生成数（5-100）
    persona_detail_level: str = "medium"  # 詳細度: "simple" | "medium" | "detailed"
    
    # シミュレーション関連
    simulation_steps: int = 10      # シミュレーションステップ数（1-50）
    time_scale: str = "hours"       # 時間単位: "minutes" | "hours" | "days"
    propagation_speed: float = 1.0  # 伝播速度係数（0.1-5.0）
    
    # LLMプロバイダー設定
    llm_provider: str = "gemini"    # "gemini" | "openai" | "anthropic"
    llm_model: str = "auto"         # "auto" | 具体的なモデル名
    llm_temperature: float = 0.7    # 創造性レベル（0.0-1.0）
    
    # 出力設定
    output_format: str = "markdown" # "markdown" | "json" | "html"
    visualization: bool = True      # 可視化の有無
    language: str = "ja"           # 出力言語
    
    # パフォーマンス設定
    parallel_processing: bool = True
    cache_enabled: bool = True
    max_api_calls_per_minute: int = 60
```

### 3.2 プログラムが動的に生成・設定する項目

```python
@dataclass
class DynamicGeneration:
    """プログラムが記事内容に基づいて動的に生成する項目"""
    
    # === ペルソナ設計（LLMが記事から推論）===
    target_audience_segments: List[Dict]    # 想定読者層
    persona_archetypes: List[Dict]          # ペルソナの原型
    persona_distribution: Dict              # セグメント別の人数配分
    
    # === 個別ペルソナ属性（完全に動的）===
    persona_attributes: Dict = {
        "demographics": {},      # 年齢、職業等（記事に応じて変化）
        "psychographics": {},    # 価値観、興味（記事から推論）
        "behavior_patterns": {}, # 行動パターン（LLM生成）
        "social_network": {},    # 関係性（動的構築）
        "decision_style": {},    # 意思決定スタイル
        "information_processing": {}  # 情報処理特性
    }
    
    # === シミュレーション挙動（動的決定）===
    interaction_patterns: Dict      # ペルソナ間の相互作用パターン
    influence_network: Dict         # 影響力ネットワーク
    propagation_patterns: Dict      # 情報伝播パターン
    emergence_behaviors: List       # 創発的な集団行動
    
    # === 評価基準（記事特性から導出）===
    relevance_criteria: Dict        # 関連性の評価基準
    sharing_thresholds: Dict        # 共有判断の閾値
    sentiment_factors: Dict         # 感情的反応の要因
    
    # === メトリクス定義（自動選択）===
    relevant_metrics: List[str]     # 記事タイプに応じたメトリクス
    visualization_types: List[str]  # 適切な可視化方法
```

### 3.3 設定例

```python
# ユーザー設定例
config = UserConfiguration(
    article="新しいAI規制法案について...",
    population_size=50,
    simulation_steps=20,
    llm_provider="gemini",
    output_format="markdown"
)

# システムが動的に生成する内容の例
dynamic = DynamicGeneration()
# 以下はLLMが記事を分析して自動生成：
dynamic.target_audience_segments = [
    {"name": "政策立案者", "size_ratio": 0.2},
    {"name": "AI研究者", "size_ratio": 0.3},
    {"name": "一般市民", "size_ratio": 0.5}
]
dynamic.persona_archetypes = [
    {"type": "規制推進派の官僚", "count": 5},
    {"type": "懸念を持つAI開発者", "count": 10},
    {"type": "中立的な研究者", "count": 8},
    # ... 記事内容に応じて動的に生成
]
```

## 4. スプリント別実装計画

### Sprint 1 (Week 1-2): コアペルソナ生成

#### Day 1-2: 基本的なペルソナ生成
```python
# テスト駆動で以下を実装
- [ ] test_article_analysis()          # 記事分析
- [ ] test_single_persona_generation() # 単一ペルソナ生成
- [ ] test_persona_validation()        # ペルソナ検証
```

#### Day 3-4: LLM統合
```python
- [ ] test_llm_context_creation()      # LLMコンテキスト生成
- [ ] test_dynamic_attribute_generation() # 動的属性生成
- [ ] test_persona_consistency()       # 一貫性チェック
```

#### Day 5-6: 複数ペルソナと関係性
```python
- [ ] test_population_generation()     # 集団生成
- [ ] test_diversity_check()           # 多様性確保
- [ ] test_network_creation()          # 関係性構築
```

#### Day 7-8: 基本的な評価機能
```python
- [ ] test_article_evaluation()        # 記事評価
- [ ] test_sharing_decision()          # 共有判断
- [ ] test_basic_metrics()             # 基本メトリクス
```

#### Day 9-10: Sprint 1統合とデモ
```python
- [ ] test_end_to_end_flow()          # E2Eテスト
- [ ] test_cli_interface()            # CLI動作確認
- [ ] デモとレトロスペクティブ
```

### Sprint 2 (Week 3-4): シミュレーションと可視化

#### Day 11-12: シミュレーションエンジン
```python
- [ ] test_simulation_step()           # 1ステップ実行
- [ ] test_agent_interactions()        # エージェント相互作用
- [ ] test_state_updates()             # 状態更新
```

#### Day 13-14: ネットワーク伝播
```python
- [ ] test_information_spread()        # 情報伝播
- [ ] test_influence_calculation()     # 影響力計算
- [ ] test_convergence_check()         # 収束判定
```

#### Day 15-16: データストリーミング
```python
- [ ] test_streaming_data_structure()  # データ構造
- [ ] test_real_time_updates()         # リアルタイム更新
- [ ] test_data_compression()          # データ圧縮
```

#### Day 17-18: 可視化とレポート
```python
- [ ] test_markdown_generation()       # Markdown生成
- [ ] test_metrics_visualization()     # メトリクス可視化
- [ ] test_report_completeness()       # レポート完全性
```

#### Day 19-20: 統合とリリース準備
```python
- [ ] test_full_simulation_flow()      # 完全フロー
- [ ] test_performance_benchmarks()    # 性能測定
- [ ] 最終デモとドキュメント整備
```

## 5. 継続的インテグレーション

### 5.1 デイリービルド
```yaml
# .github/workflows/daily.yml
name: Daily TDD Cycle
on:
  push:
  schedule:
    - cron: '0 9 * * *'  # 毎朝9時

jobs:
  tdd-cycle:
    steps:
      - name: Run new tests (RED phase)
        run: pytest tests/ -m "new" --tb=short
        continue-on-error: true
        
      - name: Run all tests (GREEN phase)
        run: pytest tests/ --cov=src
        
      - name: Check code quality (REFACTOR phase)
        run: |
          black --check src tests
          flake8 src tests
          mypy src
```

### 5.2 受け入れテスト駆動開発（ATDD）

```python
# tests/acceptance/test_user_stories.py
class TestUserStories:
    """ユーザーストーリーベースの受け入れテスト"""
    
    def test_as_a_content_creator_i_want_to_predict_article_reception(self):
        """
        As a: コンテンツクリエイター
        I want: 記事の市場反応を予測したい
        So that: 公開前に内容を最適化できる
        """
        # Given: 記事原稿
        article = load_test_article("tech_news.md")
        
        # When: シミュレーションを実行
        result = simulate_market_response(article, population_size=30)
        
        # Then: 予測結果が得られる
        assert result.total_reach > 0
        assert result.sentiment_score is not None
        assert "recommendations" in result.report
```

## 6. 成功指標

### 6.1 スプリント別の完了定義
- **Sprint 1**: 記事を入力して基本的なペルソナ評価が得られる
- **Sprint 2**: 時系列シミュレーションと可視化が動作する

### 6.2 品質指標
- テストカバレッジ: 80%以上
- 全テスト実行時間: 5分以内
- LLM API呼び出し: 1記事あたり$0.10以下

---

更新日: 2025-07-22
作成者: AMS Implementation Team