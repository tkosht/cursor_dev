# 理想的な Security Checker テストケース設計案

## 設計方針

1.  **明確な期待値:** 各テストケースで、検出 *すべき* 文字列 (`should_detect = True`) と、検出 *すべきでない* 文字列 (`should_detect = False`) を明確に区別します。
2.  **有効な形式の検証:** 各種キー/トークンの公式な、または一般的に認識されている有効な形式を確実に検出できることをテストします。
3.  **無効な形式の非検出検証:**
    *   明らかに短すぎる文字列
    *   プレフィックスが異なる文字列
    *   形式が部分的にしか一致しない文字列
    *   一般的な単語や変数名
    *   これらが誤って検出されないことをテストします (False Positives の排除)。
4.  **境界値・エッジケースの考慮:**
    *   最小/最大長（もし定義されていれば）
    *   特定の文字種（例: Base64, Hex）
    *   コメントアウトされた機密情報（これは検出対象とすることが多い）
    *   複数行にまたがる定義（Pythonの文字列結合など）
5.  **`findings` の活用:** 可能であれば、検出された場合に `findings` リストに正しい情報（行番号、ルール名など）が含まれているかも検証します（より高度なテスト）。

## 理想的なテストケース案 (抜粋・修正)

```python
# tests/test_security_check.py (Idealized Version Snippets)

import os
import tempfile
import pytest
from bin.security_check import SecurityChecker # 仮定: このCheckerは理想的に動作する

# --- (Fixtures: security_checker, temp_file は変更なし) ---

class TestIdealSecurityChecker:

    # ... (他のテストメソッドは同様の考え方で修正・拡充) ...

    def test_openai_key_detection_ideal(
        self,
        security_checker: SecurityChecker,
        temp_file: str
    ) -> None:
        """OpenAI APIキーの理想的な検出テスト。
        有効な形式のみを検出し、無効な形式は検出しないことを検証する。
        """
        test_cases = [
            # --- 検出すべきケース (True Positives) ---
            # 標準的な形式
            ("openai_api_key = '[OPENAI_KEY_REDACTED]'", True, "Standard OpenAI Key"),
            # ダブルクォート
            ('openai_key = "[OPENAI_KEY_REDACTED]"', True, "Double Quoted Key"),
            # 環境変数代入風
            ('os.environ["OPENAI_API_KEY"] = "[OPENAI_KEY_REDACTED]"', True, "Assignment Style"),
            # コメント内のキー (検出対象とする場合)
            ("# secret_key = '[OPENAI_KEY_REDACTED]'", True, "Commented Out Key"),

            # --- 検出 すべきでない ケース (False Positives / Negatives) ---
            # 短すぎるキー
            ("invalid_key = 'sk-short'", False, "Too Short Key"),
            # プレフィックスが違う
            ("wrong_prefix = 'pk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'", False, "Wrong Prefix"),
            # 形式が不完全
            ("incomplete = 'sk-incompletekey'", False, "Incomplete Format"),
            # 一般的な変数名
            ("variable = 'sk_variable_name'", False, "Looks like variable"),
            # テスト用文字列
            ("test_string = 'this is not a key sk-abcdefg'", False, "Plain text containing prefix"),
            # 空文字列
            ("empty_key = ''", False, "Empty String"),
        ]

        for content, should_detect, description in test_cases:
            with open(temp_file, 'w') as f:
                f.write(content)

            found, findings = security_checker.scan_file(temp_file)
            assert found == should_detect, \
                f"Test Case Failed: '{description}'\n" \
                f"Content: '{content}'\n" \
                f"Expected detection: {should_detect}, Actual: {found}"

            # オプション: findings の内容も検証
            if should_detect:
                assert len(findings) >= 1, f"Findings should not be empty for '{description}'"
                # assert findings[0]['rule_name'] == 'openai_key' # ルール名が返る場合
            else:
                assert len(findings) == 0, f"Findings should be empty for '{description}'"


    def test_github_token_detection_ideal(
        self,
        security_checker: SecurityChecker,
        temp_file: str
    ) -> None:
        """GitHubトークンの理想的な検出テスト。
        有効な形式のみを検出し、無効な形式は検出しないことを検証する。
        """
        test_cases = [
            # --- 検出すべきケース (True Positives) ---
            # Personal Access Token (Classic) - 40 chars [a-f0-9] (例)
            ("gh_token = 'ghp_aBcDeFgHiJkLmNoPqRsTuVwXyZaBcDeFgHiJkL'", True, "Classic PAT"), # ghp_ + 36 chars
            # Personal Access Token (Fine-grained) - Prefix + Base64 (例)
            ("github_pat = 'github_pat_11ABCD22EFGH33IJKL44MNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'", True, "Fine-grained PAT"),
            # OAuth Token - gho_...
            ("oauth_token = 'gho_aBcDeFgHiJkLmNoPqRsTuVwXyZaBcDeFgHiJkL'", True, "OAuth Token"),
            # Refresh Token - ghr_...
            ("refresh_token = '[GITHUB_TOKEN_REDACTED]'", True, "Refresh Token"),
            # コメント内
            ("# GITHUB_TOKEN = 'ghp_...' ", True, "Commented Out Token"),

            # --- 検出 すべきでない ケース (False Positives / Negatives) ---
            # 短すぎるトークン
            ("short_token = 'ghp_short'", False, "Too Short Token"),
            # プレフィックスのみ
            ("prefix_only = 'ghp_'", False, "Prefix Only"),
            # 不正な文字種 (Classic PAT の例)
            ("invalid_chars = 'ghp_aBcDeFgHiJkLmNoPqRsTuVwXyZaBcDeFgHiJkL_'", False, "Invalid Characters"),
            # 一般的な変数名
            ("variable = 'ghp_variable_name'", False, "Looks like variable"),
            # テスト用文字列
            ("test_string = 'this is not a token ghp_abcdefg'", False, "Plain text containing prefix"),
        ]

        for content, should_detect, description in test_cases:
            with open(temp_file, 'w') as f:
                f.write(content)

            found, findings = security_checker.scan_file(temp_file)
            assert found == should_detect, \
                f"Test Case Failed: '{description}'\n" \
                f"Content: '{content}'\n" \
                f"Expected detection: {should_detect}, Actual: {found}"
            # オプション: findings の検証
            if should_detect:
                assert len(findings) >= 1
            else:
                assert len(findings) == 0

    # --- (test_mask_file, test_check_directory_with_auto_mask, test_main_function_with_auto_mask も同様に、
    #      理想的な検出ロジックに基づいたマスク結果を期待するように修正) ---

    def test_masking_preserves_context_ideal(
        self,
        security_checker: SecurityChecker,
        temp_file: str
    ) -> None:
        """マスク処理がコンテキストを保持し、機密情報のみを置換するかのテスト。"""
        original_content = """
        config = {
            'user': 'testuser',
            'api_key': '[OPENAI_KEY_REDACTED]', # This is sensitive
            'endpoint': 'https://api.example.com',
            'github_token': 'ghp_aBcDeFgHiJkLmNoPqRsTuVwXyZaBcDeFgHiJkL'
        }
        print(f"Using key: {config['api_key']}")
        """
        expected_masked_content_pattern = """
        config = {
            'user': 'testuser',
            'api_key': '[REDACTED_OPENAI_KEY]', # This is sensitive
            'endpoint': 'https://api.example.com',
            'github_token': '[REDACTED_GITHUB_TOKEN]'
        }
        print(f"Using key: {config['api_key']}")
        """ # 期待するマスク後パターン（実際のマスク文字列はCheckerの実装による）

        with open(temp_file, 'w') as f:
            f.write(original_content)

        changed = security_checker.mask_file(temp_file)
        assert changed, "Masking should have occurred"

        with open(temp_file, 'r') as f:
            masked_content = f.read()

        # 単純な文字列比較ではなく、重要な部分がマスクされ、
        # 他の部分が保持されていることを確認する方が堅牢
        assert "'user': 'testuser'" in masked_content
        assert "'endpoint': 'https://api.example.com'" in masked_content
        assert "print(f" in masked_content
        assert "[OPENAI_KEY_REDACTED]" not in masked_content
        assert "ghp_aBcDeFgHiJkLmNoPqRsTuVwXyZaBcDeFgHiJkL" not in masked_content
        # 実際のマスク後文字列を確認 (例)
        assert "'api_key': '[REDACTED_OPENAI_KEY]'" in masked_content
        assert "'github_token': '[REDACTED_GITHUB_TOKEN]'" in masked_content

```

## Mermaid ダイアグラム (理想的な OpenAI キーテストフロー)

```mermaid
graph TD
    A[テスト開始: test_openai_key_detection_ideal] --> B(テストケースループ);
    B -- 各ケース --> C{テストケース準備};
    C --> D[一時ファイルに content 書き込み];
    D --> E[security_checker.scan_file(temp_file) 実行];
    E --> F{結果検証};
    F -- found == should_detect? --> G{期待通りか?};
    G -- Yes --> H{findings 検証 (オプション)};
    H -- findings 正しい? --> I{テストケース成功};
    G -- No --> J[アサーションエラー (テスト失敗)];
    H -- findings 違う --> J;
    I --> B;
    B -- ループ終了 --> K[テストメソッド終了];

    subgraph "テストケース例: 'sk-short'"
        Content["content = 'invalid_key = \\'sk-short\\''"]
        Expect["should_detect = False"]
    end
    subgraph "テストケース例: 'sk-valid...'"
        Content2["content = 'openai_key = \\'sk-valid...\\''"]
        Expect2["should_detect = True"]
    end

    style J fill:#f99,stroke:#333,stroke-width:2px
    style I fill:#9f9,stroke:#333,stroke-width:1px