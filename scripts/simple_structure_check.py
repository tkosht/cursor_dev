#!/usr/bin/env python3
"""
シンプル構造チェックスクリプト
新規ディレクトリ作成のみをチェック（根拠チェックは削除）
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Set


class SimpleStructureChecker:
    """シンプル構造チェッカー（構造変更のみ）"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.violations = []
        
    def check_new_directories(self) -> bool:
        """新規ディレクトリ作成のチェックのみ"""
        print("🔍 Checking for new directory creation...")
        
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
                
                # 既知の許可ディレクトリ（現在のプロジェクト構造に基づく）
                allowed_dirs = {
                    'app', 'tests', 'docs', 'scripts', 'memory-bank', 
                    'knowledge', 'templates', 'docker', 'bin', 'node_modules',
                    'htmlcov', '.git', '.venv', '__pycache__', '.pytest_cache',
                    '.mypy_cache', '.specstory'  # 自動生成ディレクトリも許可
                }
                
                unauthorized_dirs = new_dirs - allowed_dirs
                if unauthorized_dirs:
                    for directory in unauthorized_dirs:
                        self.violations.append(
                            f"新規ディレクトリ作成: {directory} "
                            f"(事前にユーザー許可が必要)"
                        )
                    return False
                        
        except Exception as e:
            print(f"Warning: {e}")
            
        return True
    
    def generate_report(self) -> None:
        """シンプルなレポート生成"""
        if not self.violations:
            print("✅ 構造チェック完了: 問題なし")
            return
            
        print("\n" + "=" * 60)
        print("🚨 新規ディレクトリが検出されました")
        print("=" * 60)
        
        for i, violation in enumerate(self.violations, 1):
            print(f"{i}. {violation}")
            
        print("\n💡 対処方法:")
        print("1. ユーザーに許可を申請する")
        print("2. 既存ディレクトリ内に配置する")
        print("3. 一時的スキップ: git commit --no-verify")
        print("=" * 60)
    
    def run(self) -> int:
        """チェック実行"""
        # 環境変数による制御
        if os.getenv('SKIP_STRUCTURE_CHECK') == '1':
            print("🔧 SKIP_STRUCTURE_CHECK=1: Structure check skipped")
            return 0
            
        print("🔍 シンプル構造チェック開始...")
        
        success = self.check_new_directories()
        self.generate_report()
        
        return 0 if success else 1


def main():
    """メインエントリーポイント"""
    checker = SimpleStructureChecker()
    return checker.run()


if __name__ == "__main__":
    sys.exit(main())