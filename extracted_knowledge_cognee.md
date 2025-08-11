# MANDATORY_RULES

{
  "pre_task_protocol": "(\u30bf\u30b9\u30af\u524d\u5fc5\u9808\u30ca\u30ec\u30c3\u30b8\u53c2\u7167)\n```bash\n# CRITICAL: Execute BEFORE any task - \u4f8b\u5916\u306a\u3057\n# DEFAULT: smart_knowledge_load() for ALL tasks (5-15s)\n# UPGRADE: comprehensive_knowledge_load() ONLY on explicit user request (30-60s)\n\n# \ud83d\udea8 IMPORTANT: APPLIES TO ALL CONTEXTS\n# - Regular conversation start\n# - Command execution (/command)\n# - Task continuation\n# - ANY task regardless of entry point\n\n# \ud83d\udcda IMPLEMENTATION: {KNOWLEDGE_DIR}/00-core/{FILE}\nsource {KNOWLEDGE_DIR}/00-core/{FILE}\n\nMANDATORY_SEQUENCE=(\n    \"0. DATE: Establish temporal context with date command\"\n    \"1. MCP_SELECT: Choose Serena (code/project) or Cognee (knowledge/principles) based on task\"\n    \"2. LOAD: Execute chosen MCP or smart_knowledge_load() for domain context\"\n    \"3. VERIFY: Cross-check loaded knowledge completeness\"\n    \"4. EXECUTE: Implement with continuous verification\"\n)\n\n#",
  "mcp_selection": "MCP_SELECTION_CRITERIA=(\n    \"CODE_TASK: Use Serena (editing, debugging, project structure)\"\n    \"KNOWLEDGE_TASK: Use Cognee (patterns, principles, cross-project insights)\"\n    \"HYBRID_TASK: Start with Cognee (strategy) \u2192 Apply via Serena (implementation)\"\n    \"DISCOVERY_TASK: Record in Serena \u2192 Evaluate for Cognee promotion\"\n)\n\n#",
  "security_rules": ": No secrets/credentials exposure\"\n    echo \"\u25a1 2\ufe0f\u20e3",
  "value_assessment": "(\u4fa1\u5024\u8a55\u4fa1\u5fc5\u9808)\n```bash\n# 5-POINT EVALUATION (BEFORE EVERY ACTION)\nBEFORE_ACTION_CHECKLIST=(\n    \"0. SECURITY: Exposes secrets/credentials? \u2192 STOP\"\n    \"1. USER VALUE: Serves USER not convenience? \u2192 VERIFY\"\n    \"2. LONG-TERM: Sustainable not quick-fix? \u2192 CONFIRM\"\n    \"3. FACT-BASED: Verified not speculation? \u2192 CHECK\"\n    \"4. KNOWLEDGE: Related rules loaded? \u2192 MANDATORY\"\n    \"5. ALTERNATIVES: Better approach exists? \u2192 EVALUATE\"\n)\n```\n\n### 4\ufe0f\u20e3",
  "checklist_execution": "(\u30c1\u30a7\u30c3\u30af\u30ea\u30b9\u30c8\u99c6\u52d5\u5b9f\u884c)\n```bash\n# \u2705 ALWAYS USE CHECKLISTS FOR COMPLEX TASKS\nCHECKLIST_MANDATORY=(\n    \"COMPLEX: Multi-step tasks \u2192 Create checklist FIRST\"\n    \"TRACK: Mark progress in real-time\"\n    \"VERIFY: Check completion before proceeding\"\n    \"RECORD: Save successful checklists as templates\"\n)\n\n# Checklist location\nCHECKLIST_STORAGE=\"checklists/[task_type]{FILE}\"\n\n# ENFORCEMENT\nNO_CHECKLIST_NO_PROCEED=\"Complex tasks require checklist first\"\n```\n\n### \u24ec"
}

---

# COMMAND_TEMPLATES

{
  "dag-debug-enhanced": {
    "meta": {
      "name": "Enhanced_DAG_Debugger_with_Serena_Sequential_Runner_Multi_Agent",
      "version": "2.0.0",
      "canonical": "true",
      "purpose": ">"
    },
    "execution_model": {
      "core_flow": "|"
    },
    "parameters": [],
    "pattern": "meta:"
  },
  "serena": {
    "meta": {},
    "execution_model": {},
    "parameters": [
      "--------"
    ],
    "pattern": "Token-efficient Serena MCP command for structured app development and problem-solving"
  },
  "checklistdriven": {
    "meta": {},
    "execution_model": {},
    "parameters": [],
    "pattern": "<\u30bf\u30b9\u30af/> \u306e\u5185\u5bb9\u3092\u6b63\u78ba\u306b\u89e3\u91c8\u3057\u30c1\u30a7\u30c3\u30af\u30ea\u30b9\u30c8\u30c9\u30ea\u30d6\u30f3(\u30ca\u30ec\u30c3\u30b8\u3092\u691c\u7d22\u3057\u3066\u6b63\u78ba\u306b\u610f\u5473\u3092\u628a\u63e1\u3057\u3066\u304f\u3060\u3055\u3044)\u3067\u30bf\u30b9\u30af\u3092\u5b9f\u884c\u3057\u3066\u304f\u3060\u3055\u3044"
  },
  "design": {
    "meta": {},
    "execution_model": {},
    "parameters": [],
    "pattern": "\u4ee5\u4e0b\u3001<task-design-framework/> \u306b\u5f93\u3063\u3066\u3001\u30bf\u30b9\u30af\u3092\u8a2d\u8a08\u3057\u30c1\u30a7\u30c3\u30af\u30ea\u30b9\u30c8\u30c9\u30ea\u30d6\u30f3\u3067\u5b9f\u884c\u3057\u3066\u304f\u3060\u3055\u3044\u3002"
  }
}

---

# ARCHITECTURAL_PATTERNS

{
  "a2a_architecture": {
    "principles": [],
    "components": [],
    "interactions": []
  },
  "ams_dag_debugger_technical_debt_analysis": {
    "methodology": [],
    "best_practices": [],
    "patterns": []
  },
  "ams_deployment_guide": {
    "methodology": [],
    "best_practices": [],
    "patterns": []
  },
  "ams_testing_guide": {
    "methodology": [],
    "best_practices": [],
    "patterns": []
  }
}

---
