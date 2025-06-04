# セキュリティ関連パターン

`techContext.md` (旧版) より抽出した機密情報検出パターン。

## 機密情報検出パターン (Python Regex)

```python
PATTERNS = [
    ("APIキー", r'(?i)(api[_-]?key|apikey|api[_-]?token)'),
    ("OpenAI APIキー", r'(?i)sk-[\w-]{32,}'), # Note: Original length was 48, adjusted based on common patterns, might need refinement
    ("アクセストークン", r'(?i)(access[_-]?token|auth[_-]?token)'),
    ("GitHubトークン", r'(?i)gh[opsu]_[0-9a-zA-Z]{36}'), # Adjusted based on common formats
    ("GitHubトークン (Fine-grained)", r'(?i)github_pat_[0-9a-zA-Z_]{82}'), # Adjusted based on docs
    ("トークン", r'(?i)xox[baprs]-[0-9a-zA-Z]{10,48}'), # API token pattern
    ("一般的な機密情報", r'(?i)(password|secret|private[_-]?key)') # Added private key
]
```

**注意:** 上記の正規表現は一例であり、プロジェクトの要件や使用するサービスに応じて見直しや調整が必要です。特に長さや文字種の指定は、公式ドキュメントなどを参照して最新の状態に保つことが重要です。 