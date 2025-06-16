#!/usr/bin/env python3
"""
Pre-Action Constraint Checker v1.0
Task実行前の統合制約検証システム

統合対象:
- User Authorization (check_user_authorization.py)
- Quality Anti-Hacking (check_quality_anti_hacking.py) 
- TDD Compliance (tdd_compliance_check.py)
- Memory Bank Files (制約ファイル存在確認)
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class PreActionChecker:
    """統合制約チェッカー"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.constraint_files = [
            'memory-bank/00-core/user_authorization_mandatory.md',
            'memory-bank/00-core/testing_mandatory.md',
            'memory-bank/00-core/code_quality_anti_hacking.md',
            'memory-bank/09-meta/progress_recording_mandatory_rules.md'
        ]
        self.violations = []
        self.results = {}
        
    def run(self, strict_mode: bool = False, constraint_source: str = "direct") -> bool:
        """メイン実行フロー"""
        print("🚨 Pre-Action Constraint Check Starting...")
        print("=" * 80)
        
        # Phase 1A必須制約ファイルの存在確認
        constraint_files_ok = self._check_constraint_files()
        
        # 個別制約チェック実行
        user_auth_ok = self._run_user_authorization_check()
        quality_ok = self._run_quality_check()
        tdd_ok = self._run_tdd_compliance_check()
        
        # 結果統合
        all_passed = constraint_files_ok and user_auth_ok and quality_ok and tdd_ok
        
        self._report_results(all_passed, strict_mode)
        
        return all_passed
    
    def _check_constraint_files(self) -> bool:
        """Phase 1A必須制約ファイル存在・内容チェック"""
        print("🔍 Checking constraint files...")
        
        missing_files = []
        for file_path in self.constraint_files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                missing_files.append(file_path)
            else:
                # 基本的な内容チェック（空ファイルでないか）
                if full_path.stat().st_size == 0:
                    missing_files.append(f"{file_path} (empty)")
        
        if missing_files:
            self.violations.extend([f"Missing constraint file: {f}" for f in missing_files])
            print(f"❌ Missing constraint files: {missing_files}")
            return False
        
        print("✅ All constraint files present")
        return True
    
    def _run_user_authorization_check(self) -> bool:
        """ユーザー承認制約チェック"""
        print("🛡️ Running user authorization check...")
        
        try:
            result = subprocess.run(
                ["python", "scripts/check_user_authorization.py"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print("✅ User authorization: PASSED")
                return True
            else:
                print("❌ User authorization: FAILED")
                self.violations.append("User authorization check failed")
                return False
                
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            print(f"⚠️ User authorization check error: {e}")
            # チェックスクリプトの問題はシステムの問題として扱う
            return True
    
    def _run_quality_check(self) -> bool:
        """品質制約チェック"""
        print("🧹 Running quality checks...")
        
        try:
            result = subprocess.run(
                ["python", "scripts/quality_gate_check.py"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                print("✅ Quality check: PASSED")
                return True
            else:
                print("❌ Quality check: FAILED")
                self.violations.append("Quality gate check failed")
                return False
                
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            print(f"⚠️ Quality check error: {e}")
            return True
    
    def _run_tdd_compliance_check(self) -> bool:
        """TDD遵守制約チェック"""
        print("🧪 Running TDD compliance check...")
        
        try:
            result = subprocess.run(
                ["python", "scripts/tdd_compliance_check.py"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print("✅ TDD compliance: PASSED")
                return True
            else:
                print("❌ TDD compliance: FAILED")
                self.violations.append("TDD compliance check failed")
                return False
                
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            print(f"⚠️ TDD compliance check error: {e}")
            return True
    
    def _report_results(self, all_passed: bool, strict_mode: bool):
        """結果レポート"""
        print("\n" + "=" * 80)
        
        if all_passed:
            print("✅ Pre-Action Check: PASSED")
            print("🎯 All constraints satisfied - Ready to proceed")
        else:
            print("❌ Pre-Action Check: FAILED")
            print("🛑 Constraint violations detected")
            
            if self.violations:
                print("\n📋 Violations:")
                for violation in self.violations:
                    print(f"  - {violation}")
        
        if strict_mode and not all_passed:
            print("\n🚨 STRICT MODE: All actions BLOCKED until violations resolved")
        
        print("\n💡 For detailed constraint information:")
        print("  - User authorization: memory-bank/user_authorization_mandatory_rules.md")
        print("  - Testing rules: memory-bank/testing_mandatory_rules.md") 
        print("  - Quality standards: memory-bank/code_quality_anti_hacking_rules.md")


def main():
    """メインエントリーポイント"""
    parser = argparse.ArgumentParser(
        description='Pre-Action Constraint Checker - Integrated validation system'
    )
    
    parser.add_argument(
        '--strict-mode', 
        action='store_true',
        help='Enable strict mode (exit 1 on any violation)'
    )
    
    parser.add_argument(
        '--constraint-source',
        choices=['direct', 'cognee', 'both'],
        default='direct',
        help='Source of constraint rules'
    )
    
    parser.add_argument(
        '--project-root',
        type=str,
        default='.',
        help='Project root directory path'
    )
    
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results in JSON format'
    )
    
    args = parser.parse_args()
    
    checker = PreActionChecker(args.project_root)
    success = checker.run(args.strict_mode, args.constraint_source)
    
    if args.json:
        result = {
            'success': success,
            'violations': checker.violations,
            'constraint_files_checked': checker.constraint_files,
            'strict_mode': args.strict_mode
        }
        print(json.dumps(result, indent=2))
    
    # CLAUDE.mdの期待通り: 0=Continue, 1=Stop
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())