#!/usr/bin/env python3
"""セキュリティチェックスクリプト

このスクリプトは、.specstory/history/、memory-bank/、docs/、tests/ 内のファイルから
機密情報を検出し、必要に応じてマスク処理を行います。
誤検出を減らすため、コンテキストを考慮した検証を行います。
"""

import re
import subprocess
import sys
from pathlib import Path
from typing import List, Optional, Pattern, Tuple


class SecurityChecker:
    """セキュリティチェッカークラス"""

    # 除外パターン（誤検出を防ぐ）
    EXCLUDED_PATHS = [
        r"docs/.*/examples?/.*",
        r"docs/.*/sample.*",
        r"tests/.*test_.*\.py",
        r"memory-bank/.*/example.*",
        r"templates/.*",
        r".*\.md\.template",
    ]

    # コードブロック内のパターン（Markdownファイル用）
    CODE_BLOCK_PATTERNS = [
        re.compile(r"```[\s\S]*?```", re.MULTILINE),  # Fenced code blocks
        re.compile(r"^    .*$", re.MULTILINE),        # Indented code blocks
        re.compile(r"`[^`\n]*`"),                     # Inline code
    ]

    # 機密情報のパターン定義 (Specific patterns first, then Generic)
    PATTERNS: List[Tuple[str, Pattern[str], str, int]] = [
        # --- Specific Patterns ---
        # Tuple format: (Name, Pattern, Mask, Capture Group Index for Secret)
        (
            "OpenAI APIキー",
            # Capture group 1: The key itself
            # (Compromise: Detects keys slightly longer than 48 chars)
            re.compile(r"(sk-[a-zA-Z0-9]{48})"),
            "[OPENAI_KEY_REDACTED]",
            1,
        ),
        (
            "GitHubトークン",
            # Capture group 1: The token itself (already defined by outer parens)
            re.compile(
                r"\b("
                r"ghp_[a-zA-Z0-9]{36}|"  # Classic PAT
                r"gho_[a-zA-Z0-9]{36}|"  # OAuth
                r"ghs_[a-zA-Z0-9]{36}|"  # App Installation
                r"ghr_[a-zA-Z0-9_]{40,}|"  # Refresh Token
                r"github_pat_[a-zA-Z0-9_]{80,}"  # Fine-grained PAT
                r")\b"
            ),
            "[GITHUB_TOKEN_REDACTED]",
            1,
        ),
        (
            "Slackトークン",
            # Capture group 1: The token itself (moved (?i) to the start)
            re.compile(r"(?i)(xox[baprs]-\d+-\d+-[a-zA-Z0-9]+)"),
            "[SLACK_TOKEN_REDACTED]",
            1,
        ),
        # --- Generic Patterns (Require closing quote on the same line) ---
        (
            "APIキー",
            # Capture group 2: The key value
            re.compile(
                r'(?i)(api[_-]?key|apikey|api[_-]?token)["\']?\s*[:=]\s*["\']'
                # Require at least 6 characters for the value
                r"((?!sk-|ghp_|gho_|ghs_|ghr_|github_pat_|xox[baprs]-)[\w-]{6,})"
                r'["\']'
            ),
            "[API_KEY_REDACTED]",
            2,  # Note: Capture group index is 2 here
        ),
        (
            "アクセストークン",
            # Capture group 2: The token value
            re.compile(
                r'(?i)(access[_-]?token|auth[_-]?token)["\']?\s*[:=]\s*["\']'
                # Require at least 6 characters for the value
                r"((?!sk-|ghp_|gho_|ghs_|ghr_|github_pat_|xox[baprs]-)[\w-]{6,})"
                r'["\']'
            ),
            "[TOKEN_REDACTED]",
            2,  # Note: Capture group index is 2 here
        ),
        (
            "その他の機密情報",
            # Capture group 2: The sensitive value
            re.compile(
                r'(?i)(password|secret|key)["\']?\s*[:=]\s*["\']'
                # Require at least 6 characters for the value
                r"((?!sk-|ghp_|gho_|ghs_|ghr_|github_pat_|xox[baprs]-)[\w-]{6,})"
                r'["\']'
            ),
            "[SENSITIVE_INFO_REDACTED]",
            2,  # Note: Capture group index is 2 here
        ),
    ]

    # チェック対象のファイル拡張子
    TARGET_EXTENSIONS = [".md", ".py", ".txt"]

    def __init__(self, target_dirs: Optional[List[str]] = None):
        """
        Args:
            target_dirs (Optional[List[str]]): チェック対象のディレクトリリスト (現在は未使用)
        """
        if target_dirs:
            self.target_dirs = [Path(d) for d in target_dirs]
        else:
            self.target_dirs = []

    def should_skip_file(self, file_path: Path) -> bool:
        """ファイルをスキップすべきかどうか判定"""
        file_str = str(file_path)
        for pattern in self.EXCLUDED_PATHS:
            if re.match(pattern, file_str):
                return True
        return False

    def is_in_code_block(self, content: str, line_num: int) -> bool:
        """指定行がコードブロック内にあるかチェック（Markdownファイル用）"""
        lines = content.split('\n')
        if line_num > len(lines):
            return False
        
        # Check if we're inside a code block
        in_fenced_block = False
        for i, line in enumerate(lines[:line_num], 1):
            if line.strip().startswith('```'):
                in_fenced_block = not in_fenced_block
            elif i == line_num:
                # Check if current line is indented code block
                if line.startswith('    ') or line.startswith('\t'):
                    return True
                # Check if current line is inline code
                if line.count('`') >= 2:
                    return True
                return in_fenced_block
        
        return in_fenced_block

    def is_documentation_example(self, file_path: Path, line: str) -> bool:
        """ドキュメント内の例かどうか判定"""
        # ファイル名での判定
        if any(keyword in str(file_path).lower() for keyword in 
               ['example', 'sample', 'template', 'demo', 'tutorial']):
            return True
        
        # 行の内容での判定
        example_indicators = [
            '# 例:', '# Example:', '# サンプル:', '例：', 'Example:', 'Sample:',
            'デモ用', 'テスト用', 'placeholder', 'your-key-here', 'dummy',
            'fake-', 'test-', 'mock-', 'example-'
        ]
        
        line_lower = line.lower()
        return any(indicator.lower() in line_lower for indicator in example_indicators)

    def scan_file(self, file_path: Path) -> Tuple[bool, List[Tuple[str, int, str]]]:
        """ファイルをスキャンし、機密情報を検出します。

        Args:
            file_path (Path): スキャン対象のファイルパス

        Returns:
            Tuple[bool, List[Tuple[str, int, str]]]:
                - 機密情報が見つかったかどうか
                - [(パターン名, 行番号, 重要度), ...]
        """
        # スキップ対象ファイルかチェック
        if self.should_skip_file(file_path):
            return False, []

        found = False
        findings = []

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            lines = content.split('\n')

        for i, line in enumerate(lines, 1):
            # コードブロック内かチェック（Markdownファイルの場合）
            if file_path.suffix == '.md' and self.is_in_code_block(content, i):
                continue

            # ドキュメント例かチェック
            is_example = self.is_documentation_example(file_path, line)

            for pattern_name, pattern, _, _ in self.PATTERNS:
                if pattern.search(line):
                    severity = "warning" if is_example else "error"
                    findings.append((pattern_name, i, severity))
                    if severity == "error":
                        found = True

        return found, findings

    def mask_file(self, file_path: Path) -> bool:
        """ファイル内の機密情報をマスクします。

        Args:
            file_path (Path): マスク対象のファイルパス

        Returns:
            bool: 変更が行われたかどうか
        """
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Remove unused variable: original_content = content
        modified_content = content
        changed = False

        # Iterate through patterns to find and replace secrets
        # We iterate through patterns, and for each pattern, find all matches
        for _, pattern, mask, capture_group_index in self.PATTERNS:
            new_masked_content = ""
            last_end = 0
            # Find all matches for the current pattern in the
            # *current* state of the content
            for match in pattern.finditer(modified_content):
                # Get the start and end of the specific group to mask (key itself)
                try:
                    key_start = match.start(capture_group_index)
                    key_end = match.end(capture_group_index)
                    # End of the entire match
                    match_end = match.end()

                    # Append content before the key + the mask +
                    # content after the key but within the match
                    new_masked_content += modified_content[last_end:key_start]
                    new_masked_content += mask
                    new_masked_content += modified_content[
                        key_end:match_end
                    ]  # Add back the part after the key

                    # Use the end of the *entire* match for the next slice start
                    last_end = match_end
                    changed = True
                except IndexError:
                    # Handle cases where the capture group might not exist
                    # (shouldn't happen with current regexes)
                    print(
                        f"Warning: Capture group {capture_group_index} not found for "
                        f"pattern {pattern.pattern} in {file_path}"
                    )
                    new_masked_content += modified_content[
                        last_end : match.end()
                    ]
                    last_end = match.end()

            # Append the rest of the content after the last match
            new_masked_content += modified_content[last_end:]
            # Update content for the next pattern iteration
            modified_content = (
                new_masked_content  # Add two spaces before comment
            )

        # Remove extra blank lines
        if changed:
            with open(file_path, "w", encoding="utf-8") as f:
                # Use the correct variable name
                f.write(modified_content)
            return True

        return False

    def process_file(self, file_path: Path, auto_mask: bool) -> bool:
        """1つのファイルを処理します。

        Args:
            file_path (Path): 処理対象のファイルパス
            auto_mask (bool): 機密情報を自動的にマスクするかどうか

        Returns:
            bool: 機密情報が見つかったかどうか（エラーレベルのみ）
        """
        try:
            has_errors, findings = self.scan_file(file_path)
            
            if findings:
                errors = [f for f in findings if f[2] == "error"]
                warnings = [f for f in findings if f[2] == "warning"]
                
                if errors:
                    print(f"\n❌ {file_path} で機密情報が見つかりました:")
                    for pattern_name, line_num, _ in errors:
                        print(f"  - {pattern_name} (行 {line_num})")
                
                if warnings:
                    print(f"\n⚠️  {file_path} で潜在的な機密情報が見つかりました（例/サンプル）:")
                    for pattern_name, line_num, _ in warnings:
                        print(f"  - {pattern_name} (行 {line_num}) [警告のみ]")

                if auto_mask and has_errors:
                    if self.mask_file(file_path):
                        print(f"  → 機密情報をマスクしました: {file_path}")
                
                return has_errors  # エラーレベルのみコミットをブロック
                
        except UnicodeDecodeError:
            print(
                f"警告: ファイルの読み込みに失敗しました（エンコーディング問題）: {file_path}"
            )
        except Exception as e:
            print(
                f"警告: ファイルの処理中にエラーが発生しました: {file_path} - {str(e)}"
            )

        return False


def get_staged_files() -> List[Path]:
    """Gitからステージングされたファイルリストを取得します。"""
    try:
        # Explicitly set cwd to ensure git diff runs in the correct directory
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8",
            cwd=".",  # Run git diff in the current directory
        )
        staged_files_raw = result.stdout.splitlines()
        return [Path(f) for f in staged_files_raw]
    except FileNotFoundError:
        print(
            "エラー: git コマンドが見つかりません。gitがインストールされ、PATHに含まれていることを確認してください。"
        )
        sys.exit(2)
    except subprocess.CalledProcessError as e:
        print(f"エラー: ステージングされたファイルの取得に失敗しました: {e}")
        print(f"stderr: {e.stderr}")
        sys.exit(2)
    except Exception as e:
        print(
            f"予期せぬエラー: ステージングされたファイルの取得中にエラーが発生しました: {e}"
        )
        sys.exit(2)


def filter_files_to_check(files: List[Path]) -> List[Path]:
    """チェック対象のファイルをフィルタリングします。"""
    # Compare relative paths directly
    test_file_rel_path = Path("tests/test_security_check.py")
    checker = SecurityChecker()
    
    return [
        f
        for f in files
        if f.suffix in SecurityChecker.TARGET_EXTENSIONS
        and f.exists()
        and f != test_file_rel_path  # Exclude the test file itself
        and not checker.should_skip_file(f)  # Apply improved filtering
    ]


def process_files(
    checker: SecurityChecker, files: List[Path], auto_mask: bool
) -> bool:
    """指定されたファイルリストを処理し、機密情報が見つかったかどうかを返します。"""
    found_secrets = False
    for file_path in files:
        if checker.process_file(file_path, auto_mask=auto_mask):
            found_secrets = True
    return found_secrets


def main():
    """メイン関数"""
    import argparse

    parser = argparse.ArgumentParser(
        description="機密情報検出・マスクツール (ステージングされたファイルのみ対象)"
    )
    parser.add_argument(
        "--auto-mask",
        action="store_true",
        help="検出された機密情報を自動的にマスクする",
    )
    args = parser.parse_args()

    print("ステージングされたファイルのセキュリティチェックを開始します...")

    staged_files = get_staged_files()
    files_to_check = filter_files_to_check(staged_files)

    if not files_to_check:
        print("\n✓ チェック対象のステージングされたファイルはありません。")
        sys.exit(0)

    print(f"\nチェック対象ファイル ({len(files_to_check)} 件):")
    for f in files_to_check:
        print(f"  - {f}")

    checker = SecurityChecker()
    found_secrets = process_files(checker, files_to_check, args.auto_mask)

    if found_secrets:
        if not args.auto_mask:
            print("\n❌ COMMIT BLOCKED: 機密情報（エラーレベル）が見つかりました。")
            print("手動で修正するか、警告のみの場合は --no-verify でコミットできます。")
        sys.exit(1)
    else:
        print(
            "\n✅ ステージングされたファイルに機密情報（エラーレベル）は見つかりませんでした。"
        )
        sys.exit(0)


if __name__ == "__main__":
    main()
