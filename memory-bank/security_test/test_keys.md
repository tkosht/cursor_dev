# テスト用キーファイル

## 本番キー（検出されるべき）
- OpenAI: [OPENAI_KEY_REDACTED]
- Google: AIza1234567890abcdefghijklmnopqrstuvwxyz12345
- Slack Bot: [SLACK_TOKEN_REDACTED]
- Slack App: [SLACK_TOKEN_REDACTED]

## テストキー（無視されるべき）
- OpenAI Test: [OPENAI_KEY_REDACTED]
- Google Test: AIza1234567890abcdefghijklmnopqrstuvwxyz12345_test
- Slack Test: xoxb-test-123456789012-abcdef

## コメント内のキー（無視されるべき）
<!-- [OPENAI_KEY_REDACTED] -->
// AIza1234567890abcdefghijklmnopqrstuvwxyz12345
# [SLACK_TOKEN_REDACTED]

## テストデータ（無視されるべき）
test_[API_KEY_REDACTED]"
dummy_google_[SENSITIVE_INFO_REDACTED]"
sample_slack_token = "[SLACK_TOKEN_REDACTED]" 