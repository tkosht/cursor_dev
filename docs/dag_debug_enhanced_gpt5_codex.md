# GPT-5 Codex向け Enhanced DAG Debugger メタプロンプト

## システムプロンプト構成

```python
system_prompt = """
# Enhanced DAG Debugger - GPT-5 Codex Configuration

## ROLE DEFINITION
You are an advanced debugging specialist with multi-agent coordination capabilities.
You employ DAG (Directed Acyclic Graph) exploration, semantic code analysis, and 
sequential reasoning to solve complex technical problems.

## CORE CAPABILITIES

### 1. Diagnostic Framework
- **Sequential Analysis**: Step-by-step problem decomposition
- **Hypothesis Generation**: Create multiple testable theories
- **Parallel Exploration**: Evaluate top 3 hypotheses simultaneously

### 2. DAG Exploration Model
Execute problem-solving as a directed graph where:
- Each node represents a hypothesis or investigation step
- Edges represent logical dependencies
- Priority scoring determines traversal order

### 3. Semantic Code Analysis
Perform deep code understanding through:
- Symbol identification and dependency mapping
- Impact analysis of recent changes
- Pattern recognition across codebase

## EXECUTION PROTOCOL

### Phase 1: Initial Diagnosis
```checklist
□ Capture problem symptoms and error messages
□ Analyze recent code changes (git diff)
□ Generate initial hypothesis set (minimum 3)
□ Create diagnostic test cases
```

### Phase 2: DAG Exploration
```algorithm
for each hypothesis in priority_queue:
    1. Semantic Analysis:
       - Identify relevant code symbols
       - Map dependencies and references
       - Analyze code structure patterns
    
    2. Verification Design:
       - Define preconditions
       - Create test scenarios
       - Specify expected outcomes
    
    3. Execution & Validation:
       - Run diagnostic tests
       - Compare against expectations
       - Update hypothesis confidence
    
    4. Decision Point:
       if (confidence > 0.8):
           proceed_to_fix_validation()
       elif (new_evidence_found):
           generate_refined_hypothesis()
       else:
           explore_next_hypothesis()
```

### Phase 3: Fix Validation
```validation_protocol
Pre-Fix:
  - capture_baseline_state()
  - create_reproduction_test()
  - identify_affected_components()

Post-Fix:
  - verify_reproduction_test_passes()
  - run_unit_test_suite()
  - run_integration_tests()
  - check_performance_metrics()
  - scan_security_implications()

Documentation:
  - root_cause_explanation
  - fix_implementation_rationale
  - test_coverage_report
  - rollback_procedure
```

## PRIORITY SCORING ALGORITHM

```python
def calculate_priority(node):
    suspicion_score = (
        recent_change_correlation * 0.4 +
        code_complexity * 0.2 +
        error_pattern_match * 0.3 +
        historical_bug_density * 0.1
    )
    
    cost_estimate = (
        execution_time * 0.3 +
        token_usage * 0.3 +
        api_calls * 0.2 +
        cognitive_complexity * 0.2
    )
    
    urgency_factor = get_urgency_from_context()
    
    return (suspicion_score * urgency_factor) / (1 + cost_estimate)
```

## CONSTRAINTS & REQUIREMENTS

1. **Verification Mandatory**: No fix without reproduction test
2. **Regression Prevention**: Full test suite must pass
3. **Documentation Required**: Every change needs explanation
4. **Performance Guard**: No degradation allowed
5. **Incremental Progress**: Report findings at each node

## OUTPUT FORMAT

Return structured JSON with:
```json
{
  "diagnosis": {
    "problem_statement": "string",
    "root_cause": "string",
    "confidence": "float"
  },
  "exploration_trace": {
    "nodes_visited": ["array"],
    "hypotheses_tested": ["array"],
    "key_findings": ["array"]
  },
  "fix": {
    "description": "string",
    "files_modified": ["array"],
    "validation_results": {
      "reproduction_test": "pass/fail",
      "unit_tests": {"passed": N, "failed": N},
      "integration_tests": {"passed": N, "failed": N},
      "performance_impact": "percentage"
    }
  },
  "recommendations": {
    "immediate_actions": ["array"],
    "monitoring": ["array"],
    "documentation_updates": ["array"]
  }
}
```
"""

# ユーザープロンプトテンプレート
user_prompt_template = """
## DEBUG REQUEST

**Problem Description**: {problem_description}

**Configuration**:
- Max Depth: {max_depth}
- Time Limit: {time_limit} minutes
- Parallel Width: {parallel_width}
- Focus Area: {focus_area}
- Verbose Mode: {verbose}

**Available Context**:
- Recent Changes: {recent_commits}
- Error Logs: {error_logs}
- System State: {system_state}

**Execution Instructions**:
1. Begin with Sequential Analysis of the problem
2. Generate and prioritize hypotheses using DAG structure
3. For each hypothesis node:
   - Perform semantic code analysis
   - Design verification tests
   - Execute and evaluate results
4. When root cause identified (confidence > 0.8):
   - Implement fix
   - Run complete validation protocol
   - Generate comprehensive report

Please proceed with the debugging process following the Enhanced DAG Debugger protocol.
"""
```

## OpenAI Function Calling形式への変換

```python
from typing import List, Dict, Optional
import openai

class GPT5CodexDAGDebugger:
    def __init__(self, api_key: str):
        self.client = openai.Client(api_key=api_key)
        self.system_prompt = system_prompt  # 上記で定義
        
    # Function定義（OpenAI Function Calling用）
    functions = [
        {
            "name": "analyze_code_semantically",
            "description": "Perform semantic analysis on code symbols",
            "parameters": {
                "type": "object",
                "properties": {
                    "target_symbols": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of code symbols to analyze"
                    },
                    "analysis_depth": {
                        "type": "integer",
                        "description": "Depth of dependency analysis"
                    },
                    "include_references": {
                        "type": "boolean",
                        "description": "Include reference analysis"
                    }
                },
                "required": ["target_symbols"]
            }
        },
        {
            "name": "execute_diagnostic_test",
            "description": "Run diagnostic test for hypothesis validation",
            "parameters": {
                "type": "object",
                "properties": {
                    "test_name": {
                        "type": "string",
                        "description": "Name of the diagnostic test"
                    },
                    "test_code": {
                        "type": "string",
                        "description": "Test implementation code"
                    },
                    "expected_outcome": {
                        "type": "object",
                        "description": "Expected test results"
                    }
                },
                "required": ["test_name", "test_code"]
            }
        },
        {
            "name": "update_dag_node",
            "description": "Update DAG exploration node with findings",
            "parameters": {
                "type": "object",
                "properties": {
                    "node_id": {
                        "type": "string",
                        "description": "DAG node identifier"
                    },
                    "findings": {
                        "type": "object",
                        "description": "Node exploration findings"
                    },
                    "confidence": {
                        "type": "number",
                        "description": "Confidence score (0-1)"
                    },
                    "next_actions": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Recommended next steps"
                    }
                },
                "required": ["node_id", "findings", "confidence"]
            }
        },
        {
            "name": "apply_fix_with_validation",
            "description": "Apply fix and run validation protocol",
            "parameters": {
                "type": "object",
                "properties": {
                    "fix_description": {
                        "type": "string",
                        "description": "Description of the fix"
                    },
                    "code_changes": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "file": {"type": "string"},
                                "changes": {"type": "string"}
                            }
                        },
                        "description": "List of code changes"
                    },
                    "validation_tests": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Tests to run for validation"
                    }
                },
                "required": ["fix_description", "code_changes"]
            }
        }
    ]
    
    def debug_problem(
        self,
        problem_description: str,
        max_depth: int = 8,
        time_limit: int = 30,
        parallel_width: int = 3,
        focus_area: Optional[str] = None,
        verbose: bool = False
    ) -> Dict:
        """
        Execute Enhanced DAG Debugging process
        """
        
        # ユーザープロンプトの構築
        user_prompt = user_prompt_template.format(
            problem_description=problem_description,
            max_depth=max_depth,
            time_limit=time_limit,
            parallel_width=parallel_width,
            focus_area=focus_area or "all",
            verbose=verbose,
            recent_commits=self._get_recent_commits(),
            error_logs=self._get_error_logs(),
            system_state=self._get_system_state()
        )
        
        # GPT-5 Codex実行
        response = self.client.chat.completions.create(
            model="gpt-5-codex",  # 仮定のモデル名
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            functions=self.functions,
            function_call="auto",
            temperature=0.2,  # デバッグには低温度設定
            max_tokens=8000
        )
        
        return self._process_response(response)
    
    def _process_response(self, response) -> Dict:
        """レスポンスを処理して構造化された結果を返す"""
        # Function callsの処理とDAG実行トレースの構築
        pass
    
    def _get_recent_commits(self) -> str:
        """最近のコミット情報を取得"""
        pass
    
    def _get_error_logs(self) -> str:
        """エラーログを取得"""
        pass
    
    def _get_system_state(self) -> str:
        """システム状態を取得"""
        pass
```

## 使用例

```python
# GPT-5 Codex DAG Debuggerの初期化
debugger = GPT5CodexDAGDebugger(api_key="your-api-key")

# デバッグ実行
result = debugger.debug_problem(
    problem_description="Production memory leak in user service causing OOM after 6 hours",
    max_depth=10,
    time_limit=45,
    parallel_width=5,
    focus_area="backend",
    verbose=True
)

# 結果の表示
print(f"Root Cause: {result['diagnosis']['root_cause']}")
print(f"Confidence: {result['diagnosis']['confidence']}")
print(f"Fix Applied: {result['fix']['description']}")
print(f"Validation: {result['fix']['validation_results']}")
```

## Codex特有の最適化

### 1. コード生成能力の活用
```python
# Codexの強力なコード生成を活用した診断テスト自動生成
def generate_diagnostic_test(self, hypothesis: str) -> str:
    prompt = f"""
    Generate a diagnostic test to validate the hypothesis:
    {hypothesis}
    
    The test should:
    - Be minimal and focused
    - Return clear pass/fail result
    - Include error handling
    """
    # Codexがテストコードを自動生成
```

### 2. トークン効率の最適化
```python
# DAGノードの並列処理でトークン使用を最適化
async def parallel_hypothesis_exploration(self, hypotheses: List[str]):
    tasks = []
    for hypothesis in hypotheses[:self.parallel_width]:
        task = asyncio.create_task(
            self.explore_hypothesis(hypothesis)
        )
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    return self.select_best_result(results)
```

### 3. コンテキスト管理
```python
class DAGContext:
    """DAG探索のコンテキストを効率的に管理"""
    def __init__(self):
        self.global_context = {}  # 不変のグローバル情報
        self.node_contexts = {}   # 各ノードのローカル情報
        self.thought_chain = []   # 推論の連鎖
    
    def propagate(self, direction: str, data: Dict):
        """コンテキストの伝播（上方/下方/横方向）"""
        pass
```

## まとめ

このGPT-5 Codex向け変換では：

1. **構造の保持**: DAG探索とマルチエージェント協調の概念を維持
2. **API適応**: OpenAI Function Calling形式に最適化
3. **Codex特性活用**: 強力なコード生成・解析能力を最大限活用
4. **効率化**: トークン使用とレスポンス時間の最適化

Claude Codeの`/dag-debug-enhanced`の高度な機能をGPT-5 Codexで実現可能にしています。