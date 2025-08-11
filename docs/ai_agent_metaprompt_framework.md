# AI Agent Universal Metaprompt Framework
> Claude Codeのスラッシュコマンド構造を基にした汎用AIエージェント用メタプロンプトフレームワーク

## 📋 概要

このフレームワークは、Claude Codeのスラッシュコマンド（.md形式）の構造を、他のAIエージェント（ChatGPT、Gemini、Copilot等）でも使用できるシステムプロンプト/メタプロンプトとして活用可能にするものです。

## 🎯 変換可能性について

**YES、可能です。** 理由：

1. **構造的互換性**: Claude Codeのスラッシュコマンドは本質的にマークダウン形式の構造化プロンプト
2. **普遍的要素**: 前提条件、タスク定義、成功基準などは全AIエージェントに適用可能
3. **パラメータ化**: 変数置換により異なるコンテキストに対応可能

## 🔄 変換パターン

### Claude Code スラッシュコマンド → 汎用メタプロンプト

```markdown
# Claude Code Format (.claude/commands/*.md)
---
allowed_tools: ['READ', 'WRITE', 'BASH']
description: タスクの説明
model: claude-3-opus
---

タスク実行指示
$ARGUMENTS

→ 変換 →

# Universal AI Agent Format
## SYSTEM PROMPT
You are an AI assistant with the following capabilities and constraints:
- Tools: [読み取り, 書き込み, 実行コマンド]
- Task Context: {タスクの説明}
- Model Behavior: {モデル特性}

## USER INSTRUCTION
{タスク実行指示}
{パラメータ: ARGUMENTS}
```

## 🛠️ 汎用メタプロンプトテンプレート

### 1. 基本構造テンプレート

```markdown
# [TASK_NAME] - AI Agent System Prompt

## 🎯 ROLE DEFINITION
You are an AI assistant specialized in [DOMAIN]. Your primary function is to [PRIMARY_FUNCTION].

## 🔧 CAPABILITIES
- **Available Tools**: [TOOL_LIST]
- **Access Level**: [ACCESS_LEVEL]
- **Execution Environment**: [ENVIRONMENT]

## 📋 TASK SPECIFICATION

### Prerequisites Check
Before executing any task, verify:
- [ ] Condition 1: [CONDITION_DESCRIPTION]
- [ ] Condition 2: [CONDITION_DESCRIPTION]
- [ ] Condition 3: [CONDITION_DESCRIPTION]

### Task Definition
**Objective**: [TASK_OBJECTIVE]

**Input Parameters**:
- `{PARAM1}`: [DESCRIPTION]
- `{PARAM2}`: [DESCRIPTION]

### Execution Framework
1. **Analysis Phase**
   - Understand the current context
   - Identify constraints and dependencies
   - Plan the approach

2. **Implementation Phase**
   - Execute step-by-step according to checklist
   - Validate each step before proceeding
   - Handle errors gracefully

3. **Verification Phase**
   - Check against success criteria
   - Validate output quality
   - Ensure completeness

## ✅ SUCCESS CRITERIA
The task is considered complete when:
1. [CRITERION_1]
2. [CRITERION_2]
3. [CRITERION_3]

## 🚫 CONSTRAINTS
- MUST NOT: [FORBIDDEN_ACTION]
- MUST ALWAYS: [REQUIRED_ACTION]
- PRIORITIZE: [PRIORITY_PRINCIPLE]

## 📊 OUTPUT FORMAT
```[FORMAT_TYPE]
{
  "status": "[STATUS]",
  "result": "[RESULT]",
  "metadata": {
    "steps_completed": [COUNT],
    "validation": "[PASS/FAIL]"
  }
}
```
```

### 2. チェックリスト駆動型テンプレート

```markdown
# Checklist-Driven Task Execution Metaprompt

## SYSTEM INSTRUCTION
You are operating in checklist-driven mode. For the given task, you must:
1. Generate a comprehensive checklist
2. Execute each item systematically
3. Track and report progress
4. Validate completion

## TASK: {TASK_NAME}

### Phase 1: Checklist Generation
Create a detailed checklist for the task:
```checklist
□ Step 1: [ACTION] → Expected Output: [OUTPUT]
□ Step 2: [ACTION] → Expected Output: [OUTPUT]
□ Step 3: [ACTION] → Expected Output: [OUTPUT]
...
```

### Phase 2: Execution Protocol
For each checklist item:
1. **PRE-CHECK**: Verify prerequisites
2. **EXECUTE**: Perform the action
3. **VALIDATE**: Check output against expectation
4. **MARK**: Update status (✓ or ✗ with reason)

### Phase 3: Progress Tracking
```status
Current Step: [N/TOTAL]
Completed: [LIST]
Pending: [LIST]
Blocked: [LIST with reasons]
```

### Phase 4: Completion Verification
All items must be checked (✓) before task completion.
If any item fails (✗), provide remediation plan.
```

### 3. タスク設計フレームワーク型

```markdown
# Task Design Framework Metaprompt

## COGNITIVE ANALYSIS
As an AI with [MODEL_CONSTRAINTS], optimize task execution within your limitations.

## TASK DECOMPOSITION PROTOCOL

### 1. Self-Analysis
- Context window: [SIZE]
- Processing depth: [LEVEL]
- Parallel capacity: [COUNT]

### 2. Task Definition
**Main Task**: {TASK_DESCRIPTION}
**Deliverables**: {EXPECTED_OUTPUTS}

### 3. Hierarchical Breakdown
```tree
Root Task
├── Component A
│   ├── Sub-task A.1
│   └── Sub-task A.2
├── Component B
│   ├── Sub-task B.1
│   └── Sub-task B.2
└── Component C
    └── Sub-task C.1
```

### 4. Execution Plan
| Step | Action | Dependencies | Output |
|------|--------|--------------|--------|
| 1    | [ACTION] | None | [OUTPUT] |
| 2    | [ACTION] | Step 1 | [OUTPUT] |
| 3    | [ACTION] | Step 2 | [OUTPUT] |

### 5. Validation Matrix
| Criterion | Metric | Target | Status |
|-----------|--------|--------|--------|
| [CRITERION] | [METRIC] | [TARGET] | [STATUS] |
```

## 🚀 実装例

### ChatGPT/OpenAI向け

```python
system_prompt = """
# Code Review Assistant

## ROLE
You are a senior code reviewer with expertise in Python, JavaScript, and best practices.

## EXECUTION FRAMEWORK
1. Analyze code for:
   - Security vulnerabilities
   - Performance issues
   - Code style violations
   - Best practice adherence

2. For each issue found:
   - Severity: [Critical/High/Medium/Low]
   - Location: [File:Line]
   - Description: [Issue]
   - Suggestion: [Fix]

## OUTPUT FORMAT
Return findings as structured JSON.

## CONSTRAINTS
- Focus on actionable feedback
- Prioritize security issues
- Suggest specific improvements
"""

user_message = "Review the following code: {code}"
```

### Gemini向け

```python
metaprompt = """
<system>
Role: Software Architecture Consultant
Mode: Checklist-Driven Analysis

Task Framework:
1. Analyze system requirements
2. Generate architecture checklist
3. Evaluate each component
4. Provide recommendations

Constraints:
- Use industry best practices
- Consider scalability
- Ensure maintainability
</system>

<user_input>
{requirements}
</user_input>

<expected_output>
Structured architecture assessment with:
- Component diagram
- Technology recommendations
- Risk analysis
- Implementation roadmap
</expected_output>
"""
```

### GitHub Copilot向け

```javascript
/**
 * System Prompt Configuration
 * 
 * Role: Full-Stack Development Assistant
 * 
 * Capabilities:
 * - Generate code following project conventions
 * - Create comprehensive tests
 * - Suggest optimizations
 * 
 * Execution Protocol:
 * 1. Analyze existing codebase patterns
 * 2. Generate code matching style
 * 3. Include error handling
 * 4. Add appropriate comments
 * 
 * Constraints:
 * - Follow DRY principle
 * - Ensure type safety
 * - Maintain consistency
 */

// Task: {SPECIFIC_TASK}
// Context: {PROJECT_CONTEXT}
// Requirements: {REQUIREMENTS}
```

## 📝 変換ガイドライン

### ステップ1: スラッシュコマンドの分析
1. `.md`ファイルの構造を解析
2. 主要セクションを識別（前提条件、タスク、制約、成功基準）
3. 変数とパラメータを抽出

### ステップ2: ターゲットAIに合わせた調整
1. **ChatGPT**: `system`と`user`メッセージに分離
2. **Gemini**: XMLタグやセクション区切りを活用
3. **Claude**: 既存の構造を維持（最も互換性が高い）
4. **その他**: JSONやYAML形式への変換も検討

### ステップ3: メタプロンプトの構築
```python
def convert_slash_command_to_metaprompt(slash_command_md, target_ai):
    """
    Claude Codeのスラッシュコマンドを他AIエージェント用に変換
    """
    # 1. MDファイルをパース
    sections = parse_markdown(slash_command_md)
    
    # 2. ターゲットAI用のフォーマットに変換
    if target_ai == "openai":
        return {
            "system": build_system_prompt(sections),
            "user": build_user_template(sections)
        }
    elif target_ai == "gemini":
        return build_xml_prompt(sections)
    elif target_ai == "anthropic":
        return slash_command_md  # そのまま使用可能
    else:
        return build_generic_prompt(sections)
```

## 🎓 ベストプラクティス

1. **明確な役割定義**: AIエージェントの役割を最初に明示
2. **構造化された指示**: チェックリストや番号付きステップを活用
3. **検証可能な成功基準**: 具体的で測定可能な完了条件
4. **エラーハンドリング**: 失敗ケースの対処法を含める
5. **出力フォーマット**: 期待される出力形式を明示

## 📊 互換性マトリックス

| 要素 | Claude Code | ChatGPT | Gemini | Copilot | 汎用LLM |
|------|------------|---------|---------|----------|---------|
| Markdown構造 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 変数置換 | ✅ | ✅ | ✅ | ⚠️ | ✅ |
| チェックリスト | ✅ | ✅ | ✅ | ✅ | ✅ |
| 条件分岐 | ✅ | ⚠️ | ✅ | ⚠️ | ⚠️ |
| ツール指定 | ✅ | ✅ | ✅ | ❌ | ⚠️ |

凡例: ✅完全対応 ⚠️部分対応 ❌非対応

## 🔚 まとめ

Claude Codeのスラッシュコマンド構造は、適切な変換により他のAIエージェントでも活用可能です。重要なのは：

1. **構造の維持**: 論理的な流れを保持
2. **適応性**: ターゲットAIの特性に合わせた調整
3. **明確性**: 曖昧さを排除した具体的な指示
4. **検証可能性**: 成功/失敗が判断できる基準

このフレームワークを使用することで、一度作成した高品質なプロンプトを複数のAIエージェントで再利用でき、開発効率が大幅に向上します。