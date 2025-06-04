# Git トラブルシューティングパターン

最終更新: 2025-06-04

## 📋 概要

Gitでファイルが表示されない、追加できない等の問題に対する体系的な調査手順とよくある原因をまとめたナレッジベース。

## 🔍 問題別調査フロー

### ファイルが `git status` で表示されない場合

#### 段階的調査手順
```bash
# 1. 無視されているファイルも含めて確認
git status --ignored

# 2. 具体的な無視ルールを特定（最重要）
git check-ignore --verbose <file_path>

# 3. 全無視ファイルの一覧表示
git ls-files --others --ignored --exclude-standard

# 4. 未追跡ファイルの明示的表示
git status --untracked-files=all
```

#### 調査対象の優先順位
1. **グローバル gitignore**: `~/.config/git/ignore`
2. **プロジェクト gitignore**: `./.gitignore`
3. **Git内部設定**: `.git/info/exclude`
4. **ファイル権限**: `ls -la` でアクセス権確認

### `git add` が失敗する場合

#### 典型的なエラーパターン
```bash
# エラー例
The following paths are ignored by one of your .gitignore files:
<file_path>
hint: Use -f if you really want to add them.

# 調査コマンド
git check-ignore --verbose <file_path>
```

#### 対処方法
1. **推奨**: 除外ルールの見直し・修正
2. **次善**: 必要に応じて `git add -f` で強制追加
3. **非推奨**: `--no-verify` での迂回

## 🛠️ よくある原因と解決策

### 1. グローバル gitignore による除外

**症状**: プロジェクトの `.gitignore` にルールがないのに無視される
**原因**: `~/.config/git/ignore` にルールが存在
**解決策**: 
```bash
# 確認
cat ~/.config/git/ignore

# 必要に応じて編集または --global 設定変更
git config --global core.excludesfile
```

### 2. Claude Code 固有の自動除外

**対象ファイル**: `.claude/settings.local.json`
**原因**: Claude Code が自動的にグローバル gitignore に追加
**理由**: セキュリティ配慮（API設定の漏洩防止）
**対処**: 
- 通常は除外されたままが望ましい
- 必要な場合のみ `git add -f` で強制追加

### 3. パターンマッチングの誤解

**例**: `.env*` パターンが `.environment` にもマッチ
**確認方法**: `git check-ignore --verbose` で詳細確認
**対処**: より具体的なパターンに修正

### 4. ディレクトリ権限問題

**症状**: `git add` がエラーなく終了するが何も追加されない
**確認方法**: `ls -la` でファイル権限確認
**対処**: `chmod` で適切な権限設定

## 🚨 重要な注意事項

### 1. --no-verify の使用禁止

```bash
# ❌ 禁止: 品質管理システムの迂回
git commit --no-verify

# ✅ 推奨: 根本原因の解決
git check-ignore --verbose <file>
# 原因特定後、適切な修正を実施
```

### 2. git check-ignore の活用

**最も確実な原因特定方法**:
```bash
# 詳細な無視理由を表示
git check-ignore --verbose <file_path>

# 出力例
/home/user/.config/git/ignore:1:**/.claude/settings.local.json	.claude/settings.local.json
#           ↑                    ↑                                    ↑
#    ファイルパス          行番号:パターン                    対象ファイル
```

### 3. 調査の記録

問題解決時は以下を記録：
- 問題の症状
- 実行したコマンドと結果
- 特定した原因
- 採用した解決策
- 予防策

## 📖 参考コマンド集

### 基本調査コマンド
```bash
# 全状態表示（無視ファイル含む）
git status --ignored --untracked-files=all

# 特定ファイルの無視理由
git check-ignore --verbose <file_path>

# 無視されているファイル一覧
git ls-files --others --ignored --exclude-standard

# gitignore ファイルの検索
find . -name ".gitignore" -type f

# グローバル設定確認
git config --global core.excludesfile
```

### 高度な調査コマンド
```bash
# 特定パターンがどのファイルに影響するかテスト
echo "<pattern>" | git check-ignore --stdin --verbose

# Git管理下の全ファイル表示
git ls-files

# 追跡されていない全ファイル
git ls-files --others
```

## 🔄 このナレッジの改善

新しいパターンや解決策を発見した場合：
1. この文書に追記
2. 具体的なコマンド例を含める
3. 実際の体験に基づく内容を優先
4. 最終更新日を更新

---

**作成背景**: `.claude/` ディレクトリが表示されない問題の調査過程で得られた知見をナレッジ化