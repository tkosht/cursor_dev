#!/usr/bin/env python3
"""
品質ゲート強制チェックスクリプト

このスクリプトは以下の品質基準を強制的にチェックします：
1. Flake8: コード品質 (警告ゼロ必須)
2. Pytest: テスト実行 (100%成功必須)
3. Coverage: カバレッジ (90%以上必須)

使用方法:
    python scripts/quality_gate_check.py

終了コード:
    0: 全品質基準クリア
    1: 品質基準違反発見
"""

import subprocess
import sys
from pathlib import Path


class QualityGate:
    """品質ゲートチェック実行クラス"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.errors = []

    def run_command(self, cmd: str, description: str) -> bool:
        """コマンド実行と結果判定"""
        print(f"\n🔍 {description}")
        print(f"実行: {cmd}")

        result = subprocess.run(
            cmd.split(),
            cwd=self.project_root,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

        if result.returncode == 0:
            print(f"✅ {description}: 合格")
            if result.stdout.strip():
                print(f"出力: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {description}: 不合格")
            print(f"エラー: {result.stderr.strip()}")
            if result.stdout.strip():
                print(f"詳細: {result.stdout.strip()}")
            self.errors.append(f"{description}: {result.stderr.strip()}")
            return False

    def check_flake8(self) -> bool:
        """Flake8品質チェック (警告ゼロ必須)"""
        return self.run_command(
            "poetry run flake8 app/ tests/", "Flake8 コード品質チェック"
        )

    def check_tests(self) -> bool:
        """Pytestテスト実行 (100%成功必須)"""
        return self.run_command(
            "poetry run pytest tests/ -v", "Pytest テスト実行"
        )

    def check_coverage(self) -> bool:
        """カバレッジチェック (90%以上必須)"""
        return self.run_command(
            "poetry run pytest tests/ --cov=app --cov-fail-under=90",
            "カバレッジチェック (90%以上)",
        )

    def run_all_checks(self) -> bool:
        """全品質チェック実行"""
        print("=" * 60)
        print("🚀 品質ゲート強制チェック開始")
        print("=" * 60)

        # 品質基準表示
        print("\n📋 品質基準:")
        print("- Flake8: 警告ゼロ (88文字制限)")
        print("- Pytest: テスト100%成功")
        print("- Coverage: 90%以上")

        # 各チェック実行
        flake8_ok = self.check_flake8()
        tests_ok = self.check_tests()
        coverage_ok = self.check_coverage()

        # 結果判定
        all_passed = flake8_ok and tests_ok and coverage_ok

        print("\n" + "=" * 60)
        if all_passed:
            print("🎉 全品質基準クリア！")
            print("✅ コミット/デプロイ許可")
        else:
            print("🚨 品質基準違反発見")
            print("❌ コミット/デプロイ禁止")
            print("\n🔧 修正必要項目:")
            for error in self.errors:
                print(f"   - {error}")
        print("=" * 60)

        return all_passed


def main():
    """メイン処理"""
    gate = QualityGate()
    success = gate.run_all_checks()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
