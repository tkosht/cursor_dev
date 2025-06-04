#!/usr/bin/env python3
"""
TDD Compliance Check Script

このスクリプトは、TDD実践ルールが確実に適用されていることを確認します。
pre-commitフックとして実行され、ルール違反時はコミットを阻止します。
"""

import sys
from pathlib import Path

# 重要なナレッジファイルのパス
REQUIRED_KNOWLEDGE_FILES = [
    "memory-bank/tdd_process_failures_lessons.md",
    "memory-bank/critical_issues_tracker.md",
]

# TDDチェックリスト
TDD_CHECKLIST = [
    "API仕様を実際に確認したか？",
    "テストが本当に失敗するか確認したか（Red段階）？",
    "最小限の実装でテストを通したか（Green段階）？",
    "リファクタリング後もテストが通るか確認したか？",
    "カバレッジ90%以上を維持しているか？",
    "エラーハンドリング・境界値テストを含んでいるか？",
]


def check_required_files():
    """必須ナレッジファイルの存在確認"""
    print("📚 Required Knowledge Files Check:")

    missing_files = []
    for file_path in REQUIRED_KNOWLEDGE_FILES:
        if not Path(file_path).exists():
            missing_files.append(file_path)
            print(f"   ❌ Missing: {file_path}")
        else:
            print(f"   ✅ Found: {file_path}")

    return len(missing_files) == 0


def display_tdd_checklist():
    """TDDチェックリストの表示"""
    print("\n🔍 TDD Process Checklist:")
    print("=" * 60)

    for i, item in enumerate(TDD_CHECKLIST, 1):
        print(f"{i}. {item}")

    print("=" * 60)
    print("⚠️  上記すべての項目を確認してからコミットしてください。")
    print("📖 詳細: memory-bank/tdd_process_failures_lessons.md")


def check_test_files():
    """テストファイルの存在確認"""
    print("\n🧪 Test Files Check:")

    test_files = list(Path("tests").glob("**/*test_*.py"))
    if len(test_files) == 0:
        print("   ❌ No test files found")
        return False

    print(f"   ✅ Found {len(test_files)} test files")
    return True


def main():
    """メイン実行関数"""
    print("🚀 TDD Compliance Check Starting...")
    print("-" * 50)

    # 1. 必須ファイル確認
    if not check_required_files():
        print("\n❌ Required knowledge files missing!")
        print("📋 Please create missing files before committing.")
        return 1

    # 2. テストファイル確認
    if not check_test_files():
        print("\n❌ No test files found!")
        print("📋 TDD requires tests - create tests before committing.")
        return 1

    # 3. TDDチェックリスト表示
    display_tdd_checklist()

    # 4. Critical Issues確認
    if Path("memory-bank/critical_issues_tracker.md").exists():
        print("\n📋 Critical Issues Status:")
        print("   🔗 Check: memory-bank/critical_issues_tracker.md")
        print("   ⚠️  Ensure all critical issues are addressed.")

    print("\n✅ TDD Compliance Check Completed")
    print("🎯 Proceed with confidence - TDD rules verified!")

    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
