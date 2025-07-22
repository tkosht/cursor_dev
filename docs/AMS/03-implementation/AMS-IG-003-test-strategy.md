# AMS-IG-003: Article Market Simulator テスト戦略

## 1. テスト方針

### 1.1 基本原則
- **LLMモック禁止**: すべてのテストで実際のLLM APIを使用
- **意味のあるテスト**: 形式的ではなく、実際の品質保証に寄与
- **継続的実行可能**: CI/CDパイプラインで実行可能な設計
- **コスト意識**: API利用料を考慮した効率的なテスト

### 1.2 テストレベル
```
┌─────────────────────────────────────────┐
│          E2E Tests (10%)                │
│    統合シナリオ・ユーザージャーニー      │
├─────────────────────────────────────────┤
│      Integration Tests (30%)            │
│    コンポーネント間連携・API統合        │
├─────────────────────────────────────────┤
│        Unit Tests (60%)                 │
│    個別機能・ビジネスロジック           │
└─────────────────────────────────────────┘
```

## 2. LLM統合テスト戦略

### 2.1 テスト用LLM設定
```python
# tests/config/llm_config.py
class TestLLMConfig:
    """テスト用のLLM設定（コスト最適化）"""
    
    # 開発・テスト用の設定
    TEST_CONFIGS = {
        "unit_test": {
            "model": "gemini-1.5-flash",  # 実装時に利用可能なモデルを確認
            "max_tokens": 500,      # 最小限のトークン
            "temperature": 0.1,     # 決定的な出力
            "timeout": 10           # タイムアウト短め
        },
        "integration_test": {
            "model": "gemini-1.5-flash",  # 実装時に利用可能なモデルを確認
            "max_tokens": 1000,
            "temperature": 0.3,
            "timeout": 30
        },
        "e2e_test": {
            "model": "gemini-2.5-flash",  # 本番同等
            "max_tokens": 2000,
            "temperature": 0.7,
            "timeout": 60
        }
    }
    
    # コスト制限
    DAILY_TOKEN_LIMIT = 1_000_000  # 1日あたりの上限
    TEST_RUN_LIMIT = 10_000        # 1テストランあたり
```

### 2.2 テストデータ戦略
```python
# tests/fixtures/test_articles.py
TEST_ARTICLES = {
    "simple_tech": {
        "content": "新しいAI技術が発表されました。この技術は...",
        "expected_segments": ["tech_enthusiasts", "professionals"],
        "complexity": "medium"
    },
    "complex_health": {
        "content": "最新の研究によると、特定の遺伝子変異が...",
        "expected_segments": ["medical_professionals", "patients"],
        "complexity": "high"
    },
    "viral_social": {
        "content": "話題の社会現象について、専門家は...",
        "expected_segments": ["general_public", "influencers"],
        "complexity": "low"
    }
}
```

## 3. ユニットテスト詳細

### 3.1 ペルソナ生成テスト
```python
# tests/unit/test_persona_generation.py
import pytest
from ams.personas import DeepContextAnalyzer, PersonaGenerator

class TestPersonaGeneration:
    """ペルソナ生成の単体テスト"""
    
    @pytest.fixture
    def analyzer(self):
        return DeepContextAnalyzer(llm_config=TestLLMConfig.TEST_CONFIGS["unit_test"])
    
    def test_context_analysis_basic(self, analyzer):
        """基本的な文脈分析のテスト"""
        article = TEST_ARTICLES["simple_tech"]["content"]
        context = analyzer.analyze_article_context(article)
        
        # 必須フィールドの存在確認
        assert "core_context" in context
        assert "hidden_dimensions" in context
        assert "complexity_score" in context
        
        # 妥当性チェック
        assert 0 <= context["complexity_score"] <= 1
        assert len(context["core_context"]) > 0
    
    def test_persona_attributes_consistency(self, generator):
        """ペルソナ属性の一貫性テスト"""
        persona = generator.generate_simple_persona()
        
        # 内部一貫性チェック
        assert self._check_age_occupation_consistency(persona)
        assert self._check_behavior_personality_alignment(persona)
    
    @pytest.mark.parametrize("article_type", ["tech", "health", "social"])
    def test_persona_diversity(self, generator, article_type):
        """生成されるペルソナの多様性テスト"""
        personas = [generator.generate_persona() for _ in range(5)]
        
        # 多様性メトリクス
        diversity_score = self._calculate_diversity(personas)
        assert diversity_score > 0.7  # 十分な多様性
```

### 3.2 シミュレーションエンジンテスト
```python
# tests/unit/test_simulation_engine.py
class TestSimulationEngine:
    """シミュレーションエンジンの単体テスト"""
    
    def test_event_bus_functionality(self):
        """イベントバスの基本機能テスト"""
        bus = EventBus()
        received_events = []
        
        async def handler(event):
            received_events.append(event)
        
        bus.subscribe("test_event", handler)
        event = SimulationEvent(
            timestamp=datetime.now(),
            source_id="test",
            event_type="test_event",
            payload={"data": "test"}
        )
        
        await bus.publish(event)
        assert len(received_events) == 1
        assert received_events[0].payload["data"] == "test"
    
    def test_time_advancement(self):
        """時間進行のテスト"""
        clock = SimulationClock(tick_rate=0.1)
        
        initial_time = clock.current_time
        events = await clock.advance()
        
        assert clock.current_time == initial_time + 0.1
        assert isinstance(events, list)
```

## 4. 統合テスト詳細

### 4.1 ペルソナ-シミュレーション統合
```python
# tests/integration/test_persona_simulation.py
class TestPersonaSimulationIntegration:
    """ペルソナとシミュレーションの統合テスト"""
    
    @pytest.mark.asyncio
    async def test_persona_behavior_in_simulation(self):
        """シミュレーション内でのペルソナ行動テスト"""
        # 最小限のペルソナ生成
        personas = await self._generate_test_personas(count=5)
        
        # シミュレーション環境構築
        environment = TestArticleEnvironment(
            article=TEST_ARTICLES["simple_tech"]["content"]
        )
        
        # 1タイムステップ実行
        simulator = MarketSimulator(personas, environment)
        result = await simulator.run_single_step()
        
        # 結果検証
        assert result.active_agents > 0
        assert result.interactions_count >= 0
        assert all(p.has_valid_state() for p in personas)
    
    async def test_network_propagation(self):
        """ネットワーク伝播のテスト"""
        # 初期共有者の設定
        initial_sharers = await self._create_initial_sharers(2)
        population = await self._create_population(10)
        
        # 伝播シミュレーション
        propagator = NetworkPropagator()
        result = await propagator.simulate(
            initial_sharers, 
            population,
            max_steps=3
        )
        
        # 伝播パターンの検証
        assert result.total_reached > len(initial_sharers)
        assert result.propagation_path is not None
```

### 4.2 可視化データ生成テスト
```python
# tests/integration/test_visualization_pipeline.py
class TestVisualizationPipeline:
    """可視化パイプラインの統合テスト"""
    
    async def test_streaming_data_generation(self):
        """ストリーミングデータ生成テスト"""
        # シミュレーション状態の作成
        state = self._create_mock_simulation_state()
        
        # パイプライン処理
        pipeline = VisualizationPipeline()
        stream_data = await pipeline.process_state(state)
        
        # データ構造の検証
        assert stream_data.timestamp > 0
        assert len(stream_data.agent_states) > 0
        assert stream_data.metrics is not None
        
        # JSON変換可能性
        json_data = stream_data.to_json()
        assert isinstance(json_data, str)
        assert len(json_data) < 10000  # サイズ制限
```

## 5. E2Eテスト詳細

### 5.1 完全シナリオテスト
```python
# tests/e2e/test_full_scenario.py
class TestFullScenario:
    """エンドツーエンドシナリオテスト"""
    
    @pytest.mark.e2e
    @pytest.mark.timeout(300)  # 5分タイムアウト
    async def test_article_to_report_flow(self):
        """記事入力からレポート生成までの完全フロー"""
        # 記事入力
        article = TEST_ARTICLES["viral_social"]["content"]
        
        # CLI経由での実行
        result = await run_cli_command([
            "ams", "simulate",
            "--article", article,
            "--personas", "20",
            "--steps", "5",
            "--output", "test_report.md"
        ])
        
        # 結果検証
        assert result.exit_code == 0
        assert os.path.exists("test_report.md")
        
        # レポート内容の検証
        with open("test_report.md", "r") as f:
            report_content = f.read()
        
        assert "Executive Summary" in report_content
        assert "Simulation Results" in report_content
        assert "Key Findings" in report_content
        
        # メトリクスの妥当性
        metrics = self._extract_metrics_from_report(report_content)
        assert 0 <= metrics["reach_rate"] <= 1
        assert metrics["total_personas"] == 20
```

## 6. パフォーマンステスト

### 6.1 ベンチマークテスト
```python
# tests/performance/test_benchmarks.py
class TestPerformanceBenchmarks:
    """パフォーマンスベンチマークテスト"""
    
    @pytest.mark.benchmark
    def test_persona_generation_speed(self, benchmark):
        """ペルソナ生成速度のベンチマーク"""
        generator = PersonaGenerator(
            llm_config=TestLLMConfig.TEST_CONFIGS["integration_test"]
        )
        
        result = benchmark(
            generator.generate_population,
            size=10  # ベンチマーク用の小規模
        )
        
        # 性能基準
        assert result.stats.mean < 2.0  # 平均2秒以内
        assert result.stats.stddev < 0.5  # 安定性
    
    @pytest.mark.benchmark
    async def test_simulation_throughput(self, benchmark):
        """シミュレーションスループットテスト"""
        setup = await self._setup_simulation(personas=20)
        
        async def run_simulation():
            await setup.simulator.run_steps(5)
        
        result = benchmark(run_simulation)
        
        # スループット基準
        assert result.stats.mean < 10.0  # 10秒以内
```

## 7. テスト実行戦略

### 7.1 ローカル開発
```bash
# 高速なユニットテストのみ
pytest tests/unit -v --maxfail=1

# 特定機能のテスト
pytest tests/unit/test_persona_generation.py -k "diversity"

# カバレッジ付き
pytest tests/unit --cov=ams --cov-report=html
```

### 7.2 CI/CD パイプライン
```yaml
# .github/workflows/test.yml
name: Test Suite

on: [push, pull_request]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - name: Run Unit Tests
        run: |
          pytest tests/unit -v --junit-xml=unit-results.xml
        env:
          LLM_TEST_MODE: "unit"
          
  integration-tests:
    runs-on: ubuntu-latest
    if: github.event_name == 'pull_request'
    steps:
      - name: Run Integration Tests
        run: |
          pytest tests/integration -v --junit-xml=integration-results.xml
        env:
          LLM_TEST_MODE: "integration"
          DAILY_TOKEN_LIMIT: 50000
          
  e2e-tests:
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Run E2E Tests
        run: |
          pytest tests/e2e -v --junit-xml=e2e-results.xml
        env:
          LLM_TEST_MODE: "e2e"
```

### 7.3 コスト管理
```python
# tests/utils/cost_tracker.py
class TestCostTracker:
    """テスト実行コストの追跡"""
    
    def __init__(self):
        self.token_usage = defaultdict(int)
        self.api_calls = defaultdict(int)
    
    def track_llm_call(self, test_name, tokens, model):
        """LLM呼び出しの記録"""
        self.token_usage[test_name] += tokens
        self.api_calls[model] += 1
        
        # コスト計算（例：Gemini Pro）
        cost_per_1k = 0.0005  # $0.50 per 1M tokens
        estimated_cost = (tokens / 1000) * cost_per_1k
        
        return estimated_cost
    
    def generate_report(self):
        """コストレポートの生成"""
        total_tokens = sum(self.token_usage.values())
        total_cost = self._calculate_total_cost()
        
        report = f"""
        Test Run Cost Report
        ===================
        Total Tokens: {total_tokens:,}
        Estimated Cost: ${total_cost:.2f}
        
        By Test:
        {self._format_test_breakdown()}
        
        By Model:
        {self._format_model_breakdown()}
        """
        return report
```

## 8. テスト品質保証

### 8.1 テストケース設計基準
- **境界値テスト**: 最小/最大ペルソナ数
- **異常系テスト**: API失敗、タイムアウト
- **性能劣化テスト**: 大規模データでの動作
- **互換性テスト**: 異なるLLMプロバイダー

### 8.2 テストレビューチェックリスト
- [ ] 各機能に対応するテストが存在
- [ ] エラーケースがカバーされている
- [ ] テスト実行時間が妥当（単体<1秒、統合<30秒）
- [ ] アサーションが意味のある検証を行っている
- [ ] テストデータが現実的
- [ ] 非決定的要素への対処

### 8.3 継続的改善
- 週次でのテスト実行時間レビュー
- 月次でのコスト分析
- 失敗頻度の高いテストの見直し
- カバレッジ向上の取り組み

---

更新日: 2025-07-21
作成者: AMS Implementation Team