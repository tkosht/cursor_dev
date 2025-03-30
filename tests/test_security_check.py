import os

# import shlex # Removed definitively
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

from bin.security_check import SecurityChecker


# Helper function to run git commands in tests
def run_git_command(cmd: str, cwd: Path):
    """Runs a git command in the specified directory."""
    try:
        # Using shell=True version, ensure test cmd is safe
        result = subprocess.run(
            f"git {cmd}",
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True,
            encoding='utf-8',
            shell=True
        )
        return result
    except subprocess.CalledProcessError as e:
        print(f"Git command failed: git {cmd}")
        print(f"Stderr: {e.stderr}")
        print(f"Stdout: {e.stdout}")
        raise  # Re-raise the exception to fail the test


@pytest.fixture
def git_repo(tmp_path: Path) -> Path:
    """Creates a temporary git repository for testing."""
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()
    run_git_command("init", cwd=repo_path)
    run_git_command("config user.email 'test@example.com'", cwd=repo_path)
    run_git_command("config user.name 'Test User'", cwd=repo_path)
    return repo_path


class TestSecurityChecker:
    """セキュリティチェッカーのテストクラス。

    このクラスは、セキュリティチェッカーの機能をテストします。
    主に、機密情報の検出、誤検知の防止、エッジケースの処理を検証します。
    """

    @pytest.fixture
    def security_checker(self) -> SecurityChecker:
        """SecurityCheckerインスタンスを提供するフィクスチャ。

        Returns:
            SecurityChecker: テスト用のSecurityCheckerインスタンス
        """
        return SecurityChecker(target_dirs=["."])

    @pytest.fixture
    def temp_file(self) -> str:
        """一時ファイルのパスを提供するフィクスチャ。

        テスト終了時に自動的にファイルを削除します。

        Returns:
            str: 一時ファイルのパス
        """
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as f:
            yield f.name
        os.unlink(f.name)

    def test_api_key_detection(
        self,
        security_checker: SecurityChecker,
        temp_file: str
    ) -> None:
        """APIキーの検出テスト。

        Args:
            security_checker: セキュリティチェッカーインスタンス
            temp_file: テスト用一時ファイルのパス
        """
        test_cases = [
            # Re-applied fix: Use valid dummy values
            ("api_key = 'dummy-api-key-123456'", True),
            ("api_token: 'another-dummy-token-789'", True),
            ("normal_var = 'test_value'", False),
            ("api_key = 'short'", False),  # Too short value
        ]
        
        for content, should_detect in test_cases:
            with open(temp_file, 'w') as f:
                f.write(content)
            
            # Call scan_file with Path object
            found, findings = security_checker.scan_file(Path(temp_file))
            assert found == should_detect, \
                f"内容 '{content}' の検出結果が期待と異なります。" \
                f"期待: {should_detect}, 実際: {found}"

    def test_openai_key_detection_ideal(
        self,
        security_checker: SecurityChecker,
        temp_file: str
    ) -> None:
        """OpenAI APIキーの理想的な検出テスト。
        有効な形式のみを検出し、無効な形式は検出しないことを検証する。
        """
        # Generate a valid 48-char key for testing
        valid_key_chars = "aBcDeFgHiJkLmNoPqRsTuVwXyZ0123456789aBcDeFgHiJkLm"
        valid_key = f"sk-{valid_key_chars}"  # Total 51 chars: sk- + 48

        test_cases = [
            # --- 検出すべきケース (True Positives) ---
            # 標準的な形式
            (f"openai_api_key = '{valid_key}'", True, "Standard OpenAI Key"),
            # ダブルクォート
            (f'openai_key = "{valid_key}"', True, "Double Quoted Key"),
            # 環境変数代入風
            (f'os.environ["OPENAI_API_KEY"] = "{valid_key}"', True, "Assignment Style"),
            # コメント内のキー (検出対象とする場合 - 現在のCheckerは検出する)
            (f"# secret_key = '{valid_key}'", True, "Commented Out Key"),
            # キーが単独で行にある場合
            (f"{valid_key}", True, "Key alone on line"),


            # --- 検出 すべきでない ケース (False Positives / Negatives) ---
            # 短すぎるキー
            ("invalid_key = 'sk-shortkey12345'", False, "Too Short Key"),
            # 長すぎるキー (現在のパターンでは誤検出される - 制限事項)
            (f"long_key = '{valid_key}extra'", True, "Too Long Key (Known Limitation)"),
            # プレフィックスが違う
            (f"wrong_prefix = 'pk-{valid_key_chars}'", False, "Wrong Prefix pk-"),
            (f"wrong_prefix = 'sk_{valid_key_chars}'", False, "Wrong Prefix sk_"),
            # 形式が不完全 (ハイフンなし)
            (f"incomplete = 'sk{valid_key_chars}'", False, "Incomplete Format (no hyphen)"),
            # 一般的な変数名
            ("variable = 'sk_variable_name'", False, "Looks like variable"),
            # テスト用文字列
            ("test_string = 'this is not a key sk-abcdefg'", False, "Plain text containing short prefix"),
            (f"test_string = 'this is not a real key {valid_key[:20]}...'", False, "Plain text containing partial key"),
            # 空文字列
            ("empty_key = ''", False, "Empty String"),
            ("key = 'sk-'", False, "Prefix only"),
        ]

        for content, should_detect, description in test_cases:
            with open(temp_file, 'w') as f:
                f.write(content)

            found, findings = security_checker.scan_file(Path(temp_file))  # Pass Path object
            assert found == should_detect, \
                f"Test Case Failed: '{description}'\n" \
                f"Content: '{content}'\n" \
                f"Expected detection: {should_detect}, Actual: {found}"

            # オプション: findings の内容も検証
            if should_detect:
                assert len(findings) >= 1, f"Findings should not be empty for '{description}'"
                # Check if the finding corresponds to the OpenAI pattern
                assert any(f[0] == "OpenAI APIキー" for f in findings), \
                    f"Correct pattern name not found in findings for '{description}'. Findings: {findings}"
            else:
                # Ensure no findings *at all* for this specific pattern if not detected
                assert not any(f[0] == "OpenAI APIキー" for f in findings), \
                    f"OpenAI pattern unexpectedly found for '{description}'. Findings: {findings}"

    def test_access_token_detection(
        self,
        security_checker: SecurityChecker,
        temp_file: str
    ) -> None:
        """アクセストークンの検出テスト。

        Args:
            security_checker: セキュリティチェッカーインスタンス
            temp_file: テスト用一時ファイルのパス
        """
        test_cases = [
            # Re-applied fix: Use valid dummy values
            ("access_token = 'dummy-access-token-abcde'", True),
            ("auth_token: \"dummy-auth-token-fghij\"", True),
            ("token_name = 'my_token'", False),
            ("access_token = 'short'", False),  # Too short
        ]
        
        for content, should_detect in test_cases:
            with open(temp_file, 'w') as f:
                f.write(content)
            
            # Call scan_file with Path object
            found, findings = security_checker.scan_file(Path(temp_file))
            assert found == should_detect, \
                f"内容 '{content}' の検出結果が期待と異なります。" \
                f"期待: {should_detect}, 実際: {found}"

    def test_github_token_detection_ideal(
        self,
        security_checker: SecurityChecker,
        temp_file: str
    ) -> None:
        """GitHubトークンの理想的な検出テスト。
        有効な形式のみを検出し、無効な形式は検出しないことを検証する。
        """
        # Generate valid tokens for testing (adjust lengths/chars as needed)
        valid_ghp = "ghp_" + "a" * 36
        valid_gho = "gho_" + "b" * 36
        valid_ghs = "ghs_" + "c" * 36
        valid_ghr = "ghr_" + "d" * 40
        valid_pat = "github_pat_" + "e" * 84

        test_cases = [
            # --- 検出すべきケース (True Positives) ---
            (f"token = '{valid_ghp}'", True, "Classic PAT (ghp)"),
            (f"token = '{valid_gho}'", True, "OAuth Token (gho)"),
            (f"token = '{valid_ghs}'", True, "App Token (ghs)"),
            (f"token = '{valid_ghr}'", True, "Refresh Token (ghr)"),
            (f"token = '{valid_pat}'", True, "Fine-grained PAT (github_pat)"),
            (f"# GITHUB_TOKEN = '{valid_ghp}'", True, "Commented Out Token"),

            # --- 検出 すべきでない ケース (False Positives / Negatives) ---
            ("short_token = 'ghp_short'", False, "Too Short Token (ghp)"),
            ("short_token = 'gho_short'", False, "Too Short Token (gho)"),
            ("short_token = 'ghs_short'", False, "Too Short Token (ghs)"),
            ("short_token = 'ghr_short'", False, "Too Short Token (ghr)"),
            ("short_token = 'github_pat_short'", False, "Too Short Token (github_pat)"),
            ("prefix_only = 'ghp_'", False, "Prefix Only (ghp)"),
            ("prefix_only = 'github_pat_'", False, "Prefix Only (github_pat)"),
            # Invalid chars (assuming only alphanumeric for ghp/gho/ghs)
            (f"invalid_chars = '{valid_ghp[:-1]}_'", False, "Invalid Characters (ghp)"),
            # Invalid length
            (f"invalid_length = '{valid_ghp}extra'", False, "Invalid Length - Too Long (ghp)"),
            (f"invalid_length = '{valid_ghp[:-1]}'", False, "Invalid Length - Too Short (ghp)"),
            # Variable names
            ("variable = 'ghp_variable_name'", False, "Looks like variable (ghp)"),
            ("variable = 'github_pat_variable'", False, "Looks like variable (github_pat)"),
            # Plain text
            ("test_string = 'this is not a token ghp_abcdefg'", False, "Plain text containing short prefix"),
            (f"test_string = 'look at {valid_ghp[:15]}...'", False, "Plain text containing partial token"),
        ]

        for content, should_detect, description in test_cases:
            with open(temp_file, 'w') as f:
                f.write(content)

            found, findings = security_checker.scan_file(Path(temp_file))
            assert found == should_detect, \
                f"Test Case Failed: '{description}'\n" \
                f"Content: '{content}'\n" \
                f"Expected detection: {should_detect}, Actual: {found}"

            # オプション: findings の内容も検証
            if should_detect:
                assert len(findings) >= 1, f"Findings should not be empty for '{description}'"
                assert any(f[0] == "GitHubトークン" for f in findings), \
                    f"Correct pattern name not found in findings for '{description}'. Findings: {findings}"
            else:
                assert not any(f[0] == "GitHubトークン" for f in findings), \
                    f"GitHub pattern unexpectedly found for '{description}'. Findings: {findings}"

    def test_slack_token_detection(
        self,
        security_checker: SecurityChecker,
        temp_file: str
    ) -> None:
        """Slackトークンの検出テスト。

        Args:
            security_checker: セキュリティチェッカーインスタンス
            temp_file: テスト用一時ファイルのパス
        """
        # Re-applied fix: Use a realistic dummy Slack token format
        valid_slack_token = "xoxb-1234567890-1234567890-abcdefghijklmnopqrstuvwx"
        test_cases = [
            (f"slack_token = '{valid_slack_token}'", True),
            ("fake_token = 'xoxb-short'", False),
            ("not_a_token = 'xox-123-abc'", False),
        ]
        
        for content, should_detect in test_cases:
            with open(temp_file, 'w') as f:
                f.write(content)
            
            # Call scan_file with Path object
            found, findings = security_checker.scan_file(Path(temp_file))
            assert found == should_detect, \
                f"内容 '{content}' の検出結果が期待と異なります。" \
                f"期待: {should_detect}, 実際: {found}"

    def test_other_sensitive_info_detection(
        self,
        security_checker: SecurityChecker,
        temp_file: str
    ) -> None:
        """その他の機密情報の検出テスト。

        Args:
            security_checker: セキュリティチェッカーインスタンス
            temp_file: テスト用一時ファイルのパス
        """
        test_cases = [
            # Use valid dummy values matching [\w-]{6,}
            ("password = 'dummy-password-123'", True),
            ("secret = \"dummy-secret-abc\"", True),
            ("key: 'dummy-key-xyz-789'", True),
            ("username = 'john_doe'", False),
            ("password = 'short'", False),  # Too short
        ]
        
        for content, should_detect in test_cases:
            with open(temp_file, 'w') as f:
                f.write(content)
            
            # Call scan_file with Path object
            found, findings = security_checker.scan_file(Path(temp_file))
            assert found == should_detect, \
                f"内容 '{content}' の検出結果が期待と異なります。" \
                f"期待: {should_detect}, 実際: {found}"

    def test_edge_cases(
        self,
        security_checker: SecurityChecker,
        temp_file: str
    ) -> None:
        """エッジケースのテスト。

        空ファイル、コメント行、複数行、Unicode文字などの特殊なケースをテストします。

        Args:
            security_checker: セキュリティチェッカーインスタンス
            temp_file: テスト用一時ファイルのパス
        """
        # Generate a valid OpenAI key for commented-out test
        valid_key_chars = "aBcDeFgHiJkLmNoPqRsTuVwXyZ0123456789aBcDeFgHiJkLm"
        valid_openai_key = f"sk-{valid_key_chars}"
        # Use valid dummy value matching [\w-]{6,} for unicode password test
        dummy_unicode_password = "password123456"  # Simple valid password
        dummy_generic_key = "generic-dummy-key-for-test"

        test_cases = [
            ("", False, "Empty File"),
            (f"# api_key = '{valid_openai_key}'", True, "Commented Out OpenAI Key"),
            (f"# api_key = '{dummy_generic_key}'", True, "Commented Out Generic API Key"),
            ("api_key = 'abcd' \\\n          '1234efgh5678'", False, "Multi-line String Concatenation"),
            (f"password = '{dummy_unicode_password}'", True, "Password Detection"),
            ("# This is just a comment", False, "Regular Comment"),
            ("api_key", False, "Variable name only"),
        ]

        for content, should_detect, description in test_cases:
            with open(temp_file, 'w') as f:
                f.write(content)

            found, findings = security_checker.scan_file(Path(temp_file))
            assert found == should_detect, \
                f"Test Case Failed: '{description}'\n" \
                f"Content:\n'''{content}'''\n" \
                f"Expected detection: {should_detect}, Actual: {found}"

            # Optional: Verify findings content for True cases
            if should_detect:
                assert len(findings) >= 1, f"Findings should not be empty for '{description}'"
            # We don't strictly check for empty findings in False cases here,
            # as other patterns might match unintentionally in edge cases.
            # The primary assert(found == should_detect) covers the main expectation.

    def test_mask_file(
        self,
        security_checker: SecurityChecker,
        temp_file: str
    ) -> None:
        """ファイル内の機密情報マスクテスト。

        Args:
            security_checker: セキュリティチェッカーインスタンス
            temp_file: テスト用一時ファイルのパス
        """
        # Use a detectable dummy key for input matching [\w-]{6,}
        dummy_key = "dummy-mask-key-12345"
        content = f'api_key = "{dummy_key}"'
        expected_mask = "[API_KEY_REDACTED]"

        with open(temp_file, 'w') as f:
            f.write(content)

        # マスク処理を実行 (Pass Path object)
        changed = security_checker.mask_file(Path(temp_file))

        assert changed, "マスク処理が適用されませんでした"

        with open(temp_file, 'r') as f:
            masked_content = f.read()

        # Check the dummy key is gone and the mask is present
        assert dummy_key not in masked_content, "Original key still present after mask"
        assert expected_mask in masked_content, \
            f"マスク結果に期待されるマスクパターン '{expected_mask}' が含まれていません。実際: {masked_content}"
    
    def test_masking_preserves_context_ideal(
        self,
        security_checker: SecurityChecker,
        temp_file: str
    ) -> None:
        """マスク処理がコンテキストを保持し、機密情報のみを置換するかのテスト。"""
        # Use valid keys that should be detected by the updated regex
        valid_openai_key = "sk-" + "a" * 48
        valid_github_key = "ghp_" + "b" * 36

        original_content = f"""
        config = {{
            'user': 'testuser',
            'api_key': '{valid_openai_key}', # This is sensitive
            'endpoint': 'https://api.example.com',
            'github_token': '{valid_github_key}'
        }}
        print(f"Using key: {{config['api_key']}}")
        """
        # Note: expected_masked_content_pattern is just for reference, not used directly

        with open(temp_file, 'w') as f:
            f.write(original_content)

        # Use Path object for consistency
        changed = security_checker.mask_file(Path(temp_file))
        assert changed, "Masking should have occurred"

        with open(temp_file, 'r') as f:
            masked_content = f.read()

        # Check that non-sensitive parts remain
        assert "'user': 'testuser'" in masked_content
        assert "'endpoint': 'https://api.example.com'" in masked_content
        assert "print(f" in masked_content
        # Check that original sensitive parts are gone
        assert valid_openai_key not in masked_content
        assert valid_github_key not in masked_content
        # Check that the correct redacted placeholders are present
        assert "'api_key': '[OPENAI_KEY_REDACTED]'" in masked_content
        assert "'github_token': '[GITHUB_TOKEN_REDACTED]'" in masked_content


# --- New Test Class for Integration/Main Function ---

class TestMainFunctionIntegration:
    """Tests the main function and script integration using a temporary git repo."""

    VALID_OPENAI_KEY = "sk-" + "a" * 48
    VALID_GITHUB_KEY = "ghp_" + "b" * 36
    SCRIPT_PATH = Path("bin/security_check.py").resolve()  # Get absolute path

    # Helper to run the script as a subprocess
    def run_script(self, args: list[str], cwd: Path) -> subprocess.CompletedProcess:
        cmd = [sys.executable, str(self.SCRIPT_PATH)] + args
        # Set check=False because we want to assert the returncode
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding='utf-8', check=False)
        print(f"\nRunning: {' '.join(cmd)}")  # Print command for debugging
        print(f"Return Code: {result.returncode}")
        print(f"Stdout:\n{result.stdout}")
        print(f"Stderr:\n{result.stderr}")
        return result

    def test_main_no_staged_files(self, git_repo: Path):
        """Tests main exits cleanly when no files are staged."""
        run_git_command("reset", cwd=git_repo)  # Reset staging area
        result = self.run_script([], cwd=git_repo)
        assert result.returncode == 0
        assert "✓ チェック対象のステージングされたファイルはありません。" in result.stdout

    def test_main_staged_clean_file(self, git_repo: Path):
        """Tests main exits cleanly with a staged file containing no secrets."""
        run_git_command("reset", cwd=git_repo)  # Reset staging area
        (git_repo / "clean.md").write_text("This file is clean.", encoding='utf-8')
        run_git_command("add clean.md", cwd=git_repo)

        result = self.run_script([], cwd=git_repo)
        assert result.returncode == 0
        assert "チェック対象ファイル (1 件):" in result.stdout
        # Use Path object and name for assertion robustness
        assert (Path("clean.md")).name in result.stdout
        assert "✓ ステージングされたファイルに機密情報は見つかりませんでした。" in result.stdout

    def test_main_staged_secret_file(self, git_repo: Path):
        """Tests main exits with error code 1 when a staged file has secrets."""
        run_git_command("reset", cwd=git_repo)  # Reset staging area
        secret_content = f"api_key = '{self.VALID_OPENAI_KEY}'"
        (git_repo / "secret.md").write_text(secret_content, encoding='utf-8')
        run_git_command("add secret.md", cwd=git_repo)

        result = self.run_script([], cwd=git_repo)
        assert result.returncode == 1  # Should exit with error
        assert "チェック対象ファイル (1 件):" in result.stdout
        assert (Path("secret.md")).name in result.stdout
        assert "secret.md で機密情報が見つかりました:" in result.stdout
        assert "OpenAI APIキー" in result.stdout
        assert "警告: 機密情報が見つかりました。" in result.stdout

    def test_main_unstaged_secret_file(self, git_repo: Path):
        """Tests main exits cleanly when secrets are only in unstaged files."""
        run_git_command("reset", cwd=git_repo)  # Reset staging area
        # Staged clean file
        (git_repo / "clean.md").write_text("Clean.", encoding='utf-8')
        run_git_command("add clean.md", cwd=git_repo)
        # Unstaged secret file
        secret_content = f"password = '{self.VALID_GITHUB_KEY}'"
        (git_repo / "secret_unstaged.md").write_text(secret_content, encoding='utf-8')

        result = self.run_script([], cwd=git_repo)
        assert result.returncode == 0  # Should exit cleanly
        assert "チェック対象ファイル (1 件):" in result.stdout
        assert (Path("clean.md")).name in result.stdout  # Only checks the staged file
        assert (Path("secret_unstaged.md")).name not in result.stdout
        assert "✓ ステージングされたファイルに機密情報は見つかりませんでした。" in result.stdout

    def test_main_staged_secret_non_target_extension(self, git_repo: Path):
        """Tests main exits cleanly when secrets are in staged files with non-target extensions."""
        run_git_command("reset", cwd=git_repo)  # Reset staging area
        secret_content = f"api_key = '{self.VALID_OPENAI_KEY}'"
        (git_repo / "secret.json").write_text(secret_content, encoding='utf-8')  # .json is not target
        run_git_command("add secret.json", cwd=git_repo)

        result = self.run_script([], cwd=git_repo)
        assert result.returncode == 0  # Should exit cleanly
        # The script finds the staged file but filters it out before checking
        assert "✓ チェック対象のステージングされたファイルはありません。" in result.stdout

    def test_main_auto_mask_staged_secret_file(self, git_repo: Path):
        """Tests auto-mask correctly modifies a staged file with secrets."""
        run_git_command("reset", cwd=git_repo)  # Reset staging area
        secret_file_path = git_repo / "secret_to_mask.md"
        secret_content = f"key = '{self.VALID_OPENAI_KEY}'"
        secret_file_path.write_text(secret_content, encoding='utf-8')
        run_git_command("add secret_to_mask.md", cwd=git_repo)

        # Run with --auto-mask
        result = self.run_script(["--auto-mask"], cwd=git_repo)
        # Script should still exit with 1 because secrets were *found*, even if masked
        assert result.returncode == 1

        # Check the file content in the working directory was actually masked
        masked_content = secret_file_path.read_text(encoding='utf-8')
        assert self.VALID_OPENAI_KEY not in masked_content
        assert "[OPENAI_KEY_REDACTED]" in masked_content

        # Check output confirms masking
        assert "→ 機密情報をマスクしました: " in result.stdout
        assert (Path("secret_to_mask.md")).name in result.stdout
