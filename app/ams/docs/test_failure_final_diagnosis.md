# test_minimal_pipeline 失敗の最終診断

## 根本原因（確定）

### デバッグログから判明した事実

1. **`_analyze_core_dimensions`**
   - プロンプトサイズ: **1,509文字**
   - 実行時間: **15.458秒**
   - 結果: ✓ 成功

2. **`_discover_hidden_dimensions`**
   - プロンプトサイズ: **7,141文字**
   - initial_analysis_str_size: **6,263文字**
   - 実行時間: タイムアウト（30秒）
   - 結果: ✗ 失敗

## 問題の本質

**プロンプトサイズが大きすぎる**

`_discover_hidden_dimensions`は前のステップの分析結果（6,263文字のJSON）を
プロンプトに含めているため、合計7,141文字の巨大なプロンプトになっている。

### なぜタイムアウトするのか

1. Gemini APIは大きなプロンプトの処理に時間がかかる
2. 30秒のタイムアウトでは不十分
3. プロンプトが大きいほど、レスポンス生成も遅くなる

## 解決策

### 1. 即時対応（回避策）

```python
# DeepContextAnalyzerを修正
async def _discover_hidden_dimensions(self, article, initial_analysis):
    # initial_analysisを要約して小さくする
    summary = {
        "domain": initial_analysis.get("domain_analysis", {}).get("primary_domain", "Unknown"),
        "complexity": initial_analysis.get("domain_analysis", {}).get("technical_complexity", 5),
        "stakeholders": len(initial_analysis.get("stakeholder_mapping", {}).get("beneficiaries", [])),
    }
    
    # より短いプロンプトを使用
    discovery_prompt = f"""
    Given this article summary and key insights:
    Domain: {summary['domain']}
    Complexity: {summary['complexity']}/10
    Stakeholder groups: {summary['stakeholders']}
    
    Identify 3 UNEXPECTED dimensions...
    """
```

### 2. タイムアウト延長

```python
# テストのタイムアウトを60秒に延長
context = await asyncio.wait_for(
    analyzer.analyze_article_context(short_article),
    timeout=60.0  # 30秒→60秒
)
```

### 3. プロンプト最適化

- initial_analysisの全体をプロンプトに含めない
- 重要な情報のみを抽出してサマリーを作成
- プロンプトを2,000文字以下に制限

## 推奨アクション

1. **短期的**: プロンプトサイズを削減
2. **中期的**: 分析を段階的に実行（大きな分析を小さなステップに分割）
3. **長期的**: より効率的なプロンプトエンジニアリング

## 確認された事実

- LLM自体は正常に動作している
- 1,500文字程度のプロンプトは15秒で処理可能
- 7,000文字を超えるプロンプトは現在の設定では処理できない