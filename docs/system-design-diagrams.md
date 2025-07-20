# システム設計図 - 動的ペルソナ生成による市場反応シミュレーション

## 1. システム構成図

```mermaid
graph TB
    subgraph "Client Layer"
        CLI[CLI Interface]
        API[REST API<br/>将来実装]
    end
    
    subgraph "Orchestration Layer - LangGraph"
        MainGraph[Main Control Graph<br/>全体プロセス制御]
        PersonaGen[Persona Generation<br/>並列生成制御]
        SimControl[Simulation Controller<br/>時系列制御]
    end
    
    subgraph "Processing Layer"
        ArticleAnalyzer[Article Analyzer<br/>記事分析エンジン]
        PersonaDesigner[Persona Designer<br/>ペルソナ設計オーケストレーター]
        PersonaCreator[Dynamic Persona Creator<br/>LLMベース生成器]
        ReactionSim[Reaction Simulator<br/>個人反応シミュレーター]
        NetworkSim[Network Propagation<br/>ネットワーク伝播エンジン]
        ResultAnalyzer[Result Analyzer<br/>結果分析エンジン]
    end
    
    subgraph "LLM Layer"
        LLMFactory[LLM Factory]
        Gemini[Gemini 2.5 Flash]
        OpenAI[OpenAI GPT]
        Claude[Claude API]
    end
    
    subgraph "Data Layer"
        StateStore[State Store<br/>LangGraph State]
        SimData[Simulation Data<br/>時系列データ]
        Reports[Report Storage<br/>分析結果]
    end
    
    CLI --> MainGraph
    API -.-> MainGraph
    
    MainGraph --> ArticleAnalyzer
    MainGraph --> PersonaGen
    MainGraph --> SimControl
    MainGraph --> ResultAnalyzer
    
    PersonaGen --> PersonaDesigner
    PersonaGen --> PersonaCreator
    
    SimControl --> ReactionSim
    SimControl --> NetworkSim
    
    ArticleAnalyzer --> LLMFactory
    PersonaDesigner --> LLMFactory
    PersonaCreator --> LLMFactory
    ReactionSim --> LLMFactory
    ResultAnalyzer --> LLMFactory
    
    LLMFactory --> Gemini
    LLMFactory --> OpenAI
    LLMFactory --> Claude
    
    MainGraph <--> StateStore
    SimControl <--> SimData
    ResultAnalyzer --> Reports
```

## 2. 処理シーケンス図

```mermaid
sequenceDiagram
    participant User
    participant CLI
    participant LangGraph
    participant ArticleAnalyzer
    participant PersonaDesigner
    participant PersonaCreator
    participant Simulator
    participant Analyzer
    participant LLM
    
    User->>CLI: 記事を入力
    CLI->>LangGraph: シミュレーション開始
    
    rect rgb(200, 230, 200)
        Note over LangGraph: Phase 1: 記事分析
        LangGraph->>ArticleAnalyzer: 記事を分析
        ArticleAnalyzer->>LLM: 記事内容分析依頼
        LLM-->>ArticleAnalyzer: トピック、複雑さ、想定読者
        ArticleAnalyzer-->>LangGraph: 分析結果
    end
    
    rect rgb(200, 200, 230)
        Note over LangGraph: Phase 2: ペルソナ設計・生成
        LangGraph->>PersonaDesigner: ペルソナ群を設計
        PersonaDesigner->>LLM: 記事に適したペルソナ分布を生成
        LLM-->>PersonaDesigner: ペルソナ仕様（20-50人分）
        PersonaDesigner-->>LangGraph: ペルソナ設計完了
        
        par 並列ペルソナ生成
            loop 各ペルソナ仕様
                LangGraph->>PersonaCreator: 個別ペルソナ生成
                PersonaCreator->>LLM: 詳細な個人プロファイル生成
                LLM-->>PersonaCreator: 完全なペルソナデータ
                PersonaCreator-->>LangGraph: ペルソナ生成完了
            end
        end
    end
    
    rect rgb(230, 200, 200)
        Note over LangGraph: Phase 3: 市場反応シミュレーション
        loop 時間ステップ T=0 to T=n
            LangGraph->>Simulator: 時刻Tの反応をシミュレート
            par 並列個人反応
                Simulator->>LLM: 各ペルソナの反応を生成
                LLM-->>Simulator: 評価、共有判断
            end
            Simulator->>Simulator: ネットワーク伝播計算
            Simulator-->>LangGraph: 時刻Tの結果
            
            alt 収束判定
                LangGraph->>LangGraph: 収束チェック
            else 継続
                LangGraph->>LangGraph: 次の時間ステップへ
            end
        end
    end
    
    rect rgb(230, 230, 200)
        Note over LangGraph: Phase 4: 結果分析
        LangGraph->>Analyzer: 結果を分析
        Analyzer->>LLM: 市場反応の解釈
        LLM-->>Analyzer: インサイトと予測
        Analyzer-->>LangGraph: 分析完了
    end
    
    LangGraph->>CLI: シミュレーション結果
    CLI->>User: レポート表示
```

## 3. LangGraphフロー図

```mermaid
stateDiagram-v2
    [*] --> ArticleAnalysis: START
    
    ArticleAnalysis --> PersonaDesign: 分析完了
    PersonaDesign --> PersonaGeneration: 設計完了
    
    state PersonaGeneration {
        [*] --> CreateTasks
        CreateTasks --> ParallelGen: Send API
        ParallelGen --> WaitCompletion
        WaitCompletion --> [*]
    }
    
    PersonaGeneration --> SimulationInit: 全ペルソナ生成完了
    
    SimulationInit --> TimeStepLoop
    
    state TimeStepLoop {
        [*] --> InitTimeStep
        InitTimeStep --> ProcessReactions
        ProcessReactions --> NetworkPropagation
        NetworkPropagation --> UpdateMetrics
        UpdateMetrics --> ConvergenceCheck
        
        ConvergenceCheck --> InitTimeStep: continue
        ConvergenceCheck --> [*]: converged/max_time
    }
    
    TimeStepLoop --> ResultAnalysis: シミュレーション完了
    ResultAnalysis --> ReportGeneration: 分析完了
    ReportGeneration --> [*]: END
```

## 4. データフロー図

```mermaid
graph LR
    subgraph "Input"
        Article[記事テキスト]
        Config[設定パラメータ]
    end
    
    subgraph "Phase 1: Analysis"
        ArticleData[記事分析データ]
        Audience[想定読者プロファイル]
    end
    
    subgraph "Phase 2: Generation"
        PersonaSpecs[ペルソナ仕様<br/>20-50件]
        Personas[生成済みペルソナ<br/>詳細プロファイル]
        Network[ソーシャルネットワーク<br/>関係性マップ]
    end
    
    subgraph "Phase 3: Simulation"
        Timeline[時系列データ]
        Interactions[相互作用ログ]
        Propagation[伝播パターン]
    end
    
    subgraph "Phase 4: Output"
        Metrics[評価指標]
        Insights[市場インサイト]
        Report[最終レポート]
    end
    
    Article --> ArticleData
    Config --> ArticleData
    
    ArticleData --> Audience
    Audience --> PersonaSpecs
    
    PersonaSpecs -->|LLM並列生成| Personas
    Personas --> Network
    
    Network --> Timeline
    Timeline -->|時間発展| Interactions
    Interactions --> Propagation
    
    Propagation --> Metrics
    Metrics --> Insights
    Insights --> Report
```

## 5. ペルソナ生成の詳細フロー

```mermaid
flowchart TD
    Start([記事入力]) --> Analyze[記事を分析]
    
    Analyze --> Identify{記事タイプ識別}
    
    Identify -->|健康記事| HealthPersonas[健康関心層の<br/>ペルソナ分布設計]
    Identify -->|技術記事| TechPersonas[技術関心層の<br/>ペルソナ分布設計]
    Identify -->|ビジネス記事| BizPersonas[ビジネス層の<br/>ペルソナ分布設計]
    Identify -->|その他| GeneralPersonas[一般的な<br/>ペルソナ分布設計]
    
    HealthPersonas --> Distribution[分布決定<br/>- コア層: 30%<br/>- 周辺層: 50%<br/>- 偶然層: 20%]
    TechPersonas --> Distribution
    BizPersonas --> Distribution
    GeneralPersonas --> Distribution
    
    Distribution --> ParallelGen{並列生成}
    
    ParallelGen -->|LLM 1| P1[ペルソナ1<br/>詳細生成]
    ParallelGen -->|LLM 2| P2[ペルソナ2<br/>詳細生成]
    ParallelGen -->|LLM 3| P3[ペルソナ3<br/>詳細生成]
    ParallelGen -->|...| PN[ペルソナN<br/>詳細生成]
    
    P1 --> Validate[検証・正規化]
    P2 --> Validate
    P3 --> Validate
    PN --> Validate
    
    Validate --> NetworkBuild[ネットワーク<br/>関係構築]
    
    NetworkBuild --> Complete([ペルソナ群<br/>生成完了])
```

## 6. 時系列シミュレーションフロー

```mermaid
flowchart LR
    subgraph "T=0 初期状態"
        Init0[初期読者<br/>アーリーアダプター]
        Read0[記事を読む]
        Eval0[評価する]
        Share0{共有判断}
    end
    
    subgraph "T=1 第1波"
        Exposed1[露出された人々]
        Read1[記事を読む<br/>確率的]
        Eval1[評価する]
        Share1{共有判断}
    end
    
    subgraph "T=2 第2波"
        Exposed2[新たに露出]
        Read2[記事を読む<br/>社会的証明効果]
        Eval2[評価する]
        Share2{共有判断}
    end
    
    subgraph "T=n 収束"
        Converge[拡散収束<br/>または飽和]
    end
    
    Init0 --> Read0 --> Eval0 --> Share0
    Share0 -->|Yes| Exposed1
    Share0 -->|No| End0[終了]
    
    Exposed1 --> Read1 --> Eval1 --> Share1
    Share1 -->|Yes| Exposed2
    Share1 -->|No| End1[終了]
    
    Exposed2 --> Read2 --> Eval2 --> Share2
    Share2 -->|収束判定| Converge
```

## 7. システム全体のコンポーネント相互作用

```mermaid
graph TB
    subgraph "動的適応層"
        ArticleContext[記事コンテキスト]
        AdaptiveLogic[適応ロジック]
    end
    
    subgraph "LLM駆動層"
        PromptEngine[プロンプトエンジン]
        ResponseParser[レスポンスパーサー]
    end
    
    subgraph "制御層"
        LangGraphCore[LangGraph Core]
        StateManager[状態管理]
        FlowController[フロー制御]
    end
    
    subgraph "実行層"
        ParallelExecutor[並列実行器]
        TimeSeriesEngine[時系列エンジン]
    end
    
    ArticleContext --> AdaptiveLogic
    AdaptiveLogic --> PromptEngine
    
    PromptEngine <--> LLM[LLM API]
    LLM <--> ResponseParser
    
    ResponseParser --> StateManager
    StateManager <--> LangGraphCore
    LangGraphCore --> FlowController
    
    FlowController --> ParallelExecutor
    FlowController --> TimeSeriesEngine
    
    ParallelExecutor --> Results[実行結果]
    TimeSeriesEngine --> Results
```

## 8. データモデル関係図

```mermaid
erDiagram
    Article ||--|| ArticleAnalysis : has
    ArticleAnalysis ||--|| TargetAudience : identifies
    TargetAudience ||--|{ PersonaSpecification : generates
    
    PersonaSpecification ||--|| GeneratedPersona : creates
    GeneratedPersona ||--o{ PersonaAttribute : has
    GeneratedPersona ||--|| SimulationState : maintains
    GeneratedPersona }o--o{ GeneratedPersona : influences
    
    SimulationState ||--|{ TimeStepData : records
    TimeStepData ||--|{ InteractionEvent : contains
    InteractionEvent ||--|| PersonaDecision : represents
    
    PersonaDecision ||--o| SharingAction : may_result_in
    SharingAction ||--|{ NetworkPropagation : triggers
    
    NetworkPropagation ||--|| MarketMetrics : produces
    MarketMetrics ||--|| FinalReport : summarized_in
    
    Article {
        string id PK
        string content
        string title
        datetime created_at
        json metadata
    }
    
    ArticleAnalysis {
        string id PK
        string article_id FK
        json topics
        string complexity_level
        json target_keywords
        string tone
        float estimated_reading_time
    }
    
    TargetAudience {
        string id PK
        string analysis_id FK
        json primary_segments
        json secondary_segments
        int estimated_size
        json characteristics
    }
    
    PersonaSpecification {
        string id PK
        string audience_id FK
        string persona_type
        json design_guidelines
        json target_attributes
        float weight_in_population
    }
    
    GeneratedPersona {
        string id PK
        string spec_id FK
        json profile
        json demographics
        json psychographics
        json behavior_patterns
        float influence_score
    }
    
    PersonaAttribute {
        string id PK
        string persona_id FK
        string attribute_type
        string attribute_name
        json attribute_value
    }
    
    SimulationState {
        string persona_id PK_FK
        boolean has_read
        json evaluation
        json sharing_decision
        int influenced_by_count
        datetime last_updated
    }
    
    TimeStepData {
        int time_step PK
        string simulation_id PK
        int new_readers
        int new_sharers
        float viral_coefficient
        json network_snapshot
    }
    
    InteractionEvent {
        string id PK
        int time_step FK
        string actor_persona_id FK
        string action_type
        json action_details
        datetime timestamp
    }
```

## 9. 動的ペルソナ生成の概念モデル

```mermaid
classDiagram
    class ArticleContext {
        +string content
        +string topic
        +string complexity
        +analyze() Dict
    }
    
    class PersonaDesignOrchestrator {
        +llm LLM
        +design_persona_population(article, audience) List~PersonaSpec~
        +determine_distribution(context) Dict
        +create_design_prompt(spec) str
    }
    
    class PersonaSpec {
        +string id
        +string type
        +Dict guidelines
        +Dict constraints
        +float population_weight
    }
    
    class DynamicPersonaGenerator {
        +llm LLM
        +generate_from_spec(spec, context) Persona
        +validate_persona(data) bool
        +enrich_with_details(base_profile) Dict
    }
    
    class Persona {
        +string id
        +Dict profile
        +Dict article_relationship
        +Dict simulation_state
        +evaluate_article(article) Evaluation
        +decide_sharing(evaluation, social_context) Decision
    }
    
    class SimulationEngine {
        +personas List~Persona~
        +time_step int
        +simulate_step() StepResult
        +check_convergence() bool
        +calculate_metrics() Metrics
    }
    
    class NetworkPropagation {
        +network_graph Graph
        +calculate_exposure(persona, sharers) List~Persona~
        +apply_social_influence(persona, influencers) float
        +update_network_state() void
    }
    
    ArticleContext --> PersonaDesignOrchestrator : provides context
    PersonaDesignOrchestrator --> PersonaSpec : creates
    PersonaSpec --> DynamicPersonaGenerator : used by
    DynamicPersonaGenerator --> Persona : generates
    Persona --> SimulationEngine : participates in
    SimulationEngine --> NetworkPropagation : uses
    NetworkPropagation --> Persona : affects
```

## 10. LangGraphステート遷移の詳細

```mermaid
stateDiagram-v2
    [*] --> Initialize: START
    
    state Initialize {
        [*] --> LoadArticle
        LoadArticle --> ValidateInput
        ValidateInput --> [*]
    }
    
    Initialize --> ArticleAnalysis: Valid Input
    
    state ArticleAnalysis {
        [*] --> ExtractTopics
        ExtractTopics --> AnalyzeComplexity
        AnalyzeComplexity --> IdentifyAudience
        IdentifyAudience --> [*]
    }
    
    ArticleAnalysis --> PersonaDesign: Analysis Complete
    
    state PersonaDesign {
        [*] --> DetermineDistribution
        DetermineDistribution --> CreateSpecifications
        CreateSpecifications --> ValidateSpecs
        ValidateSpecs --> [*]
    }
    
    PersonaDesign --> PersonaGeneration: Specs Ready
    
    state PersonaGeneration {
        [*] --> BatchPersonas
        BatchPersonas --> ParallelGeneration
        
        state ParallelGeneration {
            [*] --> GenerateP1
            [*] --> GenerateP2
            [*] --> GenerateP3
            [*] --> GeneratePN
            
            GenerateP1 --> [*]
            GenerateP2 --> [*]
            GenerateP3 --> [*]
            GeneratePN --> [*]
        }
        
        ParallelGeneration --> ValidatePersonas
        ValidatePersonas --> BuildNetwork
        BuildNetwork --> [*]
    }
    
    PersonaGeneration --> Simulation: Personas Ready
    
    state Simulation {
        [*] --> T0_Initial
        
        state T0_Initial {
            [*] --> IdentifyEarlyAdopters
            IdentifyEarlyAdopters --> InitialReactions
            InitialReactions --> [*]
        }
        
        T0_Initial --> TimeLoop
        
        state TimeLoop {
            [*] --> ProcessExposure
            ProcessExposure --> EvaluateContent
            EvaluateContent --> MakeSharingDecision
            MakeSharingDecision --> UpdateNetwork
            UpdateNetwork --> CheckConvergence
            
            CheckConvergence --> ProcessExposure: Continue
            CheckConvergence --> [*]: Converged
        }
        
        TimeLoop --> [*]
    }
    
    Simulation --> Analysis: Simulation Complete
    
    state Analysis {
        [*] --> AggregateMetrics
        AggregateMetrics --> IdentifyPatterns
        IdentifyPatterns --> GenerateInsights
        GenerateInsights --> [*]
    }
    
    Analysis --> Reporting: Analysis Complete
    
    state Reporting {
        [*] --> FormatResults
        FormatResults --> CreateVisualizations
        CreateVisualizations --> GenerateReport
        GenerateReport --> [*]
    }
    
    Reporting --> [*]: END
```

これらの図は、現在の動的ペルソナ生成システムの設計を包括的に表現しています。