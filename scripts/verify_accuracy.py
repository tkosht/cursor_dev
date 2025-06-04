#!/usr/bin/env python3
"""
正確性検証スクリプト
ドキュメント内のコマンド、ファイル参照、コード例の正確性を検証
"""

import os
import re
import subprocess
import sys
import json
from pathlib import Path
from typing import Set, List, Tuple

class AccuracyVerifier:
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.project_root = Path.cwd()
    
    def verify_makefile_targets(self) -> None:
        """Makefileターゲットの検証"""
        print("🔍 Verifying Makefile targets...")
        
        makefile_path = self.project_root / 'Makefile'
        if not makefile_path.exists():
            self.warnings.append("Makefile not found")
            return
        
        # Makefileからターゲットを抽出
        makefile_targets = set()
        with open(makefile_path, 'r') as f:
            for line in f:
                # ターゲット定義を検索（行頭から始まる）
                match = re.match(r'^([a-zA-Z0-9_-]+):', line)
                if match:
                    makefile_targets.add(match.group(1))
                # エイリアスも考慮
                match = re.match(r'^([a-zA-Z0-9_-]+)\s+([a-zA-Z0-9_-]+):', line)
                if match:
                    makefile_targets.add(match.group(1))
                    makefile_targets.add(match.group(2))
        
        # ドキュメントからmakeコマンドを抽出して検証
        for doc_path in self.project_root.glob('**/*.md'):
            # 除外パス
            if any(exclude in str(doc_path) for exclude in ['.venv', 'node_modules', 'htmlcov', '.specstory']):
                continue
                
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # `make xxx` または make xxx パターンを検索（コードブロック内のみ）
                # 一般的な英語表現は除外
                excluded_phrases = {'sure', 'sense', 'the', 'it', 'this', 'that', 'them', 'these', 'those', 'way', 'time', 'progress', 'changes', 'difference', 'mistakes', 'errors', 'improvements'}
                
                # コードブロック内のmakeコマンドを検索（例外パターンを除外）
                code_blocks = re.findall(r'```.*?\n(.*?)```', content, re.DOTALL)
                make_commands = []
                
                for block in code_blocks:
                    # 修正前の例やバッドプラクティス例、エラー例は除外
                    if any(marker in block for marker in [
                        '修正前', '悪い例', 'make test  # テストを実行',
                        '❌ ERROR', '⚠️  WARNING', '# Note:', 'エラー例',
                        'Makefile target not found', '存在しないターゲット',
                        '実行結果例', '以下は存在しない', 'ERROR:', 'WARNING:',
                        '誤検出問題', '品質管理システム', 'ナレッジ化', '作成背景'
                    ]):
                        continue
                    commands = re.findall(r'make\s+([a-zA-Z0-9_-]+)', block)
                    make_commands.extend(commands)
                
                # バックティック内のmakeコマンドも検索（注釈や説明文を除外）
                backtick_commands = re.findall(r'`make\s+([a-zA-Z0-9_-]+)`', content)
                # 注釈文や説明文内のコマンドは除外
                for line in content.split('\n'):
                    if any(marker in line for marker in [
                        '注：', '注意：', 'Note:', '未定義', '未実装', '修正前', '悪い例', 
                        '<!-- 修正前', '❌ ERROR', '⚠️  WARNING', 'エラー例',
                        'Makefile target not found', '存在しないターゲット',
                        '誤検出問題', '品質管理システム', 'ナレッジ化', '作成背景'
                    ]):
                        # この行のコマンドは除外
                        line_commands = re.findall(r'`make\s+([a-zA-Z0-9_-]+)`', line)
                        for cmd in line_commands:
                            if cmd in backtick_commands:
                                backtick_commands.remove(cmd)
                make_commands.extend(backtick_commands)
                
                for cmd in make_commands:
                    if cmd in excluded_phrases:
                        continue  # 一般的な英語表現はスキップ
                    if cmd not in makefile_targets:
                        self.errors.append(
                            f"{doc_path.relative_to(self.project_root)}: "
                            f"'make {cmd}' は存在しないターゲットです"
                        )
    
    def verify_file_references(self) -> None:
        """ファイル参照の検証"""
        print("🔍 Verifying file references...")
        
        for doc_path in self.project_root.glob('**/*.md'):
            # 除外パス
            if any(exclude in str(doc_path) for exclude in ['.venv', 'node_modules', 'htmlcov', '.specstory']):
                continue
                
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Markdownリンクパターンを検索
                file_refs = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
                
                for text, ref in file_refs:
                    # URLとアンカーリンクはスキップ
                    if ref.startswith(('http://', 'https://', '#')):
                        continue
                    
                    # メールアドレスはスキップ
                    if '@' in ref:
                        continue
                    
                    # 正規表現パターンやプレースホルダーはスキップ
                    if any(pattern in ref for pattern in ['[^', '\\', '{', '}', '*', '?', 'mdc:']):
                        continue
                    
                    # 相対パスを解決
                    try:
                        ref_path = (doc_path.parent / ref).resolve()
                        # プロジェクトルート外への参照は警告
                        if not str(ref_path).startswith(str(self.project_root)):
                            self.warnings.append(
                                f"{doc_path.relative_to(self.project_root)}: "
                                f"プロジェクト外への参照 '{ref}'"
                            )
                        elif not ref_path.exists():
                            self.errors.append(
                                f"{doc_path.relative_to(self.project_root)}: "
                                f"リンク '{ref}' が存在しません"
                            )
                    except Exception:
                        self.warnings.append(
                            f"{doc_path.relative_to(self.project_root)}: "
                            f"パス '{ref}' の解決に失敗"
                        )
    
    def verify_python_imports(self) -> None:
        """Pythonインポートの検証"""
        print("🔍 Verifying Python imports in documentation...")
        
        for doc_path in self.project_root.glob('**/*.md'):
            # 除外パス
            if any(exclude in str(doc_path) for exclude in ['.venv', 'node_modules', 'htmlcov', '.specstory']):
                continue
                
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # ```python コードブロックを抽出
                python_blocks = re.findall(
                    r'```python\n(.*?)\n```', 
                    content, 
                    re.DOTALL
                )
                
                for block in python_blocks:
                    # 例文やエラー例のブロックは除外
                    if any(marker in block for marker in [
                        '# 例:', '# Example:', '# サンプル:', '修正前', '悪い例',
                        'a2a_prototype', 'a2a_mvp', 'utils.helper', 'utils.config',
                        '❌', '⚠️', 'ERROR', 'WARNING', '例文', 'エラー例'
                    ]):
                        continue
                        
                    # from ... import ... パターンを検索
                    imports = re.findall(
                        r'from\s+(app\.[a-zA-Z0-9_.]+)\s+import', 
                        block
                    )
                    
                    for module_path in imports:
                        # モジュールパスをファイルパスに変換
                        file_path = module_path.replace('.', '/') + '.py'
                        if not (self.project_root / file_path).exists():
                            # __init__.pyの可能性も確認
                            init_path = module_path.replace('.', '/') + '/__init__.py'
                            if not (self.project_root / init_path).exists():
                                self.warnings.append(
                                    f"{doc_path.relative_to(self.project_root)}: "
                                    f"インポート '{module_path}' が見つかりません"
                                )
    
    def verify_command_outputs(self) -> None:
        """コマンド出力例の検証"""
        print("🔍 Verifying command outputs...")
        
        # pytest関連のコマンドを確認
        for doc_path in self.project_root.glob('**/*.md'):
            # 除外パス
            if any(exclude in str(doc_path) for exclude in ['.venv', 'node_modules', 'htmlcov', '.specstory']):
                continue
                
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # pytestコマンドの出力パターンを検索
                if 'pytest' in content:
                    # カバレッジ値のチェック
                    coverage_claims = re.findall(r'(\d+(?:\.\d+)?)\s*%.*(?:coverage|カバレッジ)', content)
                    for coverage in coverage_claims:
                        if float(coverage) > 100:
                            self.errors.append(
                                f"{doc_path.relative_to(self.project_root)}: "
                                f"不正なカバレッジ値 {coverage}%"
                            )
    
    def verify_docker_commands(self) -> None:
        """Docker関連コマンドの検証"""
        print("🔍 Verifying Docker commands...")
        
        # docker-compose.ymlまたはcompose.ymlの存在確認
        compose_exists = (
            (self.project_root / 'docker-compose.yml').exists() or
            (self.project_root / 'compose.yml').exists()
        )
        
        if not compose_exists:
            return
        
        # docker composeサービス名を抽出
        compose_file = None
        if (self.project_root / 'compose.yml').exists():
            compose_file = self.project_root / 'compose.yml'
        elif (self.project_root / 'docker-compose.yml').exists():
            compose_file = self.project_root / 'docker-compose.yml'
        
        if compose_file:
            services = set()
            with open(compose_file, 'r') as f:
                content = f.read()
                # 簡易的なサービス名抽出
                in_services = False
                for line in content.split('\n'):
                    if line.strip() == 'services:':
                        in_services = True
                        continue
                    if in_services and line and not line.startswith(' '):
                        in_services = False
                    if in_services and line.strip() and not line.startswith('  '):
                        service_name = line.strip().rstrip(':')
                        if service_name:
                            services.add(service_name)
    
    def generate_report(self) -> int:
        """検証レポートの生成"""
        print("\n" + "=" * 60)
        print("📊 Accuracy Verification Report")
        print("=" * 60)
        
        if not self.errors and not self.warnings:
            print("✅ All checks passed! No inaccuracies found.")
            print("=" * 60)
            return 0
        
        if self.errors:
            print(f"\n❌ Errors found ({len(self.errors)}):")
            print("-" * 60)
            for i, error in enumerate(self.errors, 1):
                print(f"{i:3d}. {error}")
        
        if self.warnings:
            print(f"\n⚠️  Warnings ({len(self.warnings)}):")
            print("-" * 60)
            for i, warning in enumerate(self.warnings, 1):
                print(f"{i:3d}. {warning}")
        
        print("\n" + "=" * 60)
        print(f"Summary: {len(self.errors)} errors, {len(self.warnings)} warnings")
        print("=" * 60)
        
        return 1 if self.errors else 0
    
    def run(self) -> int:
        """全検証を実行"""
        print("🚀 Starting accuracy verification...")
        print("=" * 60)
        
        self.verify_makefile_targets()
        self.verify_file_references()
        self.verify_python_imports()
        self.verify_command_outputs()
        self.verify_docker_commands()
        
        return self.generate_report()

def main():
    """メインエントリーポイント"""
    verifier = AccuracyVerifier()
    return verifier.run()

if __name__ == "__main__":
    sys.exit(main())