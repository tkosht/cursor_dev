# テスト用キーファイル

## 本番キー（検出されるべき）
- OpenAI: [OPENAI_KEY_REDACTED]N
- Google: AIza1234567890abcdefghijklmnopqrstuvwxyz12345
- Slack Bot: [SLACK_TOKEN_REDACTED]
- Slack App: [SLACK_TOKEN_REDACTED]-abcdef1234567890abcdef1234567890

## テストキー（無視されるべき）
- OpenAI Test: sk-test-abcdefghijklmnopqrstuvwxyz123456789ABCDEFGHIJKLMN
- Google Test: AIza1234567890abcdefghijklmnopqrstuvwxyz12345_test
- Slack Test: xoxb-test-123456789012-abcdef

## コメント内のキー（無視されるべき）
<!-- [OPENAI_KEY_REDACTED]N -->
// AIza1234567890abcdefghijklmnopqrstuvwxyz12345
# [SLACK_TOKEN_REDACTED]

## テストデータ（無視されるべき）
test_api_key = "[OPENAI_KEY_REDACTED]N"
dummy_google_key = "[SENSITIVE_INFO_REDACTED]"
sample_slack_token = "[SLACK_TOKEN_REDACTED]" 