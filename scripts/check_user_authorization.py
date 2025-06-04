#!/usr/bin/env python3
"""
ユーザー承認チェックスクリプト
無許可での構造変更・根拠なき主張を防止
"""

import os
import re
import subprocess
import sys
from pathlib import Path
from typing import List, Set

class UserAuthorizationChecker:
    """ユーザー承認必須チェッカー"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.violations: List[str] = []
        
    def check_project_structure_compliance(self) -> bool:
        """プロジェクト構造の準拠性チェック"""
        print("🔍 Checking project structure compliance...")
        
        # README.mdからプロジェクト構造を抽出
        readme_path = self.project_root / "README.md"
        if not readme_path.exists():
            self.violations.append("README.md not found")
            return False
            
        defined_structure = self._extract_defined_structure(readme_path)
        actual_structure = self._get_actual_structure()
        
        # 未定義ディレクトリの検出
        undefined_dirs = actual_structure - defined_structure
        if undefined_dirs:
            for directory in undefined_dirs:
                self.violations.append(
                    f"未定義ディレクトリが存在: {directory} "
                    f"(README.mdのプロジェクト構造に記載なし)"
                )
            return False
            
        return True
    
    def _extract_defined_structure(self, readme_path: Path) -> Set[str]:
        """README.mdから定義されたディレクトリ構造を抽出"""
        defined_dirs = set()
        
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # プロジェクト構造セクションを検索
        structure_match = re.search(
            r'## 📁 プロジェクト構造.*?```(.*?)```', 
            content, 
            re.DOTALL
        )
        
        if structure_match:
            structure_text = structure_match.group(1)
            # ディレクトリ名を抽出（app/, tests/ 等）
            dir_patterns = re.findall(r'^([a-zA-Z0-9_-]+)/', structure_text, re.MULTILINE)
            defined_dirs.update(dir_patterns)
            
        return defined_dirs
    
    def _get_actual_structure(self) -> Set[str]:
        """実際のディレクトリ構造を取得"""
        actual_dirs = set()
        
        # 除外ディレクトリ
        exclude_dirs = {
            '.git', '.venv', '__pycache__', 'node_modules', 
            'htmlcov', '.pytest_cache', '.mypy_cache',
            '.specstory', 'bin'  # binは例外として許可
        }
        
        for item in self.project_root.iterdir():
            if (item.is_dir() and 
                not item.name.startswith('.') and 
                item.name not in exclude_dirs):
                actual_dirs.add(item.name)
                
        return actual_dirs
    
    def check_evidence_based_claims(self) -> bool:
        """根拠に基づく主張のチェック（ドキュメント内）"""
        print("🔍 Checking evidence-based claims...")
        
        # 危険な主観的表現パターン（技術仕様の例外を考慮）
        subjective_patterns = [
            r'広く(?:使われて|受け入れられて|採用されて)',
            r'一般的(?:に|な)(?!.*(?:形式|フォーマット|仕様|API|プロトコル))',
            r'多くの(?:プロジェクト|開発者)',
            r'標準的(?:に|な)(?!.*(?:JSON|XML|HTTP|REST|API|形式|仕様|プロトコル))',
            r'よく(?:使われ|知られ)',
            r'(?:業界|コミュニティ)(?:で|の)(?:標準|慣習)',
        ]
        
        violations_found = False
        
        for doc_path in self.project_root.glob('**/*.md'):
            if any(exclude in str(doc_path) for exclude in ['.git', '.venv', 'node_modules']):
                continue
                
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
            for line_num, line in enumerate(lines, 1):
                for pattern in subjective_patterns:
                    if re.search(pattern, line):
                        # 根拠が同じ段落にあるかチェック
                        context_start = max(0, line_num - 3)
                        context_end = min(len(lines), line_num + 3)
                        context = '\n'.join(lines[context_start:context_end])
                        
                        # 根拠キーワードの存在確認
                        evidence_keywords = [
                            r'\d+%', r'\d+パーセント', 
                            r'データ', r'統計', r'調査', r'研究',
                            r'測定', r'実測', r'検証',
                            r'ソース:', r'出典:', r'参考:'
                        ]
                        
                        has_evidence = any(
                            re.search(keyword, context, re.IGNORECASE) 
                            for keyword in evidence_keywords
                        )
                        
                        if not has_evidence:
                            self.violations.append(
                                f"{doc_path.relative_to(self.project_root)}:{line_num} "
                                f"根拠なき主観的主張: '{line.strip()[:50]}...'"
                            )
                            violations_found = True
                            
        return not violations_found
    
    def check_unauthorized_changes(self) -> bool:
        """無許可変更のチェック（Git履歴ベース）"""
        print("🔍 Checking unauthorized changes...")
        
        try:
            # ステージングされたファイルで新規ディレクトリ作成をチェック
            result = subprocess.run(
                ['git', 'diff', '--cached', '--name-only', '--diff-filter=A'],
                capture_output=True, text=True, cwd=self.project_root
            )
            
            if result.returncode == 0:
                new_files = result.stdout.strip().split('\n') if result.stdout.strip() else []
                new_dirs = set()
                
                for file_path in new_files:
                    if '/' in file_path:
                        top_dir = file_path.split('/')[0]
                        new_dirs.add(top_dir)
                
                # 新規ディレクトリが定義済み構造に含まれているかチェック
                readme_path = self.project_root / "README.md"
                if readme_path.exists():
                    defined_structure = self._extract_defined_structure(readme_path)
                    
                    unauthorized_dirs = new_dirs - defined_structure
                    if unauthorized_dirs:
                        for directory in unauthorized_dirs:
                            self.violations.append(
                                f"無許可新規ディレクトリ: {directory} "
                                f"(ユーザー許可が必要)"
                            )
                        return False
                        
        except Exception:
            # Git環境でない場合はスキップ
            pass
            
        return True
    
    def generate_violation_report(self) -> None:
        """違反レポートの生成"""
        if not self.violations:
            print("✅ All user authorization checks passed!")
            return
            
        print("\n" + "=" * 80)
        print("🚨 USER AUTHORIZATION VIOLATIONS DETECTED")
        print("=" * 80)
        print("以下の違反が検出されました:")
        print()
        
        for i, violation in enumerate(self.violations, 1):
            print(f"{i:3d}. {violation}")
            
        print("\n" + "=" * 80)
        print("⚠️  これらの違反は以下の原則に反しています:")
        print("1. ユーザー明示的許可なしでの構造変更禁止")
        print("2. 根拠なき主観的主張禁止") 
        print("3. 事前確認プロセスの必須実行")
        print()
        print("💡 対処方法:")
        print("1. ユーザーに許可を申請する")
        print("2. 客観的根拠を提示する")
        print("3. 適切な代替案を提案する")
        print("=" * 80)
    
    def run(self) -> int:
        """全チェックの実行"""
        print("🚨 User Authorization Compliance Check Starting...")
        print("=" * 80)
        
        checks = [
            self.check_project_structure_compliance,
            self.check_evidence_based_claims,
            self.check_unauthorized_changes,
        ]
        
        all_passed = True
        for check in checks:
            try:
                if not check():
                    all_passed = False
            except Exception as e:
                self.violations.append(f"Check error: {str(e)}")
                all_passed = False
                
        self.generate_violation_report()
        return 0 if all_passed else 1

def main():
    """メインエントリーポイント"""
    checker = UserAuthorizationChecker()
    return checker.run()

if __name__ == "__main__":
    sys.exit(main())