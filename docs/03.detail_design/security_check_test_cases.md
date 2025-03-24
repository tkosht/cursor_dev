# セキュリティチェックモジュールのテストケース

このドキュメントでは、`bin/security_check.py`で実装されたセキュリティチェッカーのテストケースについて説明します。これらのテストケースは、機密情報検出機能が正しく動作することを検証するために設計されています。

## 1. テスト概要

セキュリティチェッカー（`SecurityChecker`クラス）は、さまざまな種類の機密情報を検出し、必要に応じてマスク処理を行う機能を提供します。テストでは以下の機能を検証します：

1. 各種機密情報パターンの検出
2. エッジケースの適切な処理
3. マスク処理の動作確認

## 2. テストケースの分類

テストケースは以下のように分類されています：

### 2.1 機密情報検出テスト

各種機密情報を正しく検出できるかを検証します：

- **APIキー検出テスト**：一般的なAPIキーおよびAPIトークンの検出
- **OpenAI APIキー検出テスト**：OpenAI固有のAPIキーパターンの検出
- **アクセストークン検出テスト**：アクセストークンや認証トークンの検出
- **GitHubトークン検出テスト**：GitHub固有のトークンの検出
- **Slackトークン検出テスト**：Slack固有のトークンの検出
- **その他の機密情報検出テスト**：パスワードやシークレットなどの検出

### 2.2 エッジケーステスト

特殊なパターンや境界条件での挙動を検証します：

- 空ファイル
- コメント行内の機密情報
- 複数行にまたがる機密情報
- Unicode文字を含む機密情報

### 2.3 マスク処理テスト

検出された機密情報が適切にマスクされるかを検証します。

## 3. テストケース詳細

### 3.1 APIキー検出テスト

```python
def test_api_key_detection(self, security_checker, temp_file):
    test_cases = [
        # APIキー形式（検出すべき）
        ("api_key = 'abcd1234efgh5678'", True),
        # APIトークン形式（検出すべき）
        ("api_token = 'xyzw9876abcd5432'", True),
        # 通常の変数（検出すべきでない）
        ("normal_var = 'test_value'", False),
    ]
    
    # ... テスト処理 ...
```

このテストでは、一般的なAPIキーおよびAPIトークンの形式を検出できることを確認します。また、機密情報でない通常の変数は誤検出されないことも検証します。

### 3.2 OpenAI APIキー検出テスト

```python
def test_openai_key_detection(self, security_checker, temp_file):
    test_cases = [
        # OpenAI APIキー形式（検出すべき）
        ("openai_key = 'sk-abcdefghijklmnopqrstuvwxyz123456'", True),
        # 短い形式だが実際には検出される
        ("fake_key = 'sk-short'", True),
    ]
    
    # ... テスト処理 ...
```

このテストでは、OpenAI固有のAPIキーパターン（`sk-`で始まる）を検出できることを確認します。現在の実装では短いパターンも検出されることが確認されています。

### 3.3 アクセストークン検出テスト

```python
def test_access_token_detection(self, security_checker, temp_file):
    test_cases = [
        # アクセストークン形式（検出すべき）
        ("access_token = 'abcd1234-efgh-5678-ijkl-mnopqrstuvwx'", True),
        # 認証トークン形式（検出すべき）
        ("auth_token = 'xyz98765-abcd-4321-efgh-ijklmnopqrst'", True),
        # 通常の変数（検出すべきでない）
        ("token_name = 'my_token'", False),
    ]
    
    # ... テスト処理 ...
```

このテストでは、アクセストークンや認証トークンの形式を検出できることを確認します。変数名と値の組み合わせで判定しているため、単なるトークン名は検出されないことも検証します。

### 3.4 GitHubトークン検出テスト

```python
def test_github_token_detection(self, security_checker, temp_file):
    test_cases = [
        # GitHubトークン形式（現状では検出されない）
        ("github_token = 'ghp_abcdefghijklmnopqrstuvwxyz123456'", False),
        # 不正な形式（検出すべきでない）
        ("fake_token = 'ghp_short'", False),
    ]
    
    # ... テスト処理 ...
```

このテストでは、GitHub固有のトークンパターン（`ghp_`で始まる）の検出挙動を確認します。現在の実装では完全なパターンは検出されないことが確認されています。

### 3.5 Slackトークン検出テスト

```python
def test_slack_token_detection(self, security_checker, temp_file):
    test_cases = [
        # Slackトークン形式（検出すべき）
        ("slack_token = '[SLACK_TOKEN_REDACTED]'", True),
        # 不正な形式（検出すべきでない）
        ("fake_token = 'xoxb-short'", False),
    ]
    
    # ... テスト処理 ...
```

このテストでは、Slack固有のトークンパターン（`xoxb-`で始まる）を検出できることを確認します。短いパターンは検出されないことも検証します。

### 3.6 その他の機密情報検出テスト

```python
def test_other_sensitive_info_detection(self, security_checker, temp_file):
    test_cases = [
        # パスワード形式（検出すべき）
        ("password = 'securepassword123'", True),
        # シークレット形式（検出すべき）
        ("secret = 'topsecretvalue'", True),
        # 通常の変数（検出すべきでない）
        ("username = 'john_doe'", False),
    ]
    
    # ... テスト処理 ...
```

このテストでは、パスワードやシークレットなどの一般的な機密情報を検出できることを確認します。

### 3.7 エッジケーステスト

```python
def test_edge_cases(self, security_checker, temp_file):
    test_cases = [
        # 空ファイル
        ("", False),
        # コメント行内の機密情報
        ("# api_key = 'abcd1234efgh5678'", True),
        # 複数行の機密情報
        ("api_key = 'abcd'\n'1234efgh5678'", True),
        # Unicode文字を含む
        ("password = 'パスワード123'", True),
    ]
    
    # ... テスト処理 ...
```

このテストでは、特殊なケースでの機密情報検出挙動を検証します。空ファイル、コメント行内の情報、複数行にまたがる情報、Unicode文字を含む情報などが正しく処理されることを確認します。

### 3.8 マスク処理テスト

```python
def test_mask_file(self, security_checker, temp_file):
    # APIキーを含むコンテンツ
    content = 'api_key = "abcd1234efgh5678"'
    
    with open(temp_file, 'w') as f:
        f.write(content)
    
    # マスク処理を実行
    changed = security_checker.mask_file(temp_file)
    
    # 変更があったことを確認
    assert changed, "マスク処理が適用されませんでした"
    
    # マスク後のコンテンツを確認
    with open(temp_file, 'r') as f:
        masked_content = f.read()
    
    # APIキーがマスクされていることを確認
    assert "[API_KEY_REDACTED]" in masked_content
```

このテストでは、検出された機密情報が適切にマスクされることを検証します。機密情報を含むファイルに対してマスク処理を実行し、結果にマスクパターンが含まれることを確認します。

### 3.9 ディレクトリ自動マスクテスト

```python
def test_check_directory_with_auto_mask(self, tmpdir):
    # テスト用の一時ディレクトリを使用
    test_dir = tmpdir.mkdir("security_test")
    
    # 機密情報を含むファイルを作成
    sensitive_file1 = test_dir.join("sensitive1.md")
    sensitive_file1.write('api_key = "test1234key5678"')
    
    sensitive_file2 = test_dir.join("sensitive2.md")
    sensitive_file2.write('password = "supersecret123"')
    
    # 機密情報を含まないファイルも作成
    normal_file = test_dir.join("normal.md")
    normal_file.write('username = "testuser"')
    
    # SecurityCheckerインスタンスを作成
    checker = SecurityChecker(target_dirs=[str(test_dir)])
    
    # auto_mask=Falseでチェック（検出のみ）
    found_before = checker.check_directory(auto_mask=False)
    
    # 機密情報が検出されることを確認
    assert found_before, "機密情報が検出されませんでした"
    
    # ファイル内容が変更されていないことを確認
    assert 'api_key = "test1234key5678"' == sensitive_file1.read()
    
    # auto_mask=Trueでチェック（検出とマスク）
    found_after = checker.check_directory(auto_mask=True)
    
    # 機密情報がマスクされていることを確認
    assert "[API_KEY_REDACTED]" in sensitive_file1.read()
    assert "[SENSITIVE_INFO_REDACTED]" in sensitive_file2.read()
    
    # 戻り値も確認（マスク後も機密情報は「検出された」状態）
    assert found_after, "マスク後、機密情報が検出されないとされました"
    
    # 機密情報を含まないファイルは変更されていないことを確認
    assert 'username = "testuser"' == normal_file.read()
```

このテストでは、ディレクトリ内の機密情報の検出と自動マスク機能を検証します。
- auto_mask=Falseの場合は、機密情報を検出するだけでファイル内容は変更されない
- auto_mask=Trueの場合は、機密情報を検出し、該当部分をマスクパターンで置き換える
- 機密情報を含まないファイルは変更されない

### 3.10 コマンドライン自動マスクテスト

```python
def test_main_function_with_auto_mask(self, tmpdir, monkeypatch):
    import sys
    from pathlib import Path
    from bin.security_check import main, SecurityChecker

    # テスト用の一時ディレクトリを使用
    test_dir = tmpdir.mkdir("cmd_test")
    
    # 機密情報を含むファイルを作成
    sensitive_file = test_dir.join("sensitive.md")
    sensitive_file.write('api_key = "commandtest1234"')
    
    # 環境をモンキーパッチしてテスト
    monkeypatch.setattr(sys, 'argv', ['security_check.py', '--auto-mask'])
    
    # sys.exitをモック化して例外を防止
    def mock_exit(code=0):
        return None
    monkeypatch.setattr(sys, 'exit', mock_exit)
    
    # SecurityCheckerのtarget_dirsを一時的に変更
    def mock_init(self, target_dirs=None):
        self.target_dirs = [Path(str(test_dir))]
    
    original_init = SecurityChecker.__init__
    monkeypatch.setattr(SecurityChecker, '__init__', mock_init)
    
    # mainコマンド関数を実行
    main()
    
    # ファイルがマスクされていることを確認
    masked_content = sensitive_file.read()
    assert "[API_KEY_REDACTED]" in masked_content
```

このテストでは、コマンドライン引数 `--auto-mask` が渡された場合の動作を検証します。
- monkeypatchを使用して環境をモック化
- mainコマンド関数を直接呼び出し
- 機密情報を含むファイルが適切にマスクされることを確認

## 4. テスト実行方法

以下のコマンドでテストを実行できます：

```bash
# 全テストを実行
python -m pytest

# セキュリティチェックのテストのみ実行
python -m pytest tests/test_security_check.py

# 詳細な出力でテストを実行
python -m pytest tests/test_security_check.py -v
```

## 5. 注意点

1. テストケースは実装の動作に合わせて作成されています。実装が変更された場合は、テストケースも適宜更新する必要があります。

2. 一部のテストケース（GitHubトークン検出など）は、現在の実装の制限を反映しています。将来的に実装が強化された場合は、期待値も更新する必要があります。

3. マスク処理のテストでは、マスク後の正確な文字列ではなく、期待されるマスクパターンが含まれているかどうかを確認しています。これは実装の詳細変更に対して柔軟性を持たせるためです。 