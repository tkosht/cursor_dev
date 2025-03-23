#!/usr/bin/env python3
"""セキュリティチェックスクリプト

このスクリプトは、.specstory/history/ および memory-bank/ 内のファイルから
機密情報を検出し、必要に応じてマスク処理を行います。
"""

import re
import sys
from pathlib import Path
from typing import List, Pattern, Tuple


class SecurityChecker:
    """セキュリティチェッカークラス"""

    # 機密情報のパターン定義
    PATTERNS: List[Tuple[str, Pattern[str], str]] = [
        (
            "APIキー",
            re.compile(r'(?i)(api[_-]?key|apikey|api[_-]?token)["\']?\s*[:=]\s*["\']([\w-]+)'),
            "[API_KEY_REDACTED]"
        ),
        (
            "OpenAI APIキー",
            re.compile(r'(?i)sk-[\w-]{32,}'),
            "[OPENAI_KEY_REDACTED]"
        ),
        (
            "アクセストークン",
            re.compile(r'(?i)(access[_-]?token|auth[_-]?token)["\']?\s*[:=]\s*["\']([\w-]+)'),
            "[TOKEN_REDACTED]"
        ),
        (
            "GitHubトークン",
            re.compile(r'(?i)gh[ps]_[\w-]{36,}'),
            "[GITHUB_TOKEN_REDACTED]"
        ),
        (
            "Slackトークン",
            re.compile(r'(?i)xox[baprs]-[\w-]{32,}'),
            "[SLACK_TOKEN_REDACTED]"
        ),
        (
            "その他の機密情報",
            re.compile(r'(?i)(password|secret|key)["\']?\s*[:=]\s*["\']([\w-]+)'),
            "[SENSITIVE_INFO_REDACTED]"
        ),
    ]

    def __init__(self, target_dirs: List[str]):
        """
        Args:
            target_dirs (List[str]): チェック対象のディレクトリリスト
        """
        self.target_dirs = [Path(d) for d in target_dirs]

    def scan_file(self, file_path: Path) -> Tuple[bool, List[Tuple[str, int]]]:
        """ファイルをスキャンし、機密情報を検出します。

        Args:
            file_path (Path): スキャン対象のファイルパス

        Returns:
            Tuple[bool, List[Tuple[str, int]]]:
                - 機密情報が見つかったかどうか
                - [(パターン名, 行番号), ...]
        """
        found = False
        findings = []

        with open(file_path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f, 1):
                for pattern_name, pattern, _ in self.PATTERNS:
                    if pattern.search(line):
                        found = True
                        findings.append((pattern_name, i))

        return found, findings

    def mask_file(self, file_path: Path) -> bool:
        """ファイル内の機密情報をマスクします。

        Args:
            file_path (Path): マスク対象のファイルパス

        Returns:
            bool: 変更が行われたかどうか
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        masked_content = content
        for _, pattern, mask in self.PATTERNS:
            masked_content = pattern.sub(mask, masked_content)

        if masked_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(masked_content)
            return True

        return False

    def check_directory(self, auto_mask: bool = False) -> bool:
        """ディレクトリ内のファイルをチェックします。

        Args:
            auto_mask (bool): 機密情報を自動的にマスクするかどうか

        Returns:
            bool: 機密情報が見つかったかどうか
        """
        found_secrets = False

        for target_dir in self.target_dirs:
            if not target_dir.exists():
                print(f"警告: ディレクトリが存在しません: {target_dir}")
                continue

            for file_path in target_dir.glob("**/*.md"):
                has_secrets, findings = self.scan_file(file_path)
                if has_secrets:
                    found_secrets = True
                    print(f"\n{file_path} で機密情報が見つかりました:")
                    for pattern_name, line_num in findings:
                        print(f"  - {pattern_name} (行 {line_num})")

                    if auto_mask:
                        if self.mask_file(file_path):
                            print(f"  → 機密情報をマスクしました: {file_path}")

        return found_secrets


def main():
    """メイン関数"""
    import argparse

    parser = argparse.ArgumentParser(description="機密情報検出・マスクツール")
    parser.add_argument(
        "--auto-mask",
        action="store_true",
        help="検出された機密情報を自動的にマスクする"
    )
    args = parser.parse_args()

    target_dirs = [".specstory/history", "memory-bank"]
    checker = SecurityChecker(target_dirs)

    print("セキュリティチェックを開始します...")
    found_secrets = checker.check_directory(auto_mask=args.auto_mask)

    if found_secrets:
        if not args.auto_mask:
            print("\n警告: 機密情報が見つかりました。")
            print("以下のオプションで対応してください：")
            print("1. 機密情報を手動で修正")
            print("2. python3 bin/security_check.py --auto-mask を実行")
        sys.exit(1)
    else:
        print("\n✓ 機密情報は見つかりませんでした。")
        sys.exit(0)


if __name__ == "__main__":
    main() 