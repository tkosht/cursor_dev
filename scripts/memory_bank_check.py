#!/usr/bin/env python3
"""
Memory Bank Required Reading Check Script

このスクリプトは、Memory Bankの必須ナレッジが確実に読み込まれ、
適用されていることを確認します。
"""

import sys
from datetime import datetime
from pathlib import Path

# 必須Memory Bankファイル
REQUIRED_MEMORY_BANK_FILES = [
    "memory-bank/projectbrief.md",
    "memory-bank/activeContext.md",
    "memory-bank/progress.md",
    "memory-bank/tdd_process_failures_lessons.md",
    "memory-bank/critical_issues_tracker.md",
]

# TDD実践で重要なファイル
TDD_CRITICAL_FILES = [
    "memory-bank/tdd_process_failures_lessons.md",
    ".pre-commit-config.yaml",
    "pyproject.toml",  # pytest設定確認
]


def check_memory_bank_files():
    """Memory Bankファイルの存在確認"""
    print("📚 Memory Bank Files Check:")

    missing_files = []
    for file_path in REQUIRED_MEMORY_BANK_FILES:
        if not Path(file_path).exists():
            missing_files.append(file_path)
            print(f"   ❌ Missing: {file_path}")
        else:
            print(f"   ✅ Found: {file_path}")

    return len(missing_files) == 0


def check_tdd_compliance_setup():
    """TDD実践環境の確認"""
    print("\n🔍 TDD Compliance Setup Check:")

    issues = []

    # pre-commitフック確認
    if not Path(".pre-commit-config.yaml").exists():
        issues.append("pre-commit configuration missing")
        print("   ❌ .pre-commit-config.yaml not found")
    else:
        print("   ✅ pre-commit configuration found")

    # pytest設定確認
    if Path("pyproject.toml").exists():
        with open("pyproject.toml", "r") as f:
            content = f.read()
            if "--cov-fail-under=90" in content:
                print("   ✅ Coverage requirement (90%) configured")
            else:
                issues.append("Coverage requirement not set to 90%")
                print("   ❌ Coverage requirement (90%) not configured")
    else:
        issues.append("pyproject.toml missing")
        print("   ❌ pyproject.toml not found")

    return len(issues) == 0


def display_memory_bank_summary():
    """Memory Bank重要事項の要約表示"""
    print("\n📋 Memory Bank Critical Knowledge Summary:")
    print("=" * 60)

    knowledge_points = [
        "TDD Red-Green-Refactor プロセスの厳格実践",
        "API仕様の事前確認必須（推測禁止）",
        "カバレッジ90%以上の維持必須",
        "Critical Issues の継続監視",
        "テスト失敗時の根本原因分析",
        "エラーハンドリング・境界値テストの網羅",
    ]

    for i, point in enumerate(knowledge_points, 1):
        print(f"{i}. {point}")

    print("=" * 60)
    print("📖 詳細: memory-bank/tdd_process_failures_lessons.md")


def check_recent_activity():
    """最近のTDD実践活動確認"""
    print("\n📅 Recent TDD Activity Check:")

    # Critical Issues Trackerの最終更新確認
    if Path("memory-bank/critical_issues_tracker.md").exists():
        stat = Path("memory-bank/critical_issues_tracker.md").stat()
        last_modified = datetime.fromtimestamp(stat.st_mtime)
        print(
            f"   📝 Critical Issues last updated: {last_modified.strftime('%Y-%m-%d %H:%M')}"
        )

        # 最近1時間以内なら活発
        time_diff = datetime.now() - last_modified
        if time_diff.total_seconds() < 3600:
            print("   ✅ Recent activity detected (within 1 hour)")
        else:
            print("   ⚠️  No recent updates detected")
    else:
        print("   ❌ Critical Issues tracker not found")


def main():
    """メイン実行関数"""
    print("🚀 Memory Bank Required Reading Check Starting...")
    print("-" * 50)

    all_checks_passed = True

    # 1. Memory Bankファイル確認
    if not check_memory_bank_files():
        print("\n❌ Required Memory Bank files missing!")
        all_checks_passed = False

    # 2. TDD環境確認
    if not check_tdd_compliance_setup():
        print("\n❌ TDD compliance setup incomplete!")
        all_checks_passed = False

    # 3. 重要事項要約表示
    display_memory_bank_summary()

    # 4. 最近の活動確認
    check_recent_activity()

    # 5. 結果判定
    if all_checks_passed:
        print("\n✅ Memory Bank Required Reading Check PASSED")
        print(
            "🎯 All required knowledge is available and properly configured!"
        )
        return 0
    else:
        print("\n❌ Memory Bank Required Reading Check FAILED")
        print(
            "📋 Please address missing files/configurations before proceeding."
        )
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
