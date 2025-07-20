# マルチエージェント記事評価・市場反応シミュレーションシステム要件定義書

## 1. システム概要

### 1.1 目的
記事に対する市場の反応を、動的に生成された仮想ペルソナ群による集団行動シミュレーションを通じて予測・評価するシステム。各ペルソナは実在の人間のように振る舞い、記事の評価、共有、拡散といった一連の行動をシミュレートする。

### 1.2 コンセプトの変更点
- **v1**: 役割ベース（技術専門家、ビジネスユーザー等）の静的評価
- **v2**: 個人ベース（具体的な属性を持つ仮想人物）の動的シミュレーション

### 1.3 システムアーキテクチャ
```
┌─────────────────────────────────────────────────────────────────┐
│                Market Response Simulation System                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  【Phase 1: ペルソナ生成】                                       │
│  ┌─────────────────┐      ┌──────────────────────────┐        │
│  │  Article Input   │ ───> │  Target Audience Analyzer │        │
│  └─────────────────┘      └──────────┬───────────────┘        │
│                                       ↓                          │
│                        ┌──────────────────────────────┐         │
│                        │  Hierarchical Persona Design  │         │
│                        │         System                │         │
│                        ├──────────────────────────────┤         │
│                        │ • Market Segmentation Agent  │         │
│                        │ • Demographics Designer      │         │
│                        │ • Psychographics Designer    │         │
│                        │ • Behavior Pattern Designer  │         │
│                        │ • Social Network Designer    │         │
│                        └──────────┬───────────────────┘         │
│                                   ↓                              │
│                        ┌──────────────────────────────┐         │
│                        │    Persona Population        │         │
│                        │      (20-50 personas)        │         │
│                        └──────────┬───────────────────┘         │
│                                   ↓                              │
│  【Phase 2: 集団行動シミュレーション】                           │
│  ┌─────────────────────────────────────────────────────┐       │
│  │               Social Behavior Simulation              │       │
│  ├─────────────────────────────────────────────────────┤       │
│  │  T=0: Initial Reading & Reaction                     │       │
│  │  T=1: Sharing Decision & Action                      │       │
│  │  T=2: Network Effect & Propagation                   │       │
│  │  T=n: Long-term Impact & Saturation                  │       │
│  └──────────┬──────────────────────────────────────────┘       │
│             ↓                                                    │
│  【Phase 3: 分析・レポート生成】                                 │
│  ┌─────────────────────────────────────────────────────┐       │
│  │          Market Response Analysis & Report           │       │
│  └─────────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────────┘
```

## 2. 機能要件

### 2.1 階層化ペルソナ設計システム

#### 2.1.1 ターゲットオーディエンス分析エージェント
```python
class TargetAudienceAnalyzer:
    """記事の内容から想定読者層を分析"""
    
    def analyze(self, article: str) -> Dict:
        """
        Returns:
        {
            "primary_segments": ["tech_professionals", "startup_founders"],
            "secondary_segments": ["students", "researchers"],
            "content_complexity": "intermediate",
            "domain": "AI/ML",
            "tone": "technical_but_accessible",
            "estimated_audience_size": "50K-100K"
        }
        """
```

#### 2.1.2 市場セグメンテーションエージェント
```python
class MarketSegmentationAgent:
    """市場を適切なセグメントに分割"""
    
    segments = {
        "tech_professionals": {
            "size_ratio": 0.3,
            "subtypes": ["frontend_dev", "backend_dev", "data_scientist", "devops"],
            "age_range": (22, 45),
            "education": ["bachelor", "master", "phd"]
        },
        "business_leaders": {
            "size_ratio": 0.2,
            "subtypes": ["startup_founder", "product_manager", "executive"],
            "age_range": (28, 55),
            "focus": ["roi", "innovation", "competitive_advantage"]
        }
        # ... 他のセグメント
    }
```

#### 2.1.3 ペルソナ属性設計エージェント

##### デモグラフィック設計
```python
class DemographicsDesigner:
    """人口統計学的属性を設計"""
    
    attributes = {
        "name": str,           # 例: "田中太郎"
        "age": int,            # 例: 32
        "gender": str,         # 例: "male"
        "location": str,       # 例: "東京都渋谷区"
        "occupation": str,     # 例: "ソフトウェアエンジニア"
        "company_type": str,   # 例: "スタートアップ"
        "income_level": str,   # 例: "600-800万円"
        "education": str,      # 例: "情報工学修士"
        "family_status": str   # 例: "既婚・子供1人"
    }
```

##### サイコグラフィック設計
```python
class PsychographicsDesigner:
    """心理的・価値観的属性を設計"""
    
    attributes = {
        "personality_type": str,     # 例: "INTJ"
        "values": List[str],         # 例: ["効率性", "革新", "学習"]
        "interests": List[str],      # 例: ["AI", "起業", "投資"]
        "lifestyle": str,            # 例: "ワークライフバランス重視"
        "tech_adoption": str,        # 例: "early_adopter"
        "risk_tolerance": float,     # 例: 0.7 (0-1)
        "influence_susceptibility": float,  # 例: 0.4 (0-1)
        "opinion_leader": bool       # 例: True
    }
```

##### 行動特性設計
```python
class BehaviorPatternDesigner:
    """行動パターンと習慣を設計"""
    
    attributes = {
        "reading_habits": {
            "preferred_length": "medium",  # short/medium/long
            "reading_time": ["morning_commute", "lunch_break"],
            "devices": ["smartphone", "laptop"],
            "attention_span": 15  # minutes
        },
        "sharing_behavior": {
            "platforms": ["twitter", "linkedin", "slack"],
            "frequency": "moderate",  # rare/moderate/frequent
            "motivation": ["help_others", "show_expertise"],
            "follower_count": {
                "twitter": 850,
                "linkedin": 1200
            }
        },
        "content_preferences": {
            "topics": ["AI", "productivity", "career"],
            "formats": ["how-to", "case_study", "analysis"],
            "depth": "detailed"
        }
    }
```

##### ソーシャルネットワーク設計
```python
class SocialNetworkDesigner:
    """社会的つながりとネットワーク構造を設計"""
    
    attributes = {
        "network_size": int,           # 例: 150 (ダンバー数)
        "strong_ties": int,            # 例: 15 (親密な関係)
        "weak_ties": int,              # 例: 135 (緩い関係)
        "communities": List[str],      # 例: ["AI研究会", "起業家コミュニティ"]
        "influence_score": float,      # 例: 0.65 (0-1)
        "network_position": str,       # 例: "bridge" (hub/bridge/peripheral)
        "professional_connections": {
            "same_company": 30,
            "same_industry": 80,
            "cross_industry": 40
        }
    }
```

### 2.2 ペルソナ群生成エージェント

#### 2.2.1 ペルソナ生成ロジック
```python
class PersonaPopulationGenerator:
    """記事に適したペルソナ群を動的に生成"""
    
    def generate_population(
        self,
        target_audience: Dict,
        population_size: int = 30
    ) -> List[Persona]:
        """
        ターゲットオーディエンス分析に基づいて、
        統計的に妥当な分布を持つペルソナ群を生成
        """
        personas = []
        
        # セグメント別の人数配分
        for segment, ratio in self.calculate_segment_distribution(target_audience):
            segment_size = int(population_size * ratio)
            
            for i in range(segment_size):
                # 各属性を相関を考慮して生成
                demographics = self.generate_demographics(segment)
                psychographics = self.generate_psychographics(demographics, segment)
                behavior = self.generate_behavior(demographics, psychographics)
                network = self.generate_network(demographics, behavior)
                
                persona = Persona(
                    id=f"persona_{segment}_{i}",
                    demographics=demographics,
                    psychographics=psychographics,
                    behavior=behavior,
                    network=network
                )
                personas.append(persona)
        
        # ネットワーク関係の構築
        self.establish_network_connections(personas)
        
        return personas
```

### 2.3 集団行動シミュレーション

#### 2.3.1 個人の意思決定モデル
```python
class PersonaDecisionEngine:
    """個々のペルソナの意思決定をシミュレート"""
    
    async def evaluate_article(self, persona: Persona, article: str) -> Dict:
        """記事に対する個人的評価"""
        
        # 関連性スコア（自分の興味との一致度）
        relevance = self.calculate_relevance(
            article_topics=extract_topics(article),
            persona_interests=persona.psychographics.interests
        )
        
        # 理解度スコア（複雑さと知識レベルの適合）
        comprehension = self.calculate_comprehension(
            article_complexity=analyze_complexity(article),
            persona_expertise=persona.demographics.education
        )
        
        # 価値スコア（提供される価値の認識）
        value = self.calculate_value(
            article_insights=extract_insights(article),
            persona_values=persona.psychographics.values
        )
        
        # 感情的反応
        emotional_response = self.calculate_emotional_response(
            article_tone=analyze_tone(article),
            persona_personality=persona.psychographics.personality_type
        )
        
        # 総合評価
        overall_score = self.weighted_average({
            "relevance": (relevance, 0.3),
            "comprehension": (comprehension, 0.2),
            "value": (value, 0.3),
            "emotional": (emotional_response, 0.2)
        })
        
        return {
            "persona_id": persona.id,
            "scores": {
                "relevance": relevance,
                "comprehension": comprehension,
                "value": value,
                "emotional": emotional_response,
                "overall": overall_score
            },
            "reaction": self.determine_reaction(overall_score),
            "timestamp": datetime.now()
        }
    
    async def decide_sharing(
        self,
        persona: Persona,
        evaluation: Dict,
        social_context: Dict
    ) -> Dict:
        """共有するかどうかの意思決定"""
        
        # 共有の動機
        sharing_motivation = self.calculate_sharing_motivation(
            evaluation_score=evaluation["scores"]["overall"],
            sharing_habits=persona.behavior.sharing_behavior,
            social_proof=social_context.get("friends_shared", 0)
        )
        
        # プラットフォーム選択
        if sharing_motivation > persona.behavior.sharing_threshold:
            platforms = self.select_platforms(
                available_platforms=persona.behavior.sharing_behavior["platforms"],
                content_type=evaluation.get("content_type"),
                audience_match=self.calculate_audience_match(persona, evaluation)
            )
            
            # 共有時のコメント生成
            comment = self.generate_sharing_comment(
                persona_style=persona.psychographics.communication_style,
                key_points=evaluation.get("key_takeaways"),
                emotion=evaluation["scores"]["emotional"]
            )
            
            return {
                "will_share": True,
                "platforms": platforms,
                "comment": comment,
                "expected_reach": self.estimate_reach(persona, platforms)
            }
        
        return {"will_share": False, "reason": "below_threshold"}
```

#### 2.3.2 ネットワーク効果シミュレーション
```python
class NetworkEffectSimulator:
    """ソーシャルネットワーク上での情報伝播をシミュレート"""
    
    async def simulate_propagation(
        self,
        initial_sharers: List[Persona],
        all_personas: List[Persona],
        article: str,
        time_steps: int = 10
    ) -> Dict:
        """時系列での情報伝播をシミュレート"""
        
        propagation_history = []
        current_readers = set(initial_sharers)
        potential_readers = set(all_personas) - current_readers
        
        for t in range(time_steps):
            new_readers = set()
            new_sharers = set()
            
            # 現在の共有者から影響を受ける人を計算
            for sharer in current_readers:
                # 共有者のネットワーク内で露出
                exposed_personas = self.get_exposed_personas(
                    sharer=sharer,
                    potential_readers=potential_readers,
                    exposure_probability=self.calculate_exposure_probability(sharer)
                )
                
                # 露出した人々の反応をシミュレート
                for exposed_persona in exposed_personas:
                    # ソーシャルプルーフの影響を含めて評価
                    social_context = {
                        "friends_shared": self.count_friends_who_shared(
                            exposed_persona,
                            current_readers
                        ),
                        "influencer_endorsed": self.check_influencer_endorsement(
                            exposed_persona,
                            current_readers
                        )
                    }
                    
                    # 記事を読むかどうかの決定
                    if self.decide_to_read(exposed_persona, social_context):
                        new_readers.add(exposed_persona)
                        
                        # 評価と共有の決定
                        evaluation = await PersonaDecisionEngine().evaluate_article(
                            exposed_persona,
                            article
                        )
                        
                        sharing_decision = await PersonaDecisionEngine().decide_sharing(
                            exposed_persona,
                            evaluation,
                            social_context
                        )
                        
                        if sharing_decision["will_share"]:
                            new_sharers.add(exposed_persona)
            
            # 状態更新
            current_readers.update(new_readers)
            potential_readers -= new_readers
            
            # 履歴記録
            propagation_history.append({
                "time_step": t,
                "new_readers": len(new_readers),
                "new_sharers": len(new_sharers),
                "total_readers": len(current_readers),
                "virality_coefficient": len(new_sharers) / len(current_readers) if current_readers else 0
            })
            
            # 収束判定
            if len(new_readers) == 0:
                break
        
        return {
            "propagation_history": propagation_history,
            "final_reach": len(current_readers),
            "reach_percentage": len(current_readers) / len(all_personas),
            "viral_status": self.determine_viral_status(propagation_history)
        }
```

#### 2.3.3 集団ダイナミクスシミュレーション
```python
class GroupDynamicsSimulator:
    """集団としての行動パターンをシミュレート"""
    
    async def simulate_collective_behavior(
        self,
        personas: List[Persona],
        article: str,
        simulation_params: Dict
    ) -> Dict:
        """集団全体の反応と行動をシミュレート"""
        
        # フェーズ1: 初期反応（個別評価）
        initial_evaluations = await asyncio.gather(*[
            PersonaDecisionEngine().evaluate_article(persona, article)
            for persona in personas
        ])
        
        # フェーズ2: アーリーアダプターの特定と初期共有
        early_adopters = self.identify_early_adopters(
            personas,
            initial_evaluations
        )
        
        initial_sharing_decisions = await asyncio.gather(*[
            PersonaDecisionEngine().decide_sharing(
                persona,
                evaluation,
                {"friends_shared": 0}  # 初期状態
            )
            for persona, evaluation in zip(early_adopters, 
                [e for e in initial_evaluations if e["persona_id"] in [p.id for p in early_adopters]])
        ])
        
        initial_sharers = [
            persona for persona, decision in zip(early_adopters, initial_sharing_decisions)
            if decision["will_share"]
        ]
        
        # フェーズ3: ネットワーク伝播シミュレーション
        propagation_result = await NetworkEffectSimulator().simulate_propagation(
            initial_sharers=initial_sharers,
            all_personas=personas,
            article=article,
            time_steps=simulation_params.get("time_steps", 10)
        )
        
        # フェーズ4: セグメント別分析
        segment_analysis = self.analyze_by_segment(
            personas,
            initial_evaluations,
            propagation_result
        )
        
        # フェーズ5: 感情とトレンドの分析
        sentiment_evolution = self.analyze_sentiment_evolution(
            initial_evaluations,
            propagation_result
        )
        
        return {
            "summary": {
                "total_reach": propagation_result["final_reach"],
                "reach_percentage": propagation_result["reach_percentage"],
                "viral_coefficient": self.calculate_viral_coefficient(propagation_result),
                "peak_velocity": self.calculate_peak_velocity(propagation_result),
                "saturation_time": self.estimate_saturation_time(propagation_result)
            },
            "segment_performance": segment_analysis,
            "sentiment_evolution": sentiment_evolution,
            "key_influencers": self.identify_key_influencers(personas, propagation_result),
            "propagation_pattern": propagation_result["propagation_history"],
            "recommendations": self.generate_recommendations(segment_analysis, sentiment_evolution)
        }
```

### 2.4 市場反応分析・レポート生成

#### 2.4.1 分析エンジン
```python
class MarketResponseAnalyzer:
    """シミュレーション結果を分析し、市場反応を予測"""
    
    def analyze_market_response(self, simulation_result: Dict) -> Dict:
        """包括的な市場反応分析"""
        
        return {
            "executive_summary": self.generate_executive_summary(simulation_result),
            
            "reach_analysis": {
                "total_addressable_market": self.estimate_tam(simulation_result),
                "expected_reach": simulation_result["summary"]["total_reach"],
                "reach_by_channel": self.analyze_reach_by_channel(simulation_result),
                "geographic_distribution": self.analyze_geographic_spread(simulation_result)
            },
            
            "engagement_metrics": {
                "average_reading_time": self.calculate_avg_reading_time(simulation_result),
                "engagement_rate": self.calculate_engagement_rate(simulation_result),
                "share_rate": self.calculate_share_rate(simulation_result),
                "comment_sentiment": self.analyze_comment_sentiment(simulation_result)
            },
            
            "virality_assessment": {
                "viral_potential": self.assess_viral_potential(simulation_result),
                "k_factor": simulation_result["summary"]["viral_coefficient"],
                "expected_lifespan": self.estimate_content_lifespan(simulation_result),
                "peak_timing": self.predict_peak_timing(simulation_result)
            },
            
            "audience_insights": {
                "primary_audience": self.identify_primary_audience(simulation_result),
                "unexpected_segments": self.identify_unexpected_segments(simulation_result),
                "barrier_analysis": self.analyze_adoption_barriers(simulation_result),
                "motivator_analysis": self.analyze_sharing_motivators(simulation_result)
            },
            
            "competitive_intelligence": {
                "market_positioning": self.analyze_market_positioning(simulation_result),
                "differentiation_factors": self.identify_differentiation(simulation_result),
                "competitive_advantages": self.assess_competitive_advantages(simulation_result)
            },
            
            "optimization_recommendations": {
                "content_improvements": self.suggest_content_improvements(simulation_result),
                "distribution_strategy": self.recommend_distribution_strategy(simulation_result),
                "targeting_refinements": self.suggest_targeting_refinements(simulation_result),
                "timing_optimization": self.optimize_release_timing(simulation_result)
            }
        }
```

#### 2.4.2 ビジュアライゼーション生成
```python
class VisualizationGenerator:
    """シミュレーション結果の可視化"""
    
    def generate_visualizations(self, analysis_result: Dict) -> Dict:
        """各種ビジュアライゼーションを生成"""
        
        return {
            "propagation_graph": self.create_propagation_network_graph(
                # ネットワーク上での伝播をグラフで表現
            ),
            
            "reach_timeline": self.create_reach_timeline_chart(
                # 時系列でのリーチ拡大を表示
            ),
            
            "segment_heatmap": self.create_segment_response_heatmap(
                # セグメント別の反応をヒートマップで表示
            ),
            
            "influence_network": self.create_influence_network_diagram(
                # キーインフルエンサーとその影響範囲
            ),
            
            "sentiment_flow": self.create_sentiment_flow_chart(
                # 感情の変化と伝播を可視化
            ),
            
            "geographic_spread": self.create_geographic_spread_map(
                # 地理的な拡散パターン
            )
        }
```

## 3. 非機能要件

### 3.1 パフォーマンス要件
- **ペルソナ生成**: 50体のペルソナを10秒以内に生成
- **シミュレーション実行**: 
  - 50ペルソナ・10タイムステップ: 60秒以内
  - 100ペルソナ・20タイムステップ: 180秒以内
- **並列処理**: 個々のペルソナの意思決定は並列実行

### 3.2 スケーラビリティ要件
- **水平スケーリング**: ペルソナ数に応じてワーカーを増やせる
- **バッチ処理**: 複数の記事を同時にシミュレーション可能
- **段階的詳細化**: 簡易シミュレーション→詳細シミュレーション

### 3.3 精度・妥当性要件
- **統計的妥当性**: ペルソナ属性の分布が現実の市場データと整合
- **行動モデルの検証**: 実際のSNSデータとの比較検証
- **予測精度**: 過去の事例での検証（70%以上の精度目標）

## 4. 技術仕様

### 4.1 LangGraphによる階層的エージェント構造

#### 4.1.1 ペルソナ生成グラフ
```python
def build_persona_generation_graph() -> CompiledGraph:
    """ペルソナ生成のための階層的グラフ構造"""
    
    workflow = StateGraph(PersonaGenerationState)
    
    # レベル1: 市場分析
    workflow.add_node("market_analyzer", MarketAnalyzer())
    
    # レベル2: セグメント設計（並列実行）
    workflow.add_node("segment_designers", segment_design_handler)
    
    # レベル3: 属性設計（並列実行）
    workflow.add_node("attribute_designers", attribute_design_handler)
    
    # レベル4: ペルソナ組み立て
    workflow.add_node("persona_assembler", PersonaAssembler())
    
    # レベル5: ネットワーク構築
    workflow.add_node("network_builder", NetworkBuilder())
    
    # フロー定義
    workflow.add_edge(START, "market_analyzer")
    workflow.add_edge("market_analyzer", "segment_designers")
    workflow.add_edge("segment_designers", "attribute_designers")
    workflow.add_edge("attribute_designers", "persona_assembler")
    workflow.add_edge("persona_assembler", "network_builder")
    workflow.add_edge("network_builder", END)
    
    return workflow.compile()
```

#### 4.1.2 シミュレーショングラフ
```python
def build_simulation_graph() -> CompiledGraph:
    """集団行動シミュレーションのグラフ構造"""
    
    workflow = StateGraph(SimulationState)
    
    # 初期評価フェーズ
    workflow.add_node("initial_evaluation", initial_evaluation_handler)
    
    # アーリーアダプター特定
    workflow.add_node("early_adopter_identification", identify_early_adopters)
    
    # 伝播シミュレーション（時系列ループ）
    workflow.add_node("propagation_loop", propagation_simulator)
    
    # 分析フェーズ
    workflow.add_node("analysis", market_response_analyzer)
    
    # 条件付きルーティング（収束判定）
    workflow.add_conditional_edges(
        "propagation_loop",
        convergence_check,
        {
            "continue": "propagation_loop",
            "converged": "analysis"
        }
    )
    
    return workflow.compile()
```

### 4.2 データモデル

#### 4.2.1 ペルソナデータ構造
```python
@dataclass
class Persona:
    """個別ペルソナの完全なデータ構造"""
    id: str
    demographics: Demographics
    psychographics: Psychographics
    behavior_patterns: BehaviorPatterns
    social_network: SocialNetwork
    
    # 動的状態
    current_state: PersonaState
    interaction_history: List[Interaction]
    influence_received: List[Influence]
    content_shared: List[SharedContent]
```

#### 4.2.2 シミュレーション状態
```python
class SimulationState(TypedDict):
    """シミュレーション全体の状態管理"""
    article: ArticleData
    personas: List[Persona]
    time_step: int
    
    # 評価結果
    evaluations: Dict[str, PersonaEvaluation]
    
    # 共有状態
    sharing_decisions: Dict[str, SharingDecision]
    propagation_network: NetworkGraph
    
    # 分析結果
    reach_metrics: ReachMetrics
    engagement_metrics: EngagementMetrics
    virality_metrics: ViralityMetrics
```

### 4.3 モデル切り替え設定（v1から継承）

```bash
# .env ファイル
LLM_PROVIDER=gemini
GEMINI_MODEL=gemini-2.5-flash

# シミュレーション設定
SIMULATION_POPULATION_SIZE=30
SIMULATION_TIME_STEPS=10
SIMULATION_PARALLEL_WORKERS=4

# 高度な設定
PERSONA_GENERATION_DETAIL_LEVEL=high  # low/medium/high
NETWORK_COMPLEXITY=realistic  # simple/moderate/realistic
BEHAVIOR_MODEL_VERSION=v2  # v1/v2
```

## 5. 実装優先順位（MVP）

### Phase 1: 基本的なペルソナ生成（Week 1）
1. ターゲットオーディエンス分析
2. 基本的な属性生成（デモグラフィック中心）
3. 5-10体の簡易ペルソナ生成

### Phase 2: 個人行動シミュレーション（Week 2）
1. 記事評価モデル
2. 共有意思決定モデル
3. 個別ペルソナの反応シミュレーション

### Phase 3: 集団行動シミュレーション（Week 3）
1. 簡易ネットワーク伝播モデル
2. 基本的な集団ダイナミクス
3. MVP版レポート生成

### Phase 4: 高度な機能（Post-MVP）
1. 詳細なネットワーク構造
2. 時系列での感情変化
3. 地理的拡散モデル
4. 競合分析機能

## 6. 検証とチューニング

### 6.1 検証方法
1. **A/Bテスト**: 実際の記事公開結果との比較
2. **過去データ検証**: 既存の成功/失敗事例での検証
3. **専門家レビュー**: マーケティング専門家による妥当性評価

### 6.2 チューニングパラメータ
- 影響力伝播の減衰率
- 共有閾値の調整
- ネットワーク密度
- 時間ステップの粒度

## 7. 期待される価値

### 7.1 ビジネス価値
- **リスク低減**: 公開前に市場反応を予測
- **最適化**: コンテンツと配信戦略の改善
- **ROI向上**: より効果的なコンテンツマーケティング

### 7.2 技術的価値
- **革新的アプローチ**: エージェントベースモデリングの応用
- **スケーラブル**: 様々なコンテンツタイプに適用可能
- **学習可能**: シミュレーション結果から継続的改善

## 8. 制限事項と今後の課題

### 8.1 現在の制限
- 単一言語（日本語）のみ対応
- テキストコンテンツのみ（画像・動画は未対応）
- SNSプラットフォームは主要なもののみ

### 8.2 将来の拡張
- マルチモーダルコンテンツ対応
- リアルタイムデータ統合
- 予測モデルの自動学習
- グローバル市場対応