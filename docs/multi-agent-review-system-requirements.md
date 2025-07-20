# マルチエージェント記事評価・市場反応シミュレーションシステム要件定義書

## 1. システム概要

### 1.1 目的
記事に対する市場の反応を、**記事内容に完全に適応して動的生成される**仮想ペルソナ群による集団行動シミュレーションを通じて予測・評価するシステム。

#### 動的生成の核心
- **記事ごとに異なるペルソナ群**: 健康記事なら医療従事者や健康志向の主婦、テック記事ならエンジニアやスタートアップ関係者など、記事内容に応じて全く異なるペルソナ群をLLMが自動生成
- **固定的な役割からの脱却**: 「技術専門家」「ビジネスユーザー」といった固定カテゴリーではなく、記事のトピック、複雑さ、文体から導き出される実在感のある個人を生成
- **LLMによる創造的生成**: オーケストレーターがLLMに対して「この記事を読む可能性のある多様な人物像」を生成させ、現実的な属性と行動パターンを付与

### 1.2 コンセプトの変更点
- **v1**: 役割ベース（技術専門家、ビジネスユーザー等）の**固定的**評価
- **v2**: 個人ベース（記事に応じて動的生成される仮想人物）の**適応的**シミュレーション

### 1.3 システムアーキテクチャ
```
┌─────────────────────────────────────────────────────────────────┐
│          Dynamic Market Response Simulation System               │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  【Phase 1: 動的ペルソナ生成】                                   │
│  ┌─────────────────┐      ┌──────────────────────────┐        │
│  │  Article Input   │ ───> │  Target Audience Analyzer │        │
│  └─────────────────┘      │    (LLM-based Analysis)   │        │
│                            └──────────┬───────────────┘          │
│                                       ↓                          │
│                        ┌──────────────────────────────┐         │
│                        │   Dynamic Persona Design      │         │
│                        │      Orchestrator             │         │
│                        ├──────────────────────────────┤         │
│                        │ • 記事内容に基づく動的設計    │         │
│                        │ • LLMによる属性生成          │         │
│                        │ • 多様性と現実性の確保       │         │
│                        │ • ネットワーク関係の構築     │         │
│                        └──────────┬───────────────────┘         │
│                                   ↓                              │
│                        ┌──────────────────────────────┐         │
│                        │  Adaptive Persona Population   │         │
│                        │   (記事に最適化された20-50人)  │         │
│                        └──────────┬───────────────────┘         │
│                                   ↓                              │
│  【Phase 2: 集団行動シミュレーション】                           │
│  ┌─────────────────────────────────────────────────────┐       │
│  │          Dynamic Social Behavior Simulation          │       │
│  ├─────────────────────────────────────────────────────┤       │
│  │  T=0: 個別の初期反応（記事内容に応じた評価）        │       │
│  │  T=1: 共有判断（ペルソナ特性に基づく意思決定）     │       │
│  │  T=2: ネットワーク伝播（動的な影響関係）           │       │
│  │  T=n: 長期的影響（収束または拡散）                 │       │
│  └──────────┬──────────────────────────────────────────┘       │
│             ↓                                                    │
│  【Phase 3: 分析・レポート生成】                                 │
│  ┌─────────────────────────────────────────────────────┐       │
│  │     Contextualized Market Response Analysis          │       │
│  │        (記事特性を反映した市場予測)                  │       │
│  └─────────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────────┘
```

## 2. 機能要件

### 2.1 階層化ペルソナ設計システム

#### 2.1.1 ターゲットオーディエンス分析エージェント
```python
class TargetAudienceAnalyzer:
    """記事の内容から想定読者層を動的に分析"""
    
    async def analyze(self, article: str) -> Dict:
        """
        LLMを使用して記事の内容を分析し、
        適切なターゲットオーディエンスを特定
        """
        prompt = f"""
        以下の記事を分析し、想定される読者層を特定してください:
        
        {article[:1000]}...
        
        以下の観点で分析してください：
        1. 記事のトピックとドメイン
        2. 内容の複雑さと前提知識
        3. 文体とトーン
        4. 想定される読者の興味・関心
        5. 読者層の規模と特徴
        """
        
        # LLMが記事内容に基づいて動的に読者層を分析
        audience_analysis = await self.llm.ainvoke(prompt)
        return self.parse_audience_analysis(audience_analysis)
```

#### 2.1.2 動的ペルソナ設計オーケストレーター
```python
class PersonaDesignOrchestrator:
    """記事に適したペルソナ群を動的に設計・生成"""
    
    async def design_persona_population(
        self, 
        article: str,
        target_audience_analysis: Dict
    ) -> List[Dict]:
        """
        記事とターゲット分析に基づいて、
        適切なペルソナ群の設計を動的に生成
        """
        prompt = f"""
        記事のターゲット分析結果:
        {json.dumps(target_audience_analysis, ensure_ascii=False)}
        
        この記事に対する市場反応をシミュレートするため、
        20-30名の多様なペルソナ群を設計してください。
        
        各ペルソナには以下の属性を含めてください：
        - 基本属性（年齢、性別、職業、居住地など）
        - 心理的特性（価値観、興味、ライフスタイルなど）
        - 行動パターン（メディア利用、情報共有習慣など）
        - 社会的ネットワーク（影響力、つながりの強さなど）
        
        記事の内容に応じて、適切な分布と多様性を持つ
        ペルソナ群を生成してください。
        """
        
        # LLMが記事に適したペルソナ群を動的に設計
        persona_designs = await self.llm.ainvoke(prompt)
        return self.parse_persona_designs(persona_designs)
```

#### 2.1.3 動的ペルソナ属性生成システム

```python
class DynamicPersonaAttributeGenerator:
    """LLMによる動的なペルソナ属性生成"""
    
    async def generate_persona_attributes(
        self,
        persona_profile: str,
        article_context: Dict
    ) -> Dict:
        """
        オーケストレーターから指定されたペルソナプロファイルに基づいて、
        具体的な属性をLLMが動的に生成
        """
        prompt = f"""
        ペルソナプロファイル: {persona_profile}
        記事コンテキスト: {json.dumps(article_context, ensure_ascii=False)}
        
        このプロファイルに基づいて、リアルな個人属性を生成してください：
        
        1. デモグラフィック属性
           - 年齢、性別、居住地、職業、教育レベルなど
           - 記事のターゲット層に応じた現実的な分布
        
        2. サイコグラフィック属性
           - 価値観、興味関心、ライフスタイル
           - 記事への関心度に影響する心理的特性
        
        3. 行動パターン
           - メディア消費習慣、情報共有行動
           - SNS利用パターン、影響を受けやすさ
        
        4. ソーシャルネットワーク
           - 社会的つながりの強さと範囲
           - 情報拡散における役割（ハブ、ブリッジ、周辺）
        """
        
        # LLMが記事とプロファイルに適した属性を動的生成
        attributes = await self.llm.ainvoke(prompt)
        return self.parse_persona_attributes(attributes)
```

##### ペルソナ属性スキーマ（動的生成の参考構造）
```python
# 注：これは固定的な定義ではなく、LLMが生成する属性の参考構造
PersonaAttributeSchema = {
    "demographics": {
        "age": "記事内容により変動（例：健康記事なら中高年、テック記事なら若年層）",
        "occupation": "記事トピックに関連する多様な職業",
        "location": "記事の地域性や言語に応じた分布",
        # その他、記事に応じて動的に決定
    },
    
    "psychographics": {
        "values": "記事テーマに共感する価値観のスペクトラム",
        "interests": "記事と関連性の高い興味分野",
        "personality_traits": "情報処理と意思決定に影響する特性",
        # 記事内容により柔軟に調整
    },
    
    "behavior_patterns": {
        "information_consumption": "記事タイプに適した消費パターン",
        "sharing_tendency": "コンテンツと読者層による共有行動",
        "influence_network": "記事の拡散に影響するネットワーク特性",
        # 動的に最適化
    },
    
    "social_network": {
        "connection_strength": "記事の性質による繋がりの重要度",
        "network_role": "情報伝播における個人の役割",
        "community_membership": "記事に関心を持つコミュニティ",
        # ネットワーク効果のシミュレーションに使用
    }
}
```

### 2.2 適応的ペルソナ群生成システム

#### 2.2.1 記事適応型ペルソナ生成
```python
class AdaptivePersonaPopulationGenerator:
    """記事内容に完全に適応したペルソナ群を動的生成"""
    
    async def generate_population(
        self,
        article: str,
        audience_analysis: Dict,
        population_size: int = 30
    ) -> List[Persona]:
        """
        記事とオーディエンス分析から、
        完全に動的なペルソナ群を生成
        """
        # Step 1: 記事に適したペルソナ分布をLLMが決定
        distribution_prompt = f"""
        記事内容の要約: {article[:500]}...
        想定読者分析: {json.dumps(audience_analysis, ensure_ascii=False)}
        
        この記事の市場反応をシミュレートするため、
        {population_size}名のペルソナ群の構成を設計してください。
        
        以下を考慮して多様な分布を作成：
        - 記事に強い関心を持つコア層
        - 部分的に関心を持つ周辺層  
        - 偶然接触する可能性のある層
        - 影響力を持つインフルエンサー層
        - 懐疑的・批判的な視点を持つ層
        
        各層の人数配分と特徴を定義してください。
        """
        
        persona_distribution = await self.llm.ainvoke(distribution_prompt)
        
        # Step 2: 各ペルソナを個別に生成
        personas = []
        for persona_spec in self.parse_distribution(persona_distribution):
            # 個々のペルソナをLLMが詳細に生成
            persona_prompt = f"""
            ペルソナタイプ: {persona_spec['type']}
            記事との関係性: {persona_spec['relationship_to_article']}
            
            このタイプの実在感のある個人を1名生成してください。
            以下を含む詳細なプロファイルを作成：
            - 具体的な背景ストーリー
            - 記事に対する初期反応の予測
            - 情報共有の可能性と動機
            - 他者への影響力
            """
            
            persona_details = await self.llm.ainvoke(persona_prompt)
            persona = self.create_persona_instance(persona_details)
            personas.append(persona)
        
        # Step 3: ペルソナ間のネットワーク関係を動的構築
        network_prompt = f"""
        生成された{len(personas)}名のペルソナ間の
        現実的な社会的つながりを設計してください。
        
        考慮事項：
        - 同じコミュニティや職場の関係
        - SNS上でのフォロー関係
        - 影響力の方向性
        - 情報伝播の経路
        """
        
        network_structure = await self.llm.ainvoke(network_prompt)
        self.establish_dynamic_connections(personas, network_structure)
        
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