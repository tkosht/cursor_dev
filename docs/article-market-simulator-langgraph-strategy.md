# Article Market Simulator - LangGraph使用戦略

## 1. 概要

本文書では、動的ペルソナ生成による市場反応シミュレーションシステムにおけるLangGraphの使用戦略を定義します。LangGraphは、複雑な多段階プロセスの制御と並列実行の管理に活用します。

## 2. LangGraphの使用箇所

### 2.1 主要な使用領域

```
┌─────────────────────────────────────────────────────────┐
│                  LangGraph適用領域                       │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  1. プロセス制御層（メインオーケストレーション）        │
│     └─ 多段階処理の状態管理とフロー制御                 │
│                                                          │
│  2. 並列実行層（ペルソナ生成・シミュレーション）        │
│     └─ 大量のLLM呼び出しの並列管理                      │
│                                                          │
│  3. 時系列制御層（伝播シミュレーション）                │
│     └─ 時間軸に沿った反復処理と収束判定                 │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### 2.2 LangGraphを使用する理由

1. **状態管理**: 複雑な多段階プロセスの状態を一元管理
2. **並列実行**: Send APIによる効率的な並列LLM呼び出し
3. **条件分岐**: Command APIによる動的なフロー制御
4. **エラー処理**: 組み込みのリトライとフォールバック機構
5. **可視化**: グラフ構造による処理フローの可視化

## 3. 具体的な適用パターン

### 3.1 メインプロセス制御

```python
# LangGraphによるメインプロセスの制御
class MarketSimulationGraph:
    """市場シミュレーションの全体制御"""
    
    def build_main_graph(self) -> CompiledGraph:
        workflow = StateGraph(SimulationState)
        
        # Phase 1: 記事分析と準備
        workflow.add_node("article_analysis", self.analyze_article)
        
        # Phase 2: 動的ペルソナ生成（並列実行）
        workflow.add_node("persona_generation", self.generate_personas)
        
        # Phase 3: シミュレーション実行（時系列ループ）
        workflow.add_node("simulation", self.run_simulation)
        
        # Phase 4: 結果分析とレポート生成
        workflow.add_node("analysis", self.analyze_results)
        
        # フロー定義
        workflow.add_edge(START, "article_analysis")
        workflow.add_edge("article_analysis", "persona_generation")
        workflow.add_edge("persona_generation", "simulation")
        
        # 条件付き遷移（シミュレーションのループ制御）
        workflow.add_conditional_edges(
            "simulation",
            self.check_convergence,
            {
                "continue": "simulation",
                "complete": "analysis"
            }
        )
        
        workflow.add_edge("analysis", END)
        
        return workflow.compile()
```

### 3.2 動的ペルソナ生成の並列化

```python
async def generate_personas(self, state: SimulationState) -> Dict:
    """LangGraphのSend APIを使用した並列ペルソナ生成"""
    
    # Step 1: 記事分析結果から必要なペルソナプロファイルを決定
    article = state["article"]
    audience_analysis = state["audience_analysis"]
    
    # LLMに記事に適したペルソナ分布を生成させる
    persona_distribution = await self.design_persona_distribution(
        article, audience_analysis
    )
    
    # Step 2: Send APIで並列生成タスクを作成
    sends = []
    for persona_spec in persona_distribution["personas"]:
        sends.append(Send(
            "persona_generator",  # 動的ペルソナ生成ワーカー
            {
                "persona_id": persona_spec["id"],
                "profile_guidelines": persona_spec["guidelines"],
                "article_context": article.summary,
                "target_attributes": persona_spec["target_attributes"]
            }
        ))
    
    # 並列実行結果を集約
    return {"persona_generation_tasks": sends}
```

### 3.3 時系列シミュレーションの制御

```python
def check_convergence(self, state: SimulationState) -> str:
    """シミュレーションの収束判定"""
    
    current_step = state.get("time_step", 0)
    max_steps = state.get("max_time_steps", 10)
    
    # 新規リーチの変化率を確認
    propagation_history = state.get("propagation_history", [])
    if len(propagation_history) >= 3:
        recent_growth = [h["new_readers"] for h in propagation_history[-3:]]
        if all(g < 0.01 * state["total_personas"] for g in recent_growth):
            return "complete"  # 収束
    
    # 最大ステップ数チェック
    if current_step >= max_steps:
        return "complete"
    
    return "continue"
```

## 4. LangGraphを使用しない部分

以下の処理はLangGraphの外で実装：

1. **個別のLLM呼び出し**: 単純なプロンプト実行
2. **データ変換・整形**: 純粋なPython処理
3. **可視化生成**: matplotlib等の専用ライブラリ
4. **ファイルI/O**: 標準的なファイル操作

## 5. 実装上の考慮事項

### 5.1 状態管理の設計

```python
class SimulationState(TypedDict):
    """LangGraphで管理する状態"""
    # 入力
    article: str
    config: SimulationConfig
    
    # 処理状態
    current_phase: str
    time_step: int
    
    # 中間結果
    audience_analysis: Dict
    persona_specs: List[Dict]
    generated_personas: List[Dict]
    
    # シミュレーション結果
    propagation_history: List[Dict]
    interaction_logs: List[Dict]
    
    # 最終出力
    analysis_results: Dict
    report: Dict
    
    # エラー管理
    errors: List[Dict]
    retry_count: Dict[str, int]
```

### 5.2 並列実行の最適化

```python
# 並列実行の粒度設定
PARALLEL_CONFIGS = {
    "persona_generation": {
        "batch_size": 5,  # 同時生成数
        "timeout": 30,    # タイムアウト（秒）
        "max_retries": 3
    },
    "initial_evaluation": {
        "batch_size": 10,
        "timeout": 20,
        "max_retries": 2
    }
}
```

## 6. 利点と制約

### 6.1 LangGraph使用の利点

1. **スケーラビリティ**: ペルソナ数に応じた自動的な並列化
2. **可観測性**: 各ステップの進捗と状態の追跡
3. **エラー耐性**: 部分的な失敗からの自動回復
4. **再現性**: 状態のチェックポイント機能

### 6.2 制約事項

1. **複雑性**: 単純な逐次処理には過剰
2. **デバッグ**: グラフ構造のデバッグは通常のコードより困難
3. **学習曲線**: LangGraph特有の概念の理解が必要

## 7. まとめ

LangGraphは以下の3つの主要な役割で使用：

1. **全体のオーケストレーション**: フェーズ間の遷移制御
2. **大規模並列処理**: ペルソナ生成と評価の並列実行
3. **時系列制御**: シミュレーションループの管理

これにより、動的で柔軟な市場反応シミュレーションを実現します。