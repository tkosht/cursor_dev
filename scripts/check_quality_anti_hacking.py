#!/usr/bin/env python3
"""
品質アンチハッキング・チェッカー

noqaの使用量監視と品質指標回避の検出を行います。
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple, Dict


class QualityAntiHackingChecker:
    """品質アンチハッキングの検出と監視"""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.violations = []
        
        # 除外対象ディレクトリ
        self.exclude_dirs = {
            '.git', '.venv', '__pycache__', 'node_modules', 
            '.pytest_cache', 'htmlcov', '.coverage', 'dev-tools'
        }
        
        # 監視対象パターン（実際のnoqaディレクティブのみ）
        self.noqa_pattern = re.compile(r'#\s*noqa(?::\s*([A-Z]\d+(?:,\s*[A-Z]\d+)*))?\s*$')
        self.pragma_pattern = re.compile(r'#\s*pragma:\s*no\s+cover')
        
    def scan_python_files(self) -> List[Path]:
        """Pythonファイルをスキャン"""
        python_files = []
        
        for path in self.project_root.rglob("*.py"):
            # 除外ディレクトリのチェック
            if any(part in self.exclude_dirs for part in path.parts):
                continue
            python_files.append(path)
            
        return python_files
    
    def check_noqa_usage(self) -> Dict[str, List[Tuple[int, str]]]:
        """noqa使用量の監視"""
        noqa_usage = {}
        
        for file_path in self.scan_python_files():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                file_violations = []
                for line_num, line in enumerate(lines, 1):
                    match = self.noqa_pattern.search(line)
                    if match:
                        # 正当性の簡易チェック
                        if not self._is_justified_noqa(line, file_path, line_num):
                            file_violations.append((line_num, line.strip()))
                
                if file_violations:
                    noqa_usage[str(file_path)] = file_violations
                    
            except (UnicodeDecodeError, IOError) as e:
                print(f"Warning: Could not read {file_path}: {e}")
        
        return noqa_usage
    
    def check_pragma_usage(self) -> Dict[str, List[Tuple[int, str]]]:
        """pragma: no cover使用量の監視"""
        pragma_usage = {}
        
        for file_path in self.scan_python_files():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                file_violations = []
                for line_num, line in enumerate(lines, 1):
                    if self.pragma_pattern.search(line):
                        # 正当性の簡易チェック
                        if not self._is_justified_pragma(line, file_path, line_num):
                            file_violations.append((line_num, line.strip()))
                
                if file_violations:
                    pragma_usage[str(file_path)] = file_violations
                    
            except (UnicodeDecodeError, IOError) as e:
                print(f"Warning: Could not read {file_path}: {e}")
        
        return pragma_usage
    
    def _is_justified_noqa(self, line: str, file_path: Path, line_num: int) -> bool:
        """noqa使用の正当性をチェック"""
        # TODO承認、期限設定、理由記載をチェック
        context_lines = self._get_context_lines(file_path, line_num, 3)
        
        justification_indicators = [
            'TODO:', 'FIXME:', '承認済み', 'アーキテクト承認',
            '一時的回避', 'レガシー', '技術的制約'
        ]
        
        for context_line in context_lines:
            if any(indicator in context_line for indicator in justification_indicators):
                return True
        
        return False
    
    def _is_justified_pragma(self, line: str, file_path: Path, line_num: int) -> bool:
        """pragma使用の正当性をチェック"""
        # 単体テストでのモック、デバッグコード等は除外
        if 'test_' in file_path.name or '/tests/' in str(file_path):
            return True
            
        context_lines = self._get_context_lines(file_path, line_num, 2)
        
        # デバッグ用、初期化コード等の正当なケース
        justified_patterns = [
            'if __name__ == "__main__"',
            'debug', 'Debug', 'DEBUG',
            'main()', 'cli()', 'run()'
        ]
        
        for context_line in context_lines:
            if any(pattern in context_line for pattern in justified_patterns):
                return True
        
        return False
    
    def _get_context_lines(self, file_path: Path, line_num: int, context: int) -> List[str]:
        """指定行の前後コンテキストを取得"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            start = max(0, line_num - context - 1)
            end = min(len(lines), line_num + context)
            
            return [line.strip() for line in lines[start:end]]
        except (UnicodeDecodeError, IOError):
            return []
    
    def generate_report(self) -> None:
        """監視レポートの生成"""
        print("🔍 品質アンチハッキング・チェック結果")
        print("=" * 60)
        
        # noqa使用量のチェック
        noqa_violations = self.check_noqa_usage()
        print(f"\n📊 noqa使用状況:")
        
        if not noqa_violations:
            print("✅ 不適切なnoqa使用は検出されませんでした")
        else:
            print(f"⚠️  {len(noqa_violations)}個のファイルで疑わしいnoqa使用を検出:")
            for file_path, violations in noqa_violations.items():
                print(f"\n📄 {file_path}:")
                for line_num, line in violations:
                    print(f"   L{line_num}: {line}")
        
        # pragma使用量チェック
        pragma_violations = self.check_pragma_usage()
        print(f"\n📊 pragma: no cover使用状況:")
        
        if not pragma_violations:
            print("✅ 不適切なpragma使用は検出されませんでした")
        else:
            print(f"⚠️  {len(pragma_violations)}個のファイルで疑わしいpragma使用を検出:")
            for file_path, violations in pragma_violations.items():
                print(f"\n📄 {file_path}:")
                for line_num, line in violations:
                    print(f"   L{line_num}: {line}")
        
        # 総合判定
        total_violations = len(noqa_violations) + len(pragma_violations)
        if total_violations == 0:
            print("\n✅ 品質アンチハッキング・チェック: 合格")
            return 0
        else:
            print(f"\n❌ 品質アンチハッキング・チェック: {total_violations}件の問題を検出")
            print("\n📋 推奨アクション:")
            print("1. 各noqa/pragmaの正当性を確認")
            print("2. 不適切な使用は根本解決を実施")
            print("3. 必要な場合はアーキテクト承認を取得")
            print("4. 一時的な例外には期限と計画を設定")
            return 1


def main():
    """メイン処理"""
    checker = QualityAntiHackingChecker()
    exit_code = checker.generate_report()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()