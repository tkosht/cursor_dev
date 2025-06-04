#!/usr/bin/env python3
"""
ディレクトリ構造検証スクリプト

プロジェクトのディレクトリ構造が規約に準拠しているかを検証します。
"""

import os
import sys
from pathlib import Path
from typing import List, Tuple, Dict

# プロジェクトルート
PROJECT_ROOT = Path(__file__).parent.parent

# 必須ディレクトリ構造
REQUIRED_DIRECTORIES = {
    "app": "ソースコード (Pythonパッケージ)",
    "app/a2a": "A2Aプロトコル実装",
    "bin": "実行ファイル、スクリプト",
    "docker": "Dockerfile群",
    "docs": "ドキュメント",
    "docs/01.requirements": "要件定義書",
    "docs/02.basic_design": "基本設計書",
    "docs/03.detail_design": "詳細設計書",
    "docs/04.implementation_reports": "実装報告書",
    "docs/05.articles": "技術記事・Note記事",
    "docs/90.references": "参考資料・ガイド",
    "docs/91.notes": "メモ・下書き",
    "memory-bank": "AIの記憶領域",
    "scripts": "ユーティリティスクリプト",
    "tests": "テストコード",
    "tests/unit": "ユニットテスト",
    "tests/integration": "統合テスト",
    "tests/e2e": "E2Eテスト",
}

# 必須ファイル
REQUIRED_FILES = {
    "README.md": "プロジェクトREADME",
    "pyproject.toml": "Poetry設定ファイル",
    "LICENSE": "ライセンス",
    "cursor_dev.code-workspace": "ワークスペース設定",
    "docs/90.references/directory_structure.md": "ディレクトリ構造規約",
}

# 禁止されたルートレベルファイルのパターン
FORBIDDEN_ROOT_PATTERNS = [
    "*.py",  # Pythonファイルはapp/以下に配置
    "*.md",  # READMEとCLAUDE以外のMarkdownはdocs/以下に配置
    "test_*",  # テストファイルはtests/以下に配置
]

# 許可されたルートレベルファイル
ALLOWED_ROOT_FILES = {
    "README.md", "CLAUDE.md", "LICENSE", "Makefile",
    "pyproject.toml", "poetry.lock", "requirements.txt",
    "compose.yml", ".gitignore", ".dockerignore",
    "cursor_dev.code-workspace", "package.json", "package-lock.json",
    "coverage.json"  # テストカバレッジレポート
}


def check_required_directories() -> List[str]:
    """必須ディレクトリの存在を確認"""
    missing = []
    for dir_path, description in REQUIRED_DIRECTORIES.items():
        full_path = PROJECT_ROOT / dir_path
        if not full_path.exists() or not full_path.is_dir():
            missing.append(f"{dir_path} ({description})")
    return missing


def check_required_files() -> List[str]:
    """必須ファイルの存在を確認"""
    missing = []
    for file_path, description in REQUIRED_FILES.items():
        full_path = PROJECT_ROOT / file_path
        if not full_path.exists() or not full_path.is_file():
            missing.append(f"{file_path} ({description})")
    return missing


def check_forbidden_root_files() -> List[str]:
    """ルートディレクトリの禁止ファイルを確認"""
    violations = []
    
    for item in PROJECT_ROOT.iterdir():
        if item.is_file():
            # 許可リストにないファイルをチェック
            if item.name not in ALLOWED_ROOT_FILES:
                # 隠しファイルは除外
                if not item.name.startswith('.'):
                    violations.append(item.name)
    
    return violations


def check_empty_directories() -> List[str]:
    """空のディレクトリを確認（.gitkeepがあれば許可）"""
    empty_dirs = []
    
    for dir_path in REQUIRED_DIRECTORIES.keys():
        full_path = PROJECT_ROOT / dir_path
        if full_path.exists() and full_path.is_dir():
            contents = list(full_path.iterdir())
            if not contents:
                empty_dirs.append(dir_path)
            elif len(contents) == 1 and contents[0].name == '.gitkeep':
                # .gitkeepのみの場合は正常
                pass
    
    return empty_dirs


def main():
    """メイン処理"""
    print("🔍 ディレクトリ構造検証を開始します...\n")
    
    errors = []
    warnings = []
    
    # 必須ディレクトリのチェック
    missing_dirs = check_required_directories()
    if missing_dirs:
        errors.append("❌ 必須ディレクトリが見つかりません:")
        for dir_path in missing_dirs:
            errors.append(f"   - {dir_path}")
    
    # 必須ファイルのチェック
    missing_files = check_required_files()
    if missing_files:
        errors.append("\n❌ 必須ファイルが見つかりません:")
        for file_path in missing_files:
            errors.append(f"   - {file_path}")
    
    # 禁止ファイルのチェック
    forbidden_files = check_forbidden_root_files()
    if forbidden_files:
        warnings.append("\n⚠️  ルートディレクトリに不適切なファイルがあります:")
        for file_name in forbidden_files:
            warnings.append(f"   - {file_name}")
        warnings.append("   適切なサブディレクトリに移動してください。")
    
    # 空ディレクトリのチェック
    empty_dirs = check_empty_directories()
    if empty_dirs:
        warnings.append("\n⚠️  空のディレクトリがあります（.gitkeepの追加を検討）:")
        for dir_path in empty_dirs:
            warnings.append(f"   - {dir_path}")
    
    # 結果の表示
    if errors:
        print("🚫 エラーが見つかりました:\n")
        for error in errors:
            print(error)
        print()
    
    if warnings:
        print("⚠️  警告:\n")
        for warning in warnings:
            print(warning)
        print()
    
    if not errors and not warnings:
        print("✅ ディレクトリ構造は規約に準拠しています！")
        return 0
    
    if errors:
        print("❌ ディレクトリ構造の検証に失敗しました。")
        print("📖 詳細は docs/90.references/directory_structure.md を参照してください。")
        return 1
    else:
        print("⚠️  警告はありますが、ディレクトリ構造は基本的に準拠しています。")
        return 0


if __name__ == "__main__":
    sys.exit(main())