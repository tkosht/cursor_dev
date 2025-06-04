# Claude Code 固有動作パターン

最終更新: 2025-06-04

## 📋 概要

Claude Code（Anthropicの公式CLI）特有の動作、ファイル構成、自動設定について理解し、適切に対応するためのナレッジ。

## 🤖 Claude Code の基本理解

### 製品概要
- **提供元**: Anthropic
- **性質**: 公式CLI for Claude
- **目的**: コードとの統合的なAI開発環境
- **設計思想**: セキュリティファーストの開発者体験

### インストール場所・設定
```bash
# 一般的なインストール場所
/usr/local/bin/claude
~/.claude/

# グローバル設定ディレクトリ
~/.config/git/ignore  # Git設定への自動追加
```

## 🔒 自動セキュリティ設定

### グローバル gitignore の自動設定

**設定ファイル**: `~/.config/git/ignore`
**追加内容**:
```
**/.claude/settings.local.json
```

**設定理由**:
1. **API設定保護**: Claude APIキーや認証情報の漏洩防止
2. **個人設定分離**: ユーザー固有設定のリポジトリ混入防止
3. **セキュリティ事故予防**: 意図しない機密情報コミットの自動防止

### 影響範囲
- **全プロジェクト**: `**/.claude/settings.local.json` パターンで全リポジトリに適用
- **自動適用**: ユーザーが明示的に設定する必要なし
- **継続性**: Claude Code アップデート時も維持

## 📁 ファイル構成パターン

### .claude/ ディレクトリ構造
```
.claude/
├── settings.local.json    # ローカル設定（常に git ignore）
└── （その他の設定ファイル）
```

### settings.local.json の内容例
```json
{
  "apiSettings": {
    "anthropicApiKey": "sk-...",
    "modelPreferences": "claude-3-sonnet"
  },
  "userPreferences": {
    "defaultMode": "code",
    "autoSave": true
  },
  "localEnvironment": {
    "workspacePath": "/path/to/workspace",
    "customCommands": {...}
  }
}
```

## 🔍 トラブルシューティング

### `.claude/` が git status に表示されない

**原因**: グローバル gitignore による自動除外
**確認方法**:
```bash
# 詳細な除外理由を確認
git check-ignore --verbose .claude/settings.local.json

# 出力例
/home/user/.config/git/ignore:1:**/.claude/settings.local.json	.claude/settings.local.json
```

**対処法**:
```bash
# 1. 通常は除外されたままが推奨（セキュリティ上）

# 2. 必要な場合は強制追加
git add -f .claude/settings.local.json

# 3. 個別設定で除外を無効化（非推奨）
git config core.excludesfile ""
```

### 設定ファイルの管理

**推奨アプローチ**:
1. **個人設定は除外**: `settings.local.json` は git ignore のまま
2. **チーム共有設定**: 別ファイル（例：`.claude/team-config.json`）で管理
3. **テンプレート提供**: 初期設定用の `settings.example.json` を用意

**設定管理例**:
```bash
# チーム共有可能な設定例
.claude/
├── settings.local.json      # git ignored（個人設定）
├── settings.example.json    # テンプレート（git tracked）
└── team-config.json         # チーム共有設定（git tracked）
```

## ⚙️ 設定カスタマイズ

### グローバル ignore の調整

**現在の設定確認**:
```bash
# グローバル gitignore の場所確認
git config --global core.excludesfile

# 内容確認
cat ~/.config/git/ignore
```

**カスタマイズ例**:
```bash
# 特定ファイルのみ除外解除（チーム設定用）
!.claude/team-config.json
!.claude/README.md
```

### プロジェクト固有の設定

**プロジェクトの `.gitignore` での上書き**:
```gitignore
# Claude Code設定の個別管理
!.claude/
.claude/settings.local.json  # 個人設定のみ除外
```

## 🛡️ セキュリティ配慮

### 保護すべき情報
- **APIキー**: Claude API認証情報
- **個人設定**: ユーザー固有の作業環境設定
- **履歴情報**: 過去のセッション記録

### セキュリティベストプラクティス
1. **デフォルト設定尊重**: 自動 gitignore を維持
2. **定期的確認**: 意図しない設定ファイルのコミットチェック
3. **チーム教育**: Claude Code 設定管理の理解促進

### 監査・確認方法
```bash
# 意図しない設定ファイルのコミット確認
git log --oneline --grep=".claude" --all

# 現在のリポジトリでの除外状況確認
git ls-files --others --ignored --exclude-standard | grep claude
```

## 🔄 業界動向との整合性

### 類似ツールとの比較

| ツール | 設定ディレクトリ | Git除外方法 |
|--------|------------------|-------------|
| VS Code | `.vscode/` | 手動設定が一般的 |
| JetBrains | `.idea/` | 手動設定が一般的 |
| Claude Code | `.claude/` | **自動設定** |

**Claude Code の優位性**:
- **セキュリティファースト**: 自動的な保護設定
- **ユーザビリティ**: 手動設定の手間削減
- **事故防止**: デフォルトで安全な状態

## 📚 開発者向けガイドライン

### 新規プロジェクトでの対応
1. **確認**: `.claude/` の除外状況チェック
2. **理解**: チームメンバーへの動作説明
3. **文書化**: プロジェクト README での注意事項記載

### 既存プロジェクトでの対応
1. **監査**: 既存コミットでの設定ファイル混入確認
2. **クリーンアップ**: 必要に応じて履歴から除去
3. **ルール策定**: 今後の管理方針決定

### チーム開発での配慮
```markdown
## Claude Code 使用時の注意事項

- `.claude/settings.local.json` は自動的に git ignore されます
- 個人設定は各自で管理してください
- チーム共有が必要な設定は別ファイルで管理します
```

## 🔄 将来的な考慮事項

### 想定される変更
- **新しい設定ファイル**: Claude Code アップデートでの追加
- **除外パターン変更**: セキュリティ要件に応じた調整
- **統合機能拡張**: 他のツールとの連携強化

### 対応準備
- **定期確認**: `.config/git/ignore` の内容チェック
- **ナレッジ更新**: 新機能に応じた文書更新
- **チーム共有**: 変更点の適切な伝達

---

**作成背景**: `.claude/settings.local.json` が表示されない問題の調査過程で判明した Claude Code の自動セキュリティ設定について、その設計思想と適切な対応方法をナレッジ化