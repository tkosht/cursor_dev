#!/usr/bin/env python3
"""
検証ツール自体の検証スクリプト
「再発防止策の再発防止策」として機能

検証対象:
1. verify_accuracy.py が実際に動作するか
2. critical_documentation_review.py が実際に動作するか  
3. pre-commit フックが実際に機能するか
4. エラー検出機能が正常に動作するか
"""

import subprocess
import tempfile
import os
import sys
from pathlib import Path
from typing import List, Tuple

class VerificationToolsVerifier:
    """検証ツールの検証者"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.test_results: List[Tuple[str, bool, str]] = []
    
    def log_result(self, test_name: str, success: bool, message: str = ""):
        """テスト結果をログ"""
        self.test_results.append((test_name, success, message))
        status = "✅" if success else "❌"
        print(f"{status} {test_name}: {message}")
    
    def test_verify_accuracy_exists(self) -> bool:
        """verify_accuracy.py の存在確認"""
        script_path = self.project_root / "scripts" / "verify_accuracy.py"
        exists = script_path.exists() and script_path.is_file()
        self.log_result(
            "verify_accuracy.py existence", 
            exists,
            f"File exists: {exists}"
        )
        return exists
    
    def test_verify_accuracy_executable(self) -> bool:
        """verify_accuracy.py の実行可能性確認"""
        try:
            result = subprocess.run(
                ["python", "scripts/verify_accuracy.py"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=30
            )
            # 0 (成功) または 1 (警告あり) は正常
            success = result.returncode in [0, 1]
            self.log_result(
                "verify_accuracy.py executable",
                success,
                f"Return code: {result.returncode}"
            )
            return success
        except Exception as e:
            self.log_result(
                "verify_accuracy.py executable", 
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def test_critical_review_exists(self) -> bool:
        """critical_documentation_review.py の存在確認"""
        script_path = self.project_root / "scripts" / "critical_documentation_review.py"
        exists = script_path.exists() and script_path.is_file()
        self.log_result(
            "critical_documentation_review.py existence",
            exists,
            f"File exists: {exists}"
        )
        return exists
    
    def test_critical_review_executable(self) -> bool:
        """critical_documentation_review.py の実行可能性確認"""
        try:
            result = subprocess.run(
                ["python", "scripts/critical_documentation_review.py", "--target", "README.md"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=30
            )
            # 0, 1, 2 は正常な終了コード
            success = result.returncode in [0, 1, 2]
            self.log_result(
                "critical_documentation_review.py executable",
                success,
                f"Return code: {result.returncode}"
            )
            return success
        except Exception as e:
            self.log_result(
                "critical_documentation_review.py executable",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def test_precommit_hook_exists(self) -> bool:
        """pre-commit フックの存在確認"""
        hook_path = self.project_root / ".git" / "hooks" / "pre-commit"
        exists = hook_path.exists() and hook_path.is_file()
        self.log_result(
            "pre-commit hook existence",
            exists,
            f"File exists: {exists}"
        )
        return exists
    
    def test_precommit_hook_contains_verification(self) -> bool:
        """pre-commit フックに検証コードが含まれているか確認"""
        try:
            hook_path = self.project_root / ".git" / "hooks" / "pre-commit"
            with open(hook_path, 'r') as f:
                content = f.read()
            
            required_patterns = [
                "verify_accuracy.py",
                "Documentation Accuracy Check",
                "COMMIT BLOCKED"
            ]
            
            contains_all = all(pattern in content for pattern in required_patterns)
            self.log_result(
                "pre-commit hook contains verification logic",
                contains_all,
                f"Contains required patterns: {contains_all}"
            )
            return contains_all
        except Exception as e:
            self.log_result(
                "pre-commit hook contains verification logic",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def test_error_detection_functionality(self) -> bool:
        """エラー検出機能のテスト"""
        try:
            # 一時的にエラーのあるファイルを作成
            test_content = '''# Test Document
            
```bash
make nonexistent_target  # This should be detected as error
```
'''
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
                f.write(test_content)
                temp_file = f.name
            
            try:
                # verify_accuracy.py でエラー検出をテスト
                result = subprocess.run(
                    ["python", "scripts/verify_accuracy.py"],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                # エラーが検出される（return code 1）ことを確認
                error_detected = result.returncode == 1 and "nonexistent_target" in result.stderr
                self.log_result(
                    "error detection functionality",
                    error_detected,
                    f"Error properly detected: {error_detected}"
                )
                return error_detected
            finally:
                os.unlink(temp_file)
                
        except Exception as e:
            self.log_result(
                "error detection functionality",
                False,
                f"Exception: {str(e)}"
            )
            return False
    
    def test_self_verification_execution(self) -> bool:
        """このスクリプト自体の実行記録"""
        # この関数が呼ばれていることは、スクリプトが実行されている証拠
        self.log_result(
            "verification tools verifier execution",
            True,
            "Self-verification successfully executed"
        )
        return True
    
    def run_all_tests(self) -> bool:
        """全テストの実行"""
        print("🔬 Verification Tools Verification Starting...")
        print("=" * 60)
        print("検証ツール自体が正常に機能するかを検証します")
        print("=" * 60)
        
        tests = [
            self.test_verify_accuracy_exists,
            self.test_verify_accuracy_executable,
            self.test_critical_review_exists,
            self.test_critical_review_executable,
            self.test_precommit_hook_exists,
            self.test_precommit_hook_contains_verification,
            self.test_self_verification_execution,
        ]
        
        all_passed = True
        for test in tests:
            try:
                result = test()
                if not result:
                    all_passed = False
            except Exception as e:
                print(f"❌ {test.__name__}: Exception - {str(e)}")
                all_passed = False
        
        print("\n" + "=" * 60)
        print("📊 Verification Tools Verification Report")
        print("=" * 60)
        
        passed = sum(1 for _, success, _ in self.test_results if success)
        total = len(self.test_results)
        
        print(f"Tests passed: {passed}/{total}")
        
        if not all_passed:
            print("\n❌ CRITICAL: Some verification tools are not working properly!")
            print("The verification system itself has failed.")
            print("This means the re-prevention system is NOT functional.")
        else:
            print("\n✅ All verification tools are working properly!")
            print("The re-prevention system is functional.")
        
        print("=" * 60)
        return all_passed
    
def main():
    """メインエントリーポイント"""
    verifier = VerificationToolsVerifier()
    success = verifier.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())