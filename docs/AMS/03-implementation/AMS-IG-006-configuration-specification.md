# AMS-IG-006: 設定仕様 - ユーザー設定と動的生成の明確化

## 1. 設定の階層構造

```
┌─────────────────────────────────────────────────────┐
│           ユーザー設定（外部から制御可能）              │
├─────────────────────────────────────────────────────┤
│  必須設定:                                           │
│    - article: 評価対象の記事                         │
│                                                     │
│  オプション設定:                                      │
│    - population_size: ペルソナ数（5-100）            │
│    - simulation_steps: ステップ数（1-50）            │
│    - llm_provider: LLMプロバイダー                   │
│    - output_format: 出力形式                        │
└─────────────────────────────────────────────────────┘
                           ↓
                    記事内容を分析
                           ↓
┌─────────────────────────────────────────────────────┐
│          動的生成（プログラムが自動決定）               │
├─────────────────────────────────────────────────────┤
│  記事分析結果:                                        │
│    - target_segments: 想定読者層                     │
│    - complexity_level: 複雑度                        │
│    - domain: 分野（tech/health/social等）            │
│                                                     │
│  ペルソナ設計:                                        │
│    - persona_types: 記事に応じたペルソナタイプ        │
│    - distribution: セグメント別配分                   │
│    - relationships: ペルソナ間の関係性                │
│                                                     │
│  シミュレーション:                                    │
│    - behavior_models: 行動モデル                     │
│    - interaction_rules: 相互作用ルール               │
│    - emergence_patterns: 創発パターン               │
└─────────────────────────────────────────────────────┘
```

## 2. ユーザー設定の詳細仕様

### 2.1 設定ファイル形式

```yaml
# config/simulation_config.yaml
# ユーザーが制御可能な設定項目

# === 必須設定 ===
article_path: "path/to/article.txt"  # または直接テキスト

# === ペルソナ生成設定 ===
persona:
  population_size: 30        # 生成するペルソナ数（デフォルト: 30）
  detail_level: "medium"     # 詳細度: simple/medium/detailed
  
# === シミュレーション設定 ===
simulation:
  max_steps: 10             # 最大ステップ数（デフォルト: 10）
  time_scale: "hours"       # 時間単位: minutes/hours/days
  convergence_threshold: 0.01  # 収束判定閾値
  
# === LLM設定 ===
llm:
  provider: "gemini"        # gemini/openai/anthropic
  model: "gemini-1.5-flash" # 具体的なモデル名を明示的に指定（実装時に利用可能なモデルを確認）
  temperature: 0.7          # 0.0-1.0（創造性レベル）
  max_tokens_per_call: 1000
  
# === 出力設定 ===
output:
  format: "markdown"        # markdown/json/html
  include_visualizations: true
  language: "ja"
  report_sections:          # 含めるセクション
    - executive_summary
    - detailed_analysis
    - recommendations
    
# === パフォーマンス設定 ===
performance:
  enable_cache: true
  parallel_personas: 10     # 並列生成数
  api_rate_limit: 60       # 分あたりのAPI呼び出し上限
```

### 2.2 CLIオプション

```bash
# CLIでの設定例
ams simulate \
  --article "article.txt" \
  --personas 50 \
  --steps 20 \
  --provider gemini \
  --output report.md \
  --detail-level detailed \
  --parallel
```

### 2.3 プログラマティック設定

```python
from ams import SimulationConfig, MarketSimulator

# プログラムからの設定
config = SimulationConfig(
    article="AI規制に関する新しい法案が...",
    population_size=40,
    simulation_steps=15,
    llm_provider="gemini",
    output_format="markdown",
    # 以下はオプション（デフォルト値あり）
    detail_level="medium",
    time_scale="hours",
    temperature=0.7,
    enable_cache=True
)

simulator = MarketSimulator(config)
result = await simulator.run()
```

## 3. 動的生成の詳細仕様

### 3.1 記事分析による動的決定

```python
class DynamicAnalyzer:
    """記事内容から動的に要素を決定"""
    
    async def analyze_article(self, article: str) -> ArticleContext:
        """記事を分析して文脈を抽出"""
        
        # LLMによる記事分析
        analysis_prompt = f"""
        以下の記事を分析し、シミュレーションに必要な要素を抽出してください：
        
        {article[:1000]}...
        
        抽出項目：
        1. 主要トピックとドメイン
        2. 想定される読者層（複数可）
        3. 記事の複雑度（専門性）
        4. 感情的なトーン
        5. 議論の余地がある要素
        """
        
        analysis = await self.llm.analyze(analysis_prompt)
        
        return ArticleContext(
            domain=analysis.domain,              # 例: "tech", "health", "politics"
            topics=analysis.topics,              # 例: ["AI", "規制", "倫理"]
            target_segments=analysis.segments,   # 例: ["政策立案者", "AI開発者", "一般市民"]
            complexity=analysis.complexity,      # 例: 0.7 (0-1)
            emotional_tone=analysis.tone,        # 例: "neutral", "controversial"
            controversy_level=analysis.controversy  # 例: 0.8 (0-1)
        )
```

### 3.2 ペルソナタイプの動的生成

```python
class DynamicPersonaDesigner:
    """記事に応じたペルソナタイプを動的生成"""
    
    async def design_persona_types(
        self, 
        article_context: ArticleContext,
        population_size: int
    ) -> List[PersonaType]:
        """記事文脈からペルソナタイプを設計"""
        
        design_prompt = f"""
        記事の分析結果：
        - ドメイン: {article_context.domain}
        - トピック: {article_context.topics}
        - 想定読者: {article_context.target_segments}
        - 複雑度: {article_context.complexity}
        
        この記事に対して多様な反応を示す{population_size}人のペルソナ群を設計してください。
        
        以下の観点で設計：
        1. 記事への関心度（高/中/低）
        2. 専門知識レベル
        3. 立場（賛成/中立/反対）
        4. 影響力（インフルエンサー/一般/周辺）
        5. 行動パターン（積極的共有/選択的共有/非共有）
        
        現実的で多様な分布を作成してください。
        """
        
        persona_design = await self.llm.design(design_prompt)
        
        # 例: 記事がAI規制の場合の動的生成結果
        return [
            PersonaType(
                name="慎重派のAI研究者",
                count=5,
                attributes={
                    "expertise": "high",
                    "concern_level": "high",
                    "sharing_tendency": "selective"
                }
            ),
            PersonaType(
                name="規制推進派の政策立案者",
                count=3,
                attributes={
                    "expertise": "medium",
                    "stance": "pro-regulation",
                    "influence": "high"
                }
            ),
            # ... 他のペルソナタイプも動的に生成
        ]
```

### 3.3 行動ルールの動的生成

```python
class DynamicBehaviorGenerator:
    """ペルソナの行動ルールを動的生成"""
    
    async def generate_behavior_rules(
        self,
        persona_type: PersonaType,
        article_context: ArticleContext
    ) -> BehaviorRules:
        """ペルソナタイプと記事文脈から行動ルールを生成"""
        
        behavior_prompt = f"""
        ペルソナ: {persona_type.name}
        記事トピック: {article_context.topics}
        
        このペルソナが記事に対してどのように行動するか、
        以下の観点でルールを生成してください：
        
        1. 記事を読む確率と条件
        2. 評価基準（何を重視するか）
        3. 共有判断の基準
        4. 他者からの影響の受けやすさ
        5. 時間経過による関心の変化
        """
        
        rules = await self.llm.generate_rules(behavior_prompt)
        
        return BehaviorRules(
            reading_probability=rules.reading_prob,
            evaluation_criteria=rules.criteria,
            sharing_threshold=rules.sharing_threshold,
            influence_susceptibility=rules.influence,
            interest_decay=rules.decay_rate
        )
```

### 3.4 メトリクスの動的選択

```python
class DynamicMetricsSelector:
    """記事タイプに応じて適切なメトリクスを選択"""
    
    def select_metrics(self, article_context: ArticleContext) -> List[Metric]:
        """文脈に応じたメトリクスを動的選択"""
        
        base_metrics = [
            Metric("total_reach", "総リーチ数"),
            Metric("engagement_rate", "エンゲージメント率"),
            Metric("sharing_rate", "共有率")
        ]
        
        # ドメイン特有のメトリクスを追加
        if article_context.domain == "tech":
            base_metrics.extend([
                Metric("expert_adoption", "専門家の採用率"),
                Metric("technical_discussion", "技術的議論の発生率")
            ])
        elif article_context.domain == "health":
            base_metrics.extend([
                Metric("trust_score", "信頼性スコア"),
                Metric("patient_interest", "患者層の関心度")
            ])
        elif article_context.controversy_level > 0.7:
            base_metrics.extend([
                Metric("polarization_index", "意見の分極化指数"),
                Metric("debate_intensity", "議論の激しさ")
            ])
            
        return base_metrics
```

## 4. 設定と生成の境界線

### 4.1 明確な区分原則

| 項目 | ユーザー設定 | 動的生成 | 理由 |
|------|------------|---------|------|
| ペルソナ数 | ✓ | - | 計算資源とコストに影響 |
| ペルソナの属性 | - | ✓ | 記事内容に依存すべき |
| シミュレーション期間 | ✓ | - | ユーザーのニーズに依存 |
| 伝播パターン | - | ✓ | 記事とペルソナで決まる |
| LLMプロバイダー | ✓ | - | コストと性能の選択 |
| 評価基準 | - | ✓ | 記事内容で自動決定 |
| 出力形式 | ✓ | - | ユーザーの用途に依存 |
| 可視化タイプ | △ | △ | 基本はユーザー、詳細は自動 |

### 4.2 ハイブリッド設定の例

```python
# ユーザーが大枠を指定、詳細は動的生成
config = SimulationConfig(
    # ユーザー指定
    visualization_preference="network",  # "network" or "timeline" or "auto"
    
    # システムが動的に決定
    # - networkを選んだ場合でも、記事の性質により
    #   階層型、放射型、クラスター型などを自動選択
)
```

## 5. 実装例：設定から実行まで

```python
# main.py
async def run_simulation(user_config: dict):
    """ユーザー設定から動的生成を経てシミュレーション実行"""
    
    # Step 1: ユーザー設定の検証
    config = validate_user_config(user_config)
    
    # Step 2: 記事分析（動的）
    analyzer = DynamicAnalyzer()
    article_context = await analyzer.analyze_article(config.article)
    
    # Step 3: ペルソナ設計（動的）
    designer = DynamicPersonaDesigner()
    persona_types = await designer.design_persona_types(
        article_context, 
        config.population_size  # ユーザー指定の数
    )
    
    # Step 4: 行動ルール生成（動的）
    behavior_gen = DynamicBehaviorGenerator()
    behavior_rules = {}
    for persona_type in persona_types:
        behavior_rules[persona_type.name] = await behavior_gen.generate_behavior_rules(
            persona_type, 
            article_context
        )
    
    # Step 5: シミュレーション実行
    simulator = MarketSimulator(
        config=config,              # ユーザー設定
        article_context=article_context,  # 動的分析結果
        persona_types=persona_types,      # 動的生成
        behavior_rules=behavior_rules     # 動的生成
    )
    
    result = await simulator.run()
    
    # Step 6: 出力生成（ユーザー設定に従う）
    return format_output(result, config.output_format)
```

---

更新日: 2025-07-22
作成者: AMS Implementation Team