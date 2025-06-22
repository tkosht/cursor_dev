#!/usr/bin/env python3
"""
Task Completion Integrity Check

This script verifies task completion against predefined criteria,
detects completion condition drift, and enforces quality standards.

Usage:
    python scripts/task_completion_check.py --task "task_name" --mode [check|strict|report]
    python scripts/task_completion_check.py --define-criteria "task_name"
    python scripts/task_completion_check.py --check-drift "task_name"
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class TaskCompletionChecker:
    """Task Completion Integrity verification system."""
    
    def __init__(self, workspace_path: str = "/home/devuser/workspace"):
        self.workspace_path = Path(workspace_path)
        self.criteria_file = self.workspace_path / "memory-bank" / "09-meta" / "completion_criteria_tracker.md"
        self.quality_tools = {
            "flake8": ["flake8", "app/", "tests/", "--statistics"],
            "black": ["black", "app/", "tests/", "--check", "--diff"],
            "mypy": ["mypy", "app/", "--show-error-codes"],
            "pytest": ["pytest", "--cov=app", "--cov-fail-under=85"],
            "security": ["python", "scripts/security_check.py"],
            "user_auth": ["python", "scripts/check_user_authorization.py"]
        }
        
    def define_completion_criteria(self, task_name: str) -> Dict:
        """Interactive completion criteria definition."""
        print(f"🎯 Defining completion criteria for: {task_name}")
        print("=" * 60)
        
        criteria = {
            "task_name": task_name,
            "defined_at": datetime.now().isoformat(),
            "must_conditions": [],
            "should_conditions": [],
            "could_conditions": [],
            "acceptance_tests": [],
            "user_agreement": False
        }
        
        # MUST conditions
        print("\n🚨 MUST CONDITIONS (Required for completion - 100% necessary)")
        print("Enter MUST conditions (press Enter on empty line to finish):")
        while True:
            condition = input("MUST: ").strip()
            if not condition:
                break
            criteria["must_conditions"].append(condition)
        
        # SHOULD conditions  
        print("\n📋 SHOULD CONDITIONS (Quality standards - 80%+ recommended)")
        print("Enter SHOULD conditions (press Enter on empty line to finish):")
        while True:
            condition = input("SHOULD: ").strip()
            if not condition:
                break
            criteria["should_conditions"].append(condition)
            
        # COULD conditions
        print("\n✨ COULD CONDITIONS (Nice to have - bonus points)")
        print("Enter COULD conditions (press Enter on empty line to finish):")
        while True:
            condition = input("COULD: ").strip()
            if not condition:
                break
            criteria["could_conditions"].append(condition)
            
        # Acceptance Tests
        print("\n🧪 ACCEPTANCE TESTS")
        print("Enter acceptance tests (press Enter on empty line to finish):")
        while True:
            test = input("TEST: ").strip()
            if not test:
                break
            criteria["acceptance_tests"].append(test)
            
        # User agreement confirmation
        print("\n📋 COMPLETION CRITERIA SUMMARY")
        print("=" * 60)
        self._display_criteria(criteria)
        
        agreement = input("\nDo you agree with these completion criteria? (y/N): ").lower()
        criteria["user_agreement"] = agreement in ['y', 'yes']
        
        if criteria["user_agreement"]:
            self._save_criteria(criteria)
            print("✅ Completion criteria saved successfully!")
        else:
            print("❌ Completion criteria not saved. Please redefine.")
            
        return criteria
        
    def check_completion_status(self, task_name: str, strict_mode: bool = False) -> Tuple[bool, Dict]:
        """Check if task meets completion criteria."""
        criteria = self._load_criteria(task_name)
        if not criteria:
            print(f"❌ No completion criteria found for task: {task_name}")
            return False, {}
            
        print(f"🔍 Checking completion status for: {task_name}")
        print("=" * 60)
        
        results = {
            "task_name": task_name,
            "checked_at": datetime.now().isoformat(),
            "must_results": [],
            "should_results": [],
            "could_results": [],
            "acceptance_test_results": [],
            "quality_gate_results": {},
            "overall_status": "incomplete"
        }
        
        # Check MUST conditions
        must_passed = 0
        must_total = len(criteria["must_conditions"])
        print(f"\n🚨 MUST CONDITIONS ({must_total} total)")
        for i, condition in enumerate(criteria["must_conditions"], 1):
            status = self._check_condition(condition, "MUST")
            results["must_results"].append({"condition": condition, "status": status})
            if status:
                must_passed += 1
            print(f"  {i}. {'✅' if status else '❌'} {condition}")
            
        # Check SHOULD conditions
        should_passed = 0
        should_total = len(criteria["should_conditions"])
        print(f"\n📋 SHOULD CONDITIONS ({should_total} total)")
        for i, condition in enumerate(criteria["should_conditions"], 1):
            status = self._check_condition(condition, "SHOULD")
            results["should_results"].append({"condition": condition, "status": status})
            if status:
                should_passed += 1
            print(f"  {i}. {'✅' if status else '❌'} {condition}")
            
        # Check COULD conditions
        could_passed = 0
        could_total = len(criteria["could_conditions"])
        print(f"\n✨ COULD CONDITIONS ({could_total} total)")
        for i, condition in enumerate(criteria["could_conditions"], 1):
            status = self._check_condition(condition, "COULD")
            results["could_results"].append({"condition": condition, "status": status})
            if status:
                could_passed += 1
            print(f"  {i}. {'✅' if status else '❌'} {condition}")
            
        # Run acceptance tests
        print(f"\n🧪 ACCEPTANCE TESTS ({len(criteria['acceptance_tests'])} total)")
        acceptance_passed = 0
        for i, test in enumerate(criteria["acceptance_tests"], 1):
            status = self._run_acceptance_test(test)
            results["acceptance_test_results"].append({"test": test, "status": status})
            if status:
                acceptance_passed += 1
            print(f"  {i}. {'✅' if status else '❌'} {test}")
            
        # Run quality gates
        print(f"\n🔧 QUALITY GATES")
        quality_results = self._run_quality_gates()
        results["quality_gate_results"] = quality_results
        
        # Overall completion assessment
        must_completion = (must_passed / must_total * 100) if must_total > 0 else 100
        should_completion = (should_passed / should_total * 100) if should_total > 0 else 100
        could_completion = (could_passed / could_total * 100) if could_total > 0 else 100
        acceptance_completion = (acceptance_passed / len(criteria["acceptance_tests"]) * 100) if criteria["acceptance_tests"] else 100
        
        print(f"\n📊 COMPLETION SUMMARY")
        print("=" * 60)
        print(f"MUST Conditions:      {must_passed}/{must_total} ({must_completion:.1f}%)")
        print(f"SHOULD Conditions:    {should_passed}/{should_total} ({should_completion:.1f}%)")
        print(f"COULD Conditions:     {could_passed}/{could_total} ({could_completion:.1f}%)")
        print(f"Acceptance Tests:     {acceptance_passed}/{len(criteria['acceptance_tests'])} ({acceptance_completion:.1f}%)")
        
        # Completion criteria
        is_complete = (
            must_completion == 100.0 and
            acceptance_completion == 100.0 and
            should_completion >= 80.0 and
            quality_results.get("overall_pass", False)
        )
        
        if strict_mode:
            is_complete = is_complete and should_completion == 100.0
            
        results["overall_status"] = "complete" if is_complete else "incomplete"
        
        print(f"\n🎯 OVERALL STATUS: {'✅ COMPLETE' if is_complete else '❌ INCOMPLETE'}")
        
        if not is_complete:
            print("\n⚠️ COMPLETION BLOCKERS:")
            if must_completion < 100:
                print(f"  - MUST conditions: {must_total - must_passed} remaining")
            if acceptance_completion < 100:
                print(f"  - Acceptance tests: {len(criteria['acceptance_tests']) - acceptance_passed} failing")
            if should_completion < 80:
                print(f"  - SHOULD conditions: {should_completion:.1f}% (need 80%+)")
            if not quality_results.get("overall_pass", False):
                print(f"  - Quality gates: Failed checks detected")
                
        return is_complete, results
        
    def check_drift(self, task_name: str) -> Dict:
        """Check for completion criteria drift."""
        criteria = self._load_criteria(task_name)
        if not criteria:
            return {"error": f"No criteria found for task: {task_name}"}
            
        print(f"🔍 Checking for completion criteria drift: {task_name}")
        
        # Load change history if available
        changes_file = self.workspace_path / "memory-bank" / "09-meta" / f"criteria_changes_{task_name}.json"
        changes = []
        if changes_file.exists():
            with open(changes_file, 'r') as f:
                changes = json.load(f)
                
        drift_detected = len(changes) > 0
        
        if drift_detected:
            print("⚠️ DRIFT DETECTED - Criteria have been modified:")
            for change in changes:
                print(f"  {change['timestamp']}: {change['type']} - {change['description']}")
        else:
            print("✅ No drift detected - Original criteria maintained")
            
        return {
            "drift_detected": drift_detected,
            "changes": changes,
            "original_criteria": criteria
        }
        
    def generate_report(self, task_name: str) -> str:
        """Generate comprehensive completion report."""
        criteria = self._load_criteria(task_name)
        if not criteria:
            return f"No criteria found for task: {task_name}"
            
        is_complete, results = self.check_completion_status(task_name)
        drift_info = self.check_drift(task_name)
        
        report = f"""
# Task Completion Report: {task_name}

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Completion Criteria
### MUST Conditions (Required)
{self._format_conditions_list(criteria['must_conditions'])}

### SHOULD Conditions (Quality Standards) 
{self._format_conditions_list(criteria['should_conditions'])}

### COULD Conditions (Nice to Have)
{self._format_conditions_list(criteria['could_conditions'])}

### Acceptance Tests
{self._format_conditions_list(criteria['acceptance_tests'])}

## Completion Status
Overall Status: **{'COMPLETE' if is_complete else 'INCOMPLETE'}**

### MUST Conditions Results
{self._format_results(results['must_results'])}

### SHOULD Conditions Results  
{self._format_results(results['should_results'])}

### COULD Conditions Results
{self._format_results(results['could_results'])}

### Acceptance Test Results
{self._format_results(results['acceptance_test_results'])}

### Quality Gate Results
{self._format_quality_results(results['quality_gate_results'])}

## Criteria Drift Analysis
{self._format_drift_analysis(drift_info)}

## Recommendations
{self._generate_recommendations(results, drift_info)}
"""
        
        # Save report
        report_file = self.workspace_path / "memory-bank" / "09-meta" / f"completion_report_{task_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_file, 'w') as f:
            f.write(report)
            
        print(f"📄 Report saved: {report_file}")
        return report
        
    def _check_condition(self, condition: str, level: str) -> bool:
        """Check if a specific condition is met."""
        # This is a simplified check - in practice, would implement
        # specific verification logic for different condition types
        
        condition_lower = condition.lower()
        
        # Security checks
        if "security" in condition_lower:
            return self._run_security_check()
            
        # Test checks
        if "test" in condition_lower:
            return self._run_tests()
            
        # Quality checks
        if "quality" in condition_lower or "clean code" in condition_lower:
            return self._run_quality_check()
            
        # Function/feature checks
        if "function" in condition_lower or "feature" in condition_lower:
            return self._check_functionality()
            
        # Default to manual verification prompt
        response = input(f"  Manual verification - Is this condition met? '{condition}' (y/N): ")
        return response.lower() in ['y', 'yes']
        
    def _run_acceptance_test(self, test: str) -> bool:
        """Run a specific acceptance test."""
        test_lower = test.lower()
        
        if "pytest" in test_lower or "unit test" in test_lower:
            return self._run_tests()
        elif "flake8" in test_lower or "lint" in test_lower:
            return self._run_quality_check()
        else:
            # Manual test verification
            response = input(f"  Manual test - Does this test pass? '{test}' (y/N): ")
            return response.lower() in ['y', 'yes']
            
    def _run_quality_gates(self) -> Dict:
        """Run all quality gate checks."""
        results = {}
        
        for tool_name, command in self.quality_tools.items():
            try:
                result = subprocess.run(
                    command, 
                    capture_output=True, 
                    text=True, 
                    cwd=self.workspace_path,
                    timeout=120
                )
                results[tool_name] = {
                    "passed": result.returncode == 0,
                    "output": result.stdout[:500],  # Truncate for brevity
                    "error": result.stderr[:500] if result.stderr else None
                }
                print(f"  {'✅' if result.returncode == 0 else '❌'} {tool_name}")
                
            except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
                results[tool_name] = {
                    "passed": False,
                    "output": None,
                    "error": str(e)
                }
                print(f"  ❌ {tool_name} (error: {str(e)[:100]})")
                
        results["overall_pass"] = all(r.get("passed", False) for r in results.values() if isinstance(r, dict))
        return results
        
    def _run_security_check(self) -> bool:
        """Run security verification."""
        try:
            result = subprocess.run(
                ["python", "scripts/security_check.py"], 
                capture_output=True, 
                cwd=self.workspace_path,
                timeout=60
            )
            return result.returncode == 0
        except:
            return False
            
    def _run_tests(self) -> bool:
        """Run test suite."""
        try:
            result = subprocess.run(
                ["pytest", "--tb=short"], 
                capture_output=True, 
                cwd=self.workspace_path,
                timeout=300
            )
            return result.returncode == 0
        except:
            return False
            
    def _run_quality_check(self) -> bool:
        """Run code quality checks."""
        try:
            flake8_result = subprocess.run(
                ["flake8", "app/", "tests/"], 
                capture_output=True, 
                cwd=self.workspace_path,
                timeout=60
            )
            return flake8_result.returncode == 0
        except:
            return False
            
    def _check_functionality(self) -> bool:
        """Check basic functionality."""
        # Simplified functionality check
        response = input("  Manual check - Is the main functionality working? (y/N): ")
        return response.lower() in ['y', 'yes']
        
    def _load_criteria(self, task_name: str) -> Optional[Dict]:
        """Load completion criteria for a task."""
        if not self.criteria_file.exists():
            return None
            
        try:
            with open(self.criteria_file, 'r') as f:
                content = f.read()
                
            # Simple JSON extraction (would be more robust in production)
            start_marker = f"<!-- CRITERIA_START_{task_name} -->"
            end_marker = f"<!-- CRITERIA_END_{task_name} -->"
            
            start_idx = content.find(start_marker)
            end_idx = content.find(end_marker)
            
            if start_idx == -1 or end_idx == -1:
                return None
                
            json_content = content[start_idx + len(start_marker):end_idx].strip()
            return json.loads(json_content)
            
        except (json.JSONDecodeError, IOError):
            return None
            
    def _save_criteria(self, criteria: Dict) -> None:
        """Save completion criteria to file."""
        self.criteria_file.parent.mkdir(parents=True, exist_ok=True)
        
        task_name = criteria["task_name"]
        
        # Create or update the tracker file
        if self.criteria_file.exists():
            with open(self.criteria_file, 'r') as f:
                content = f.read()
        else:
            content = "# Task Completion Criteria Tracker\n\n"
            
        # Remove existing criteria for this task
        start_marker = f"<!-- CRITERIA_START_{task_name} -->"
        end_marker = f"<!-- CRITERIA_END_{task_name} -->"
        
        start_idx = content.find(start_marker)
        end_idx = content.find(end_marker)
        
        if start_idx != -1 and end_idx != -1:
            content = content[:start_idx] + content[end_idx + len(end_marker):]
            
        # Add new criteria
        criteria_block = f"""
{start_marker}
{json.dumps(criteria, indent=2)}
{end_marker}

"""
        
        content += criteria_block
        
        with open(self.criteria_file, 'w') as f:
            f.write(content)
            
    def _display_criteria(self, criteria: Dict) -> None:
        """Display completion criteria in a readable format."""
        print(f"Task: {criteria['task_name']}")
        print(f"Defined: {criteria['defined_at']}")
        
        print(f"\nMUST Conditions ({len(criteria['must_conditions'])}):")
        for i, condition in enumerate(criteria['must_conditions'], 1):
            print(f"  {i}. {condition}")
            
        print(f"\nSHOULD Conditions ({len(criteria['should_conditions'])}):")
        for i, condition in enumerate(criteria['should_conditions'], 1):
            print(f"  {i}. {condition}")
            
        print(f"\nCOULD Conditions ({len(criteria['could_conditions'])}):")
        for i, condition in enumerate(criteria['could_conditions'], 1):
            print(f"  {i}. {condition}")
            
        print(f"\nAcceptance Tests ({len(criteria['acceptance_tests'])}):")
        for i, test in enumerate(criteria['acceptance_tests'], 1):
            print(f"  {i}. {test}")
            
    def _format_conditions_list(self, conditions: List[str]) -> str:
        """Format a list of conditions for the report."""
        if not conditions:
            return "- None defined"
        return "\n".join(f"- {condition}" for condition in conditions)
        
    def _format_results(self, results: List[Dict]) -> str:
        """Format test/condition results for the report."""
        if not results:
            return "- No results"
        return "\n".join(f"- {'✅' if r.get('status', False) else '❌'} {r.get('condition', r.get('test', 'Unknown'))}" for r in results)
        
    def _format_quality_results(self, results: Dict) -> str:
        """Format quality gate results."""
        if not results:
            return "- No quality checks run"
        
        formatted = []
        for tool, result in results.items():
            if tool == "overall_pass":
                continue
            if isinstance(result, dict):
                status = "✅" if result.get("passed", False) else "❌"
                formatted.append(f"- {status} {tool}")
                
        overall = "✅ PASS" if results.get("overall_pass", False) else "❌ FAIL"
        formatted.append(f"\n**Overall Quality Gates: {overall}**")
        
        return "\n".join(formatted)
        
    def _format_drift_analysis(self, drift_info: Dict) -> str:
        """Format drift analysis for the report."""
        if drift_info.get("drift_detected", False):
            changes = drift_info.get("changes", [])
            formatted = ["**DRIFT DETECTED** - Criteria have been modified:"]
            for change in changes:
                formatted.append(f"- {change.get('timestamp', 'Unknown')}: {change.get('type', 'Unknown')} - {change.get('description', 'No description')}")
            return "\n".join(formatted)
        else:
            return "**No drift detected** - Original criteria maintained"
            
    def _generate_recommendations(self, results: Dict, drift_info: Dict) -> str:
        """Generate recommendations based on results."""
        recommendations = []
        
        # Check for failing MUST conditions
        must_failures = [r for r in results.get("must_results", []) if not r.get("status", False)]
        if must_failures:
            recommendations.append("🚨 **CRITICAL**: Complete all MUST conditions before claiming task completion")
            
        # Check for low SHOULD completion
        should_failures = [r for r in results.get("should_results", []) if not r.get("status", False)]
        if len(should_failures) > len(results.get("should_results", [])) * 0.2:  # >20% failure
            recommendations.append("📋 **IMPORTANT**: Improve SHOULD condition completion for better quality")
            
        # Check for test failures
        test_failures = [r for r in results.get("acceptance_test_results", []) if not r.get("status", False)]
        if test_failures:
            recommendations.append("🧪 **TESTING**: Fix failing acceptance tests before completion")
            
        # Quality gate failures
        if not results.get("quality_gate_results", {}).get("overall_pass", False):
            recommendations.append("🔧 **QUALITY**: Address quality gate failures")
            
        # Drift warnings
        if drift_info.get("drift_detected", False):
            recommendations.append("⚠️ **DRIFT**: Review criteria changes for appropriateness")
            
        if not recommendations:
            recommendations.append("✅ **EXCELLENT**: All criteria met - task ready for completion!")
            
        return "\n".join(recommendations)


def main():
    """Main entry point for the task completion checker."""
    parser = argparse.ArgumentParser(description="Task Completion Integrity Checker")
    parser.add_argument("--task", required=True, help="Task name to check")
    parser.add_argument("--mode", choices=["check", "strict", "report", "define", "drift"], 
                       default="check", help="Checking mode")
    parser.add_argument("--define-criteria", action="store_true", 
                       help="Define completion criteria for the task")
    parser.add_argument("--check-drift", action="store_true",
                       help="Check for completion criteria drift")
    parser.add_argument("--workspace", default="/home/devuser/workspace",
                       help="Workspace path")
    
    args = parser.parse_args()
    
    checker = TaskCompletionChecker(args.workspace)
    
    if args.define_criteria or args.mode == "define":
        checker.define_completion_criteria(args.task)
    elif args.check_drift or args.mode == "drift":
        drift_info = checker.check_drift(args.task)
        print(json.dumps(drift_info, indent=2))
    elif args.mode == "report":
        report = checker.generate_report(args.task)
        print(report)
    else:
        strict_mode = args.mode == "strict"
        is_complete, results = checker.check_completion_status(args.task, strict_mode)
        
        # Exit with appropriate code
        sys.exit(0 if is_complete else 1)


if __name__ == "__main__":
    main()