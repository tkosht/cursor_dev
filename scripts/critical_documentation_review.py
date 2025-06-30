#!/usr/bin/env python3
"""
批判的ドキュメントレビュースクリプト
ゼロベースでの客観的・批判的レビューを自動化

使用方法:
  python scripts/critical_documentation_review.py --target README.md
  python scripts/critical_documentation_review.py --all
"""

import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import List, Dict, Set, Tuple
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ReviewFinding:
    """レビュー発見事項"""
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    category: str  # ACCURACY, CLARITY, COMPLETENESS, CONSISTENCY
    file_path: str
    line_number: int
    description: str
    suggestion: str
    evidence: str = ""

class CriticalDocumentationReviewer:
    """批判的ドキュメントレビューア"""
    
    def __init__(self):
        self.findings: List[ReviewFinding] = []
        self.project_root = Path.cwd()
        self.verified_commands: Set[str] = set()
        self.verified_files: Set[str] = set()
    
    def review_document(self, doc_path: Path) -> None:
        """ドキュメントの批判的レビュー実行"""
        print(f"🔍 批判的レビュー中: {doc_path.relative_to(self.project_root)}")
        
        with open(doc_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
        
        # 各種レビューを実行
        self._review_command_accuracy(doc_path, content, lines)
        self._review_claims_verification(doc_path, content, lines)
        self._review_clarity_consistency(doc_path, content, lines)
        self._review_completeness(doc_path, content, lines)
        self._review_maintainability(doc_path, content, lines)
    
    def _review_command_accuracy(self, doc_path: Path, content: str, lines: List[str]) -> None:
        """コマンド正確性のレビュー"""
        
        # コードブロック内のコマンドを抽出
        code_blocks = re.findall(r'```(?:bash|shell)?\n(.*?)\n```', content, re.DOTALL)
        
        for block_idx, block in enumerate(code_blocks):
            block_lines = block.split('\n')
            for line_idx, line in enumerate(block_lines):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # 各種コマンドパターンをチェック
                self._check_make_commands(doc_path, line, block_idx)
                self._check_python_commands(doc_path, line, block_idx)
                self._check_file_paths(doc_path, line, block_idx)
    
    def _check_make_commands(self, doc_path: Path, command: str, block_idx: int) -> None:
        """makeコマンドの検証"""
        make_match = re.search(r'make\s+([a-zA-Z0-9_-]+)', command)
        if not make_match:
            return
        
        target = make_match.group(1)
        makefile_path = self.project_root / 'Makefile'
        
        if not makefile_path.exists():
            self.findings.append(ReviewFinding(
                severity="HIGH",
                category="ACCURACY",
                file_path=str(doc_path.relative_to(self.project_root)),
                line_number=block_idx + 1,
                description=f"Makefileが存在しないのに 'make {target}' を使用",
                suggestion="Makefileを作成するか、該当コマンドを削除してください",
                evidence=f"Command: {command}"
            ))
            return
        
        # Makefileのターゲット一覧を取得
        if target not in self.verified_commands:
            try:
                result = subprocess.run(
                    ['make', '-n', target], 
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode != 0:
                    self.findings.append(ReviewFinding(
                        severity="CRITICAL",
                        category="ACCURACY", 
                        file_path=str(doc_path.relative_to(self.project_root)),
                        line_number=block_idx + 1,
                        description=f"存在しないMakeターゲット 'make {target}'",
                        suggestion=f"Makefileにターゲット '{target}' を追加するか、コマンドを修正してください",
                        evidence=f"Command: {command}\nError: {result.stderr.strip()}"
                    ))
                else:
                    self.verified_commands.add(target)
            except subprocess.TimeoutExpired:
                self.findings.append(ReviewFinding(
                    severity="MEDIUM",
                    category="ACCURACY",
                    file_path=str(doc_path.relative_to(self.project_root)),
                    line_number=block_idx + 1,
                    description=f"Makeターゲット '{target}' の検証がタイムアウト",
                    suggestion="コマンドの実行時間を確認してください",
                    evidence=f"Command: {command}"
                ))
    
    def _check_python_commands(self, doc_path: Path, command: str, block_idx: int) -> None:
        """Pythonコマンドの検証"""
        python_match = re.search(r'python\s+(scripts/[^\s]+)', command)
        if not python_match:
            return
        
        script_path = python_match.group(1)
        full_script_path = self.project_root / script_path
        
        if not full_script_path.exists():
            self.findings.append(ReviewFinding(
                severity="CRITICAL",
                category="ACCURACY",
                file_path=str(doc_path.relative_to(self.project_root)),
                line_number=block_idx + 1,
                description=f"存在しないスクリプト '{script_path}' を参照",
                suggestion=f"スクリプト '{script_path}' を作成するか、パスを修正してください",
                evidence=f"Command: {command}"
            ))
        elif script_path not in self.verified_files:
            # スクリプトの実行可能性を確認
            try:
                result = subprocess.run(
                    ['python', script_path, '--help'],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                if result.returncode not in [0, 1, 2]:  # 一般的な正常終了コード
                    self.findings.append(ReviewFinding(
                        severity="HIGH", 
                        category="ACCURACY",
                        file_path=str(doc_path.relative_to(self.project_root)),
                        line_number=block_idx + 1,
                        description=f"スクリプト '{script_path}' の実行に失敗",
                        suggestion="スクリプトの構文エラーまたは依存関係を確認してください",
                        evidence=f"Command: {command}\nError: {result.stderr.strip()}"
                    ))
                else:
                    self.verified_files.add(script_path)
            except subprocess.TimeoutExpired:
                self.findings.append(ReviewFinding(
                    severity="MEDIUM",
                    category="ACCURACY",
                    file_path=str(doc_path.relative_to(self.project_root)),
                    line_number=block_idx + 1,
                    description=f"スクリプト '{script_path}' の検証がタイムアウト",
                    suggestion="スクリプトの実行時間を確認してください",
                    evidence=f"Command: {command}"
                ))
    
    def _check_file_paths(self, doc_path: Path, command: str, block_idx: int) -> None:
        """ファイルパスの検証"""
        # Markdownリンクは除外（この関数はコードブロック内のコマンド専用）
        if '](' in command or command.strip().startswith('- **['):
            return
            
        # 一般的なファイルパターンを検索（より厳密なパターン）
        file_patterns = [
            r'(app/[^\s\]\)]+\.py)',
            r'(tests/[^\s\]\)]+\.py)', 
            r'(docs/[^\s\]\)]+\.md)',
            r'([^\s\]\)]+\.yml)',
            r'([^\s\]\)]+\.yaml)',
            r'([^\s\]\)]+\.json)',
            r'([^\s\]\)]+\.toml)'
        ]
        
        for pattern in file_patterns:
            matches = re.findall(pattern, command)
            for file_path in matches:
                # Markdownリンク構文の一部を除外
                if '](' in file_path or file_path.endswith(']'):
                    continue
                    
                full_path = self.project_root / file_path
                if not full_path.exists():
                    self.findings.append(ReviewFinding(
                        severity="HIGH",
                        category="ACCURACY", 
                        file_path=str(doc_path.relative_to(self.project_root)),
                        line_number=block_idx + 1,
                        description=f"存在しないファイル '{file_path}' を参照",
                        suggestion=f"ファイル '{file_path}' を作成するか、パスを修正してください",
                        evidence=f"Command: {command}"
                    ))
    
    def _review_claims_verification(self, doc_path: Path, content: str, lines: List[str]) -> None:
        """主張・数値の検証可能性レビュー"""
        
        # 検証困難な数値的主張を検索
        unverifiable_patterns = [
            (r'(\d+)日間.*開発', "開発期間の主張に根拠が必要"),
            (r'(\d+(?:\.\d+)?)ms.*レスポンス', "レスポンス時間の測定方法が必要"),
            (r'(\d+(?:\.\d+)?)倍.*向上', "性能向上の測定基準が必要"),
            (r'業界平均.*(\d+)', "業界平均の出典が必要"),
        ]
        
        for line_idx, line in enumerate(lines):
            for pattern, message in unverifiable_patterns:
                if re.search(pattern, line):
                    # 同一行または近傍行に根拠があるかチェック
                    context_lines = lines[max(0, line_idx-2):min(len(lines), line_idx+3)]
                    context = '\n'.join(context_lines)
                    
                    # 根拠キーワードの存在確認
                    evidence_keywords = ['測定', '実測', '検証', 'テスト', '確認', 'time', 'pytest', 'benchmark']
                    has_evidence = any(keyword in context for keyword in evidence_keywords)
                    
                    if not has_evidence:
                        self.findings.append(ReviewFinding(
                            severity="MEDIUM",
                            category="ACCURACY",
                            file_path=str(doc_path.relative_to(self.project_root)),
                            line_number=line_idx + 1,
                            description=f"検証困難な数値的主張: {message}",
                            suggestion="測定方法、測定日時、測定環境を明記してください",
                            evidence=f"Line: {line.strip()}"
                        ))
    
    def _review_clarity_consistency(self, doc_path: Path, content: str, lines: List[str]) -> None:
        """明確性・一貫性のレビュー"""
        
        # 曖昧な表現を検索
        vague_patterns = [
            (r'高性能', "具体的な数値・指標で表現してください"),
            (r'高品質', "品質の指標（テストカバレッジ、バグ数等）を明記してください"),
            (r'簡単(?:に|な)', "具体的な手順数や時間を明記してください"),
            (r'すぐに', "具体的な時間を明記してください"),
            (r'たくさん', "具体的な数量を明記してください"),
        ]
        
        for line_idx, line in enumerate(lines):
            for pattern, suggestion in vague_patterns:
                if re.search(pattern, line):
                    self.findings.append(ReviewFinding(
                        severity="LOW",
                        category="CLARITY",
                        file_path=str(doc_path.relative_to(self.project_root)),
                        line_number=line_idx + 1,
                        description=f"曖昧な表現: {pattern}",
                        suggestion=suggestion,
                        evidence=f"Line: {line.strip()}"
                    ))
    
    def _review_completeness(self, doc_path: Path, content: str, lines: List[str]) -> None:
        """完全性のレビュー"""
        
        # README.mdの場合、必須セクションをチェック
        if doc_path.name == 'README.md':
            required_sections = [
                ('## インストール', 'インストール手順'),
                ('## 使用方法', '基本的な使用方法'),  
                ('## 開発', '開発環境のセットアップ'),
                ('## テスト', 'テスト実行方法'),
                ('## ライセンス', 'ライセンス情報')
            ]
            
            for section_pattern, description in required_sections:
                if not re.search(section_pattern, content, re.IGNORECASE):
                    self.findings.append(ReviewFinding(
                        severity="MEDIUM",
                        category="COMPLETENESS",
                        file_path=str(doc_path.relative_to(self.project_root)),
                        line_number=1,
                        description=f"必須セクション不足: {description}",
                        suggestion=f"セクション '{section_pattern}' を追加してください",
                        evidence=""
                    ))
    
    def _review_maintainability(self, doc_path: Path, content: str, lines: List[str]) -> None:
        """保守性のレビュー"""
        
        # 日付の記載があるか（古い情報の検出）
        date_patterns = [
            r'最終更新.*(\d{4})',
            r'検証日.*(\d{4}-\d{2}-\d{2})',
            r'測定日.*(\d{4}-\d{2}-\d{2})'
        ]
        
        has_date_info = False
        for line in lines:
            for pattern in date_patterns:
                if re.search(pattern, line):
                    has_date_info = True
                    break
            if has_date_info:
                break
        
        if not has_date_info and doc_path.name == 'README.md':
            self.findings.append(ReviewFinding(
                severity="LOW",
                category="MAINTAINABILITY",
                file_path=str(doc_path.relative_to(self.project_root)),
                line_number=1,
                description="最終更新日の記載がありません",
                suggestion="ドキュメントの最終更新日を記載してください",
                evidence=""
            ))
    
    def generate_report(self) -> int:
        """レビューレポートの生成"""
        print("\n" + "=" * 80)
        print("📊 Critical Documentation Review Report")
        print("=" * 80)
        print(f"レビュー実行日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        if not self.findings:
            print("✅ Excellent! No critical issues found.")
            print("ドキュメントは批判的レビューをパスしました。")
            print("=" * 80)
            return 0
        
        # 重要度別にグループ化
        by_severity = {}
        for finding in self.findings:
            if finding.severity not in by_severity:
                by_severity[finding.severity] = []
            by_severity[finding.severity].append(finding)
        
        # カテゴリ別にグループ化
        by_category = {}
        for finding in self.findings:
            if finding.category not in by_category:
                by_category[finding.category] = []
            by_category[finding.category].append(finding)
        
        # 重要度順で表示
        severity_order = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']
        
        for severity in severity_order:
            if severity in by_severity:
                findings = by_severity[severity]
                icon = {'CRITICAL': '🚨', 'HIGH': '❌', 'MEDIUM': '⚠️', 'LOW': '💡'}[severity]
                print(f"\n{icon} {severity} Issues ({len(findings)}件):")
                print("-" * 80)
                
                for i, finding in enumerate(findings, 1):
                    print(f"{i:3d}. [{finding.category}] {finding.file_path}:{finding.line_number}")
                    print(f"     問題: {finding.description}")
                    print(f"     提案: {finding.suggestion}")
                    if finding.evidence:
                        print(f"     根拠: {finding.evidence}")
                    print()
        
        # サマリー統計
        print("=" * 80)
        print("📈 Summary Statistics:")
        print("-" * 80)
        for severity in severity_order:
            count = len(by_severity.get(severity, []))
            if count > 0:
                print(f"{severity}: {count}件")
        
        print("\nカテゴリ別:")
        for category, findings in by_category.items():
            print(f"{category}: {len(findings)}件")
        
        print("\n" + "=" * 80)
        
        # 重要度に応じて終了コードを決定
        if 'CRITICAL' in by_severity:
            return 2
        elif 'HIGH' in by_severity:
            return 1
        else:
            return 0
    
    def run(self, target_files: List[Path]) -> int:
        """批判的レビューの実行"""
        print("🔬 Critical Documentation Review Starting...")
        print("=" * 80)
        print("📋 レビュー原則:")
        print("✅ 事実ベースの記載のみ許可")
        print("✅ 全ての主張に検証可能な根拠が必要")
        print("✅ 推測・憶測は明確に区別して記載")
        print("✅ ゼロベースでの客観的評価")
        print("=" * 80)
        
        for doc_path in target_files:
            if doc_path.exists() and doc_path.suffix == '.md':
                self.review_document(doc_path)
        
        return self.generate_report()

def main():
    """メインエントリーポイント"""
    parser = argparse.ArgumentParser(description='批判的ドキュメントレビュー')
    parser.add_argument('--target', type=str, help='レビュー対象ファイル')
    parser.add_argument('--all', action='store_true', help='全Markdownファイルをレビュー')
    
    args = parser.parse_args()
    
    reviewer = CriticalDocumentationReviewer()
    
    if args.all:
        target_files = list(reviewer.project_root.glob('**/*.md'))
        # 除外パス
        target_files = [
            f for f in target_files 
            if not any(exclude in str(f) for exclude in ['.venv', 'node_modules', 'htmlcov', '.git'])
        ]
    elif args.target:
        target_files = [reviewer.project_root / args.target]
    else:
        target_files = [reviewer.project_root / 'README.md']
    
    return reviewer.run(target_files)

if __name__ == "__main__":
    sys.exit(main())