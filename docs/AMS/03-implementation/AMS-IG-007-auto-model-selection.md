# AMS-IG-007: LLMモデル自動選択機能の仕様

## 1. `llm_model: "auto"` の動作仕様

### 1.1 概要
`llm_model: "auto"`を指定した場合、システムが以下の要因を考慮して最適なLLMモデルを自動選択します。

### 1.2 選択基準

```python
class AutoModelSelector:
    """LLMモデルの自動選択ロジック"""
    
    def select_model(
        self,
        provider: str,
        task_type: str,
        article_length: int,
        detail_level: str,
        budget_constraint: Optional[float] = None
    ) -> str:
        """タスクと制約に基づいて最適なモデルを選択"""
        
        # プロバイダー別のモデル選択
        if provider == "gemini":
            return self._select_gemini_model(
                task_type, article_length, detail_level, budget_constraint
            )
        elif provider == "openai":
            return self._select_openai_model(
                task_type, article_length, detail_level, budget_constraint
            )
        # ... 他のプロバイダー
```

## 2. Geminiプロバイダーでの自動選択

### 2.1 選択マトリクス

| 条件 | 選択されるモデル | 理由 |
|------|----------------|------|
| 記事分析（初期） | gemini-pro | 高速・低コスト |
| ペルソナ生成（simple） | gemini-pro | 基本的な生成で十分 |
| ペルソナ生成（detailed） | gemini-2.5-flash | 高品質な生成が必要 |
| 長文記事（>5000文字） | gemini-2.5-flash | コンテキスト長の制約 |
| 予算制約あり | gemini-pro | コスト優先 |
| リアルタイム要求 | gemini-pro | レスポンス速度優先 |

### 2.2 実装例

```python
def _select_gemini_model(
    self,
    task_type: str,
    article_length: int,
    detail_level: str,
    budget_constraint: Optional[float]
) -> str:
    """Geminiモデルの自動選択"""
    
    # 予算制約がある場合
    if budget_constraint and budget_constraint < 0.01:  # $0.01以下/リクエスト
        return "gemini-pro"
    
    # タスクタイプ別の選択
    if task_type == "article_analysis":
        # 記事分析は軽量モデルで十分
        return "gemini-pro"
    
    elif task_type == "persona_generation":
        # 詳細度による選択
        if detail_level == "simple":
            return "gemini-pro"
        elif detail_level in ["medium", "detailed"]:
            # 長文の場合は高性能モデル
            if article_length > 5000:
                return "gemini-2.5-flash"
            else:
                return "gemini-pro"
    
    elif task_type == "behavior_simulation":
        # シミュレーションは高品質モデルを使用
        return "gemini-2.5-flash"
    
    # デフォルト
    return "gemini-pro"
```

## 3. タスク別の自動選択

### 3.1 記事分析フェーズ

```python
# 記事分析時の自動選択
async def analyze_article(article: str, config: UserConfiguration):
    if config.llm_model == "auto":
        # 記事の特性を簡易分析
        article_stats = {
            "length": len(article),
            "complexity": estimate_complexity(article),
            "language": detect_language(article)
        }
        
        # 最適なモデルを選択
        model = AutoModelSelector().select_model(
            provider=config.llm_provider,
            task_type="article_analysis",
            article_length=article_stats["length"],
            detail_level="medium"  # 分析は中程度の詳細度
        )
    else:
        model = config.llm_model
```

### 3.2 ペルソナ生成フェーズ

```python
# ペルソナ生成時の自動選択
async def generate_personas(context: ArticleContext, config: UserConfiguration):
    if config.llm_model == "auto":
        # ペルソナ生成の要求レベルを判定
        requirements = {
            "count": config.population_size,
            "detail": config.persona_detail_level,
            "diversity": context.get("audience_diversity", "medium")
        }
        
        # 複雑なペルソナが必要な場合は高性能モデル
        if (requirements["count"] > 30 or 
            requirements["detail"] == "detailed" or
            requirements["diversity"] == "high"):
            model = "gemini-2.5-flash"
        else:
            model = "gemini-pro"
    else:
        model = config.llm_model
```

## 4. 動的切り替え

### 4.1 実行時の動的切り替え

```python
class DynamicModelManager:
    """実行中のモデル切り替えを管理"""
    
    def __init__(self, config: UserConfiguration):
        self.config = config
        self.usage_stats = defaultdict(float)
        self.error_counts = defaultdict(int)
    
    async def get_model_for_task(self, task: str) -> str:
        """タスクに応じてモデルを動的に選択"""
        
        if self.config.llm_model != "auto":
            return self.config.llm_model
        
        # エラー率が高い場合は別モデルに切り替え
        current_model = self._get_default_model(task)
        if self.error_counts[current_model] > 3:
            return self._get_fallback_model(current_model)
        
        # レート制限に近い場合は別モデルに分散
        if self._is_near_rate_limit(current_model):
            return self._get_alternative_model(current_model)
        
        return current_model
```

### 4.2 コスト最適化

```python
class CostOptimizedSelector:
    """コストを考慮したモデル選択"""
    
    def select_with_budget(
        self,
        remaining_budget: float,
        remaining_tasks: int
    ) -> str:
        """残予算と残タスク数から最適なモデルを選択"""
        
        avg_budget_per_task = remaining_budget / remaining_tasks
        
        # モデル別の推定コスト（例）
        model_costs = {
            "gemini-pro": 0.0005,          # $0.50 per 1M tokens
            "gemini-2.5-flash": 0.002,     # $2.00 per 1M tokens
            "gpt-3.5-turbo": 0.001,        # $1.00 per 1M tokens
            "gpt-4": 0.03                  # $30.00 per 1M tokens
        }
        
        # 予算内で最高性能のモデルを選択
        affordable_models = [
            model for model, cost in model_costs.items()
            if cost <= avg_budget_per_task
        ]
        
        # 性能順でソート（仮定）
        performance_order = [
            "gpt-4", "gemini-2.5-flash", "gpt-3.5-turbo", "gemini-pro"
        ]
        
        for model in performance_order:
            if model in affordable_models:
                return model
        
        return "gemini-pro"  # 最も安価なモデル
```

## 5. 設定例と動作

### 5.1 自動選択の例

```python
# ユーザー設定
config = UserConfiguration(
    article="短い技術ニュース（500文字）",
    llm_model="auto",  # 自動選択
    llm_provider="gemini",
    persona_detail_level="simple",
    population_size=20
)

# システムの動作
# 1. 記事分析 → gemini-pro（短文・シンプル）
# 2. ペルソナ生成 → gemini-pro（20体・simple）
# 3. シミュレーション → gemini-pro（軽量タスク）
```

### 5.2 明示的指定の例

```python
# ユーザー設定
config = UserConfiguration(
    article="複雑な医学論文（10000文字）",
    llm_model="gemini-2.5-flash",  # 明示的に指定
    llm_provider="gemini",
    persona_detail_level="detailed",
    population_size=50
)

# システムの動作
# すべてのタスクでgemini-2.5-flashを使用
```

## 6. 推奨設定

### 6.1 ユースケース別の推奨

| ユースケース | 推奨設定 | 理由 |
|------------|---------|------|
| 初期テスト・開発 | `llm_model="gemini-pro"` | コスト削減 |
| 本番環境 | `llm_model="auto"` | 最適化された選択 |
| 高品質要求 | `llm_model="gemini-2.5-flash"` | 品質優先 |
| 予算制約あり | `llm_model="auto"` + `budget_constraint` | コスト管理 |

### 6.2 注意事項

1. **プロバイダー間の互換性**
   - `auto`選択はプロバイダー内でのみ動作
   - プロバイダーを跨いだ自動選択は現在未対応

2. **モデルの可用性**
   - 選択されたモデルが利用できない場合は自動的にフォールバック
   - エラーログに記録される

3. **コスト管理**
   - `auto`使用時もコスト上限を設定可能
   - 予算超過時は自動的に低コストモデルに切り替え

---

更新日: 2025-07-22
作成者: AMS Implementation Team