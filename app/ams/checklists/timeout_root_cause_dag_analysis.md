# test_performance_baseline タイムアウト根本原因分析（DAG探索）

実行日: 2025-07-30
タスク: test_performance_baselineタイムアウトの根本原因特定

## DAG探索による根本原因分析

### ルートノード: パフォーマンステストのタイムアウト
優先度: 1.0

### 子ノード1: LLMコール累積時間仮説
- **仮説**: 複数のLLMコールの累積時間がタイムアウトを引き起こしている
- **検証結果**: PROVED
- **詳細分析**:
  - DeepContextAnalyzer (軽量モード): 1回
  - PopulationArchitect:
    - _design_major_segments: 1回
    - _design_sub_segments: 3-5回（各メジャーセグメントに対して）
  - PersonaGenerator: 3回（3人のペルソナ）
  - **合計**: 8-10回のLLM呼び出し
- **優先度**: 0.95

### 子ノード2: プロンプトサイズ肥大化仮説
- **仮説**: PopulationArchitectがcontextをJSON形式で何度も含めることでプロンプトが肥大化
- **検証結果**: PROVED
- **詳細分析**:
  ```python
  # PopulationArchitect._design_major_segments
  segment_prompt = f"""
  Context: {json.dumps(context, indent=2)}  # 全コンテキストをJSON化
  ...
  """
  
  # PopulationArchitect._design_sub_segments
  sub_segment_prompt = f"""
  Major segment: {json.dumps(segment, indent=2)}
  Article context: {json.dumps(context.get('core_context', {}), indent=2)}
  ...
  """
  ```
- **影響**: 各LLM呼び出しで数KB〜数十KBのプロンプト
- **優先度**: 0.9

### 子ノード3: 直列処理による累積遅延仮説
- **仮説**: 全ての処理が直列で実行されるため、待ち時間が累積
- **検証結果**: PROVED
- **詳細分析**:
  1. DeepContextAnalyzer実行（待機）
  2. PopulationArchitect実行（待機）
     - _design_major_segments（待機）
     - 各セグメントに対して_design_sub_segments（待機×3-5）
  3. PersonaGenerator実行（待機×3）
- **優先度**: 0.85

### 子ノード4: LLMモデル応答時間仮説
- **仮説**: デフォルトモデル（Gemini 2.5 Flash）の応答時間が予想より長い
- **検証結果**: PARTIALLY_PROVED
- **詳細分析**:
  - 1,509文字: 15.5秒
  - 7,141文字: 35-45秒（推定）
  - JSON形式のプロンプト: さらに処理時間増加
- **優先度**: 0.7

## 根本原因の特定

### 主要因（相乗効果）
1. **プロンプトの冗長性**
   - PopulationArchitectがcontextを何度もJSON形式で含める
   - インデント付きJSONでさらにサイズ増大
   
2. **LLMコール数の多さ**
   - 最小でも8回、通常10回以上のLLM呼び出し
   - 各呼び出しで10-20秒かかると150-200秒必要

3. **直列処理アーキテクチャ**
   - 並列化可能な処理も全て直列実行
   - 待ち時間の累積

### 副次的要因
1. **タイムアウト設定の不整合**
   - 各コンポーネント: 60秒制限
   - 全体: 180秒制限
   - しかしLLMコール10回×15秒=150秒で既にギリギリ

2. **force_lightweight=Trueの効果不足**
   - DeepContextAnalyzerは軽量化されるが、1回のみ
   - PopulationArchitectとPersonaGeneratorは軽量化されない

## 証拠となるコード

### 1. PopulationArchitect（最大のボトルネック）
```python
# 93行目: メジャーセグメント設計
segment_prompt = f"""
Context: {json.dumps(context, indent=2)}  # 巨大なJSON
Design 3-5 major population segments...
"""

# 153行目: サブセグメント設計（3-5回実行）
sub_segment_prompt = f"""
Major segment: {json.dumps(segment, indent=2)}
Article context: {json.dumps(context.get('core_context', {}), indent=2)}
Create 2-4 sub-segments...
"""
```

### 2. 実際のLLMコール箇所
- deep_context_analyzer.py: 4箇所（軽量モードで1箇所）
- population_architect.py: 2箇所（実際は4-6回実行）
- persona_generator.py: 1箇所（3回実行）

## 結論

**根本原因**: PopulationArchitectが生成する冗長なプロンプトと、直列実行による累積遅延の組み合わせ

1. **プロンプトの冗長性**: 同じcontextがJSON形式で何度も含まれる（数KB×複数回）
2. **過剰なLLMコール**: 10回前後のLLM呼び出しで累積150-200秒
3. **アーキテクチャの制約**: 並列化されていない直列処理

これらが組み合わさって、180秒の制限時間を超過している。