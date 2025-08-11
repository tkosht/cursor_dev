#!/usr/bin/env python3
"""
Core Knowledge Extraction Script for Serena & Cognee Integration
Extracts essential patterns and principles for cross-repository reuse
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Any

class KnowledgeExtractor:
    """Extract and categorize knowledge for Serena/Cognee storage"""
    
    def __init__(self, workspace_path: str = "/home/devuser/workspace"):
        self.workspace = Path(workspace_path)
        self.extracted_knowledge = {
            "cognee_patterns": {},
            "serena_memories": {}
        }
    
    def extract_mandatory_rules(self) -> Dict[str, Any]:
        """Extract core mandatory rules from AGENTS.md"""
        agents_file = self.workspace / "AGENTS.md"
        
        if not agents_file.exists():
            return {}
        
        content = agents_file.read_text()
        
        # Extract key patterns
        patterns = {
            "pre_task_protocol": self._extract_section(
                content, 
                "PRE-TASK KNOWLEDGE PROTOCOL",
                "COMMAND EXECUTION SPECIFIC"
            ),
            "mcp_selection": self._extract_section(
                content,
                "MCP SELECTION CRITERIA",
                "ENFORCEMENT"
            ),
            "security_rules": self._extract_section(
                content,
                "SECURITY ABSOLUTE",
                "VALUE ASSESSMENT"
            ),
            "value_assessment": self._extract_section(
                content,
                "VALUE ASSESSMENT MANDATORY",
                "CORE OPERATING PRINCIPLES"
            ),
            "checklist_execution": self._extract_section(
                content,
                "CHECKLIST-DRIVEN EXECUTION",
                "TASK DESIGN FRAMEWORK"
            )
        }
        
        # Clean and abstract patterns
        return self._abstract_patterns(patterns)
    
    def extract_command_templates(self) -> Dict[str, Any]:
        """Extract meta-prompt patterns from .claude/commands"""
        commands_dir = self.workspace / ".claude" / "commands" / "tasks"
        
        if not commands_dir.exists():
            return {}
        
        templates = {}
        priority_commands = [
            "dag-debug-enhanced.md",
            "serena.md", 
            "checklistdriven.md",
            "design.md"
        ]
        
        for cmd_file in priority_commands:
            cmd_path = commands_dir / cmd_file
            if cmd_path.exists():
                content = cmd_path.read_text()
                
                # Extract meta structure
                templates[cmd_file.replace(".md", "")] = {
                    "meta": self._extract_yaml_section(content, "meta:"),
                    "execution_model": self._extract_yaml_section(content, "execution_model:"),
                    "parameters": self._extract_parameters(content),
                    "pattern": self._extract_pattern_description(content)
                }
        
        return templates
    
    def extract_architectural_patterns(self) -> Dict[str, Any]:
        """Extract reusable architectural patterns"""
        patterns = {}
        
        # Extract from basic design
        design_dir = self.workspace / "docs" / "02.basic_design"
        if design_dir.exists():
            for design_file in design_dir.glob("*.md"):
                content = design_file.read_text()
                patterns[design_file.stem] = self._extract_design_patterns(content)
        
        # Extract from AMS docs
        ams_docs = self.workspace / "app" / "ams" / "docs"
        if ams_docs.exists():
            priority_files = [
                "dag_debugger_technical_debt_analysis.md",
                "deployment_guide.md",
                "testing_guide.md"
            ]
            
            for filename in priority_files:
                filepath = ams_docs / filename
                if filepath.exists():
                    content = filepath.read_text()
                    patterns[f"ams_{filename.replace('.md', '')}"] = \
                        self._extract_implementation_patterns(content)
        
        return patterns
    
    def build_project_hierarchy(self) -> Dict[str, Any]:
        """Build project-specific hierarchy for Serena"""
        return {
            "repository": {
                "name": "ai-agent-workspace",
                "type": "multi-agent-development",
                "structure": {
                    "docs": "Documentation and guides",
                    "app/ams": "Agent Management System",
                    "memory-bank": "Knowledge storage patterns",
                    ".claude/commands": "Dynamic prompt templates",
                    "scripts": "Automation and utilities",
                    "checklists": "Execution checklists"
                }
            },
            "modules": {
                "ams": {
                    "description": "Multi-agent orchestration system",
                    "key_patterns": ["DAG exploration", "Sequential thinking", "Agent hierarchy"]
                },
                "memory_bank": {
                    "description": "Knowledge management system",
                    "key_patterns": ["Knowledge loading", "Session initialization", "Rule enforcement"]
                },
                "commands": {
                    "description": "Dynamic prompt system",
                    "key_patterns": ["Meta-prompts", "Parameter handling", "Context adaptation"]
                }
            },
            "constraints": {
                "branch_patterns": "feature/*, docs/*, fix/*, task/*",
                "testing": "TDD mandatory, no mocks in integration tests",
                "quality_gates": "Pre-commit hooks, type checking, linting"
            }
        }
    
    def _extract_section(self, content: str, start_marker: str, end_marker: str) -> str:
        """Extract content between markers"""
        pattern = rf"{re.escape(start_marker)}(.*?){re.escape(end_marker)}"
        match = re.search(pattern, content, re.DOTALL)
        return match.group(1).strip() if match else ""
    
    def _extract_yaml_section(self, content: str, marker: str) -> Dict:
        """Extract YAML-like section from markdown"""
        lines = content.split('\n')
        in_section = False
        section_lines = []
        indent_level = 0
        
        for line in lines:
            if marker in line:
                in_section = True
                indent_level = len(line) - len(line.lstrip())
                continue
            
            if in_section:
                current_indent = len(line) - len(line.lstrip())
                if current_indent <= indent_level and line.strip() and not line.startswith(' '):
                    break
                section_lines.append(line)
        
        # Parse simplified YAML structure
        return self._parse_yaml_lines(section_lines)
    
    def _parse_yaml_lines(self, lines: List[str]) -> Dict:
        """Simple YAML-like parser for extracted sections"""
        result = {}
        current_key = None
        
        for line in lines:
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                continue
                
            if ':' in stripped and not stripped.startswith('-'):
                key, value = stripped.split(':', 1)
                current_key = key.strip()
                value = value.strip()
                
                if value:
                    result[current_key] = value.strip('"\'')
                else:
                    result[current_key] = []
            elif current_key and stripped.startswith('-'):
                if isinstance(result[current_key], list):
                    result[current_key].append(stripped[1:].strip())
                else:
                    result[current_key] = [stripped[1:].strip()]
        
        return result
    
    def _extract_parameters(self, content: str) -> List[str]:
        """Extract command parameters/options"""
        params = []
        
        # Look for options section
        if "## Options" in content or "Options:" in content:
            lines = content.split('\n')
            in_options = False
            
            for line in lines:
                if "Options" in line:
                    in_options = True
                    continue
                
                if in_options:
                    if line.startswith('|') and '-' in line:
                        # Parse table format
                        parts = line.split('|')
                        if len(parts) > 1:
                            param = parts[1].strip()
                            if param.startswith('-'):
                                params.append(param)
                    elif line.startswith('#') and not line.startswith('##'):
                        break
        
        return params
    
    def _extract_pattern_description(self, content: str) -> str:
        """Extract pattern description from command"""
        lines = content.split('\n')
        
        for line in lines:
            if 'description:' in line:
                return line.split('description:', 1)[1].strip()
        
        # Fallback to first non-metadata line
        for line in lines:
            if line.strip() and not line.startswith('#') and not line.startswith('-'):
                return line.strip()
        
        return ""
    
    def _extract_design_patterns(self, content: str) -> Dict:
        """Extract design patterns from architecture documents"""
        patterns = {
            "principles": [],
            "components": [],
            "interactions": []
        }
        
        # Extract architectural principles
        if "## Architecture" in content or "## Design" in content:
            principles_section = self._extract_section(
                content, 
                "Architecture", 
                "Implementation"
            )
            patterns["principles"] = self._extract_bullet_points(principles_section)
        
        # Extract component patterns
        if "## Components" in content:
            components_section = self._extract_section(
                content,
                "Components",
                "##"
            )
            patterns["components"] = self._extract_bullet_points(components_section)
        
        return patterns
    
    def _extract_implementation_patterns(self, content: str) -> Dict:
        """Extract implementation patterns from technical documents"""
        return {
            "methodology": self._extract_bullet_points(
                self._extract_section(content, "## Methodology", "##")
            ),
            "best_practices": self._extract_bullet_points(
                self._extract_section(content, "Best Practices", "##")
            ),
            "patterns": self._extract_bullet_points(
                self._extract_section(content, "Pattern", "##")
            )
        }
    
    def _extract_bullet_points(self, text: str) -> List[str]:
        """Extract bullet points from text"""
        points = []
        for line in text.split('\n'):
            if line.strip().startswith(('-', '*', '•', '+')):
                points.append(line.strip()[1:].strip())
        return points
    
    def _abstract_patterns(self, patterns: Dict) -> Dict:
        """Abstract patterns to remove project-specific details"""
        abstracted = {}
        
        for key, value in patterns.items():
            if isinstance(value, str):
                # Remove absolute paths
                value = re.sub(r'/home/[^/]+/[^/]+/', '{PROJECT_ROOT}/', value)
                # Remove specific file names
                value = re.sub(r'[a-zA-Z0-9_-]+\.(py|md|sh|js)', '{FILE}', value)
                # Abstract specific names
                value = re.sub(r'memory-bank/', '{KNOWLEDGE_DIR}/', value)
                
            abstracted[key] = value
        
        return abstracted
    
    def generate_cognee_knowledge(self) -> str:
        """Generate Cognee-ready knowledge structure"""
        knowledge = {
            "mandatory_rules": self.extract_mandatory_rules(),
            "command_templates": self.extract_command_templates(),
            "architectural_patterns": self.extract_architectural_patterns()
        }
        
        # Format for Cognee ingestion
        cognee_format = []
        
        for category, content in knowledge.items():
            cognee_format.append(f"# {category.upper()}\n")
            cognee_format.append(json.dumps(content, indent=2))
            cognee_format.append("\n---\n")
        
        return '\n'.join(cognee_format)
    
    def generate_serena_memories(self) -> Dict[str, str]:
        """Generate Serena memory structures"""
        memories = {
            "project_hierarchy": json.dumps(
                self.build_project_hierarchy(), 
                indent=2
            ),
            "mcp_usage_strategy": self._create_mcp_strategy_memory(),
            "dynamic_prompt_loading": self._create_prompt_loading_memory()
        }
        
        return memories
    
    def _create_mcp_strategy_memory(self) -> str:
        """Create MCP usage strategy memory"""
        return """
# MCP Usage Strategy for Cross-Repository Knowledge

## Selection Criteria
- **Serena**: Use for project-specific code, configurations, and constraints
- **Cognee**: Use for patterns, principles, and cross-project knowledge

## Access Patterns
1. Check Cognee for design patterns and methodologies
2. Load Serena memories for project context
3. Merge and adapt for current task

## Optimization Tips
- Cache frequently used patterns
- Batch knowledge queries
- Use specific search terms
"""
    
    def _create_prompt_loading_memory(self) -> str:
        """Create dynamic prompt loading instructions"""
        return """
# Dynamic Prompt Loading System

## Loading Mechanism
1. Query available commands from Cognee
2. Fetch command template structure
3. Get project context from Serena
4. Merge template with context
5. Execute adapted prompt

## Adaptation Rules
- Replace {PROJECT_ROOT} with actual path
- Substitute {PARAMETERS} with task-specific values
- Inject project constraints from Serena
- Apply security and quality rules

## Cross-CLI Compatibility
- Extract core prompt structure
- Adapt to CLI-specific syntax
- Maintain parameter compatibility
- Preserve execution model
"""


def main():
    """Execute knowledge extraction"""
    print("🚀 Starting Core Knowledge Extraction...")
    
    extractor = KnowledgeExtractor()
    
    # Generate Cognee knowledge
    print("📊 Generating Cognee knowledge graph content...")
    cognee_content = extractor.generate_cognee_knowledge()
    
    # Save Cognee-ready content
    cognee_file = Path("/home/devuser/workspace/extracted_knowledge_cognee.md")
    cognee_file.write_text(cognee_content)
    print(f"✅ Cognee knowledge saved to: {cognee_file}")
    
    # Generate Serena memories
    print("📝 Generating Serena memory structures...")
    serena_memories = extractor.generate_serena_memories()
    
    # Save Serena memories
    for memory_name, content in serena_memories.items():
        memory_file = Path(f"/home/devuser/workspace/serena_memory_{memory_name}.md")
        memory_file.write_text(content)
        print(f"✅ Serena memory saved: {memory_file}")
    
    print("\n🎯 Knowledge extraction complete!")
    print("Next steps:")
    print("1. Review extracted knowledge files")
    print("2. Load into Cognee using cognify()")
    print("3. Store in Serena using write_memory()")
    print("4. Test cross-repository access")


if __name__ == "__main__":
    main()