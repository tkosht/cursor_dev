# Skipped Test DAG探索分析レポート

実行日: 2025-07-30
タスク: pytest実行時の1件skippedテスト要因分析

## 現象の詳細

### 基本情報
- **テスト結果**: 118 passed, 1 skipped, 15 warnings (実行時間: 398.27秒)
- **Skippedテスト**: `tests/integration/test_small_scale_integration.py:228`
- **メソッド名**: `test_performance_baseline`
- **Skip理由**: "Performance baseline test times out with real LLM calls - needs optimization"

### テストの内容
```python
@pytest.mark.skip(reason="Performance baseline test times out with real LLM calls - needs optimization")
async def test_performance_baseline(self, short_article):
    """Establish performance baseline for small scale."""
```

このテストは、3つのコンポーネントのパフォーマンスを測定：
1. DeepContextAnalyzer（記事分析）- 制限: 60秒
2. PopulationArchitect（人口階層設計）- 制限: 60秒  
3. PersonaGenerator（ペルソナ生成）- 制限: 60秒
4. 全体パイプライン - 制限: 180秒

## DAG探索による要因分析

### ルートノード: パフォーマンステストのタイムアウト
優先度: 1.0 (最高)

### 子ノード1: LLM APIコールの遅延仮説
- **仮説**: 実際のLLM APIコールが予想以上に時間がかかる
- **根拠**: 
  - 他のテストでも7,141文字のプロンプトで30秒タイムアウト発生
  - 実測: 1,509文字で15.5秒、7,141文字で35-45秒予想
- **優先度**: 0.9
- **ステータス**: PROVED

### 子ノード2: テスト設計の問題仮説
- **仮説**: パフォーマンステストの時間制限が厳しすぎる
- **根拠**: 
  - 各コンポーネント60秒制限は実際の処理には短い
  - 3つのコンポーネントで実際のLLM呼び出しが複数回発生
- **優先度**: 0.8
- **ステータス**: PROVED

### 子ノード3: 環境依存の遅延仮説
- **仮説**: CI/CD環境でのネットワーク遅延
- **根拠**: テスト実行環境により通信速度が変動
- **優先度**: 0.3
- **ステータス**: UNCERTAIN

### 子ノード4: プロンプトサイズの問題仮説
- **仮説**: DeepContextAnalyzerが生成する大きなプロンプトが原因
- **根拠**: 
  - force_lightweight=Trueを指定しても制限時間内に収まらない
  - ドキュメントによるとプロンプト最適化が必要
- **優先度**: 0.7
- **ステータス**: PROVED

## 要因候補の整理

### 1. 主要因（確度: 高）
- **実LLM APIコールの累積時間**
  - 各コンポーネントが独立してLLMを呼び出す
  - 合計で10回以上のAPI呼び出しが発生
  - 1回あたり15-20秒として150-200秒必要

### 2. 副次的要因（確度: 中）
- **プロンプトサイズ**
  - DeepContextAnalyzerが詳細な分析プロンプトを生成
  - 7,000文字級のプロンプトで処理時間増大
  
- **直列処理**
  - 3つのコンポーネントが順次実行
  - 並列化の余地あり

### 3. 環境要因（確度: 低）
- **ネットワーク遅延**
- **API側のレート制限**
- **リソース競合**

## 既存の対策と履歴
1. `test_minimal_pipeline`では60秒→90秒にタイムアウト延長済み
2. `timeout_configuration.md`によるとLLM_TIMEOUT環境変数で調整可能
3. `timeout_vs_prompt_optimization_analysis.md`で両方の対策を推奨

## 結論
このテストがスキップされている理由は、**実際のLLM APIコールを使用したパフォーマンスベースライン測定が現実的な時間内に完了しない**ためです。これは設計上の制約であり、エラーではありません。

### 推奨される対応（実装は不要）
1. **モックを使用したパフォーマンステスト**を別途作成
2. **E2Eテスト**として別カテゴリで管理  
3. **CI/CD**では定期実行のみに限定
4. **タイムアウト値**を現実的な値（300秒）に設定