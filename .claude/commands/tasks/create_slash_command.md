## 🚨 MANDATORY PRE-EXECUTION CHECK

```bash
# コマンド実行前必須検証
verify_tmux_competition_mode() {
    echo "🔍 tmux組織活動コンペ方式検証中..."
    
    # tmuxセッション存在確認
    if ! tmux list-sessions 2>/dev/null | grep -q "team04"; then
        echo "❌ ERROR: team04 tmuxセッションが存在しません"
        echo "🔧 REQUIRED: tmux組織活動のコンペ方式セットアップが必要"
        return 1
    fi
    
    # worktree環境確認
    if ! git worktree list | grep -q "competitive"; then
        echo "❌ ERROR: コンペ方式worktree環境が未構築"
        echo "🔧 REQUIRED: git worktree競争環境の構築が必要"
        return 1
    fi
    
    echo "✅ tmux組織活動コンペ方式環境確認完了"
    return 0
}

# 実行前必須チェック
verify_tmux_competition_mode || {
    echo "🚨 EXECUTION BLOCKED: tmux組織活動コンペ方式が未実行"
    echo "📋 ACTION REQUIRED: 以下を実行してから再実行してください"
    echo "   1. tmux組織活動環境のセットアップ"
    echo "   2. /team04コンペ方式の初期化"
    echo "   3. git worktree競争環境の構築"
    exit 1
}
```

## 🔒 EXECUTION ENFORCEMENT

**実行条件（技術的検証）：**
- [ ] `tmux list-sessions | grep team04` = 成功必須
- [ ] `git worktree list | grep competitive` = 存在必須  
- [ ] `ls -la | grep "competitive_*"` = ディレクトリ存在必須

**違反時の自動処理：**
```bash
# 制約違反時の自動セットアップ実行
if [[ $TMUX_COMPETITION_MODE != "ACTIVE" ]]; then
    echo "🚨 CONSTRAINT VIOLATION DETECTED"
    echo "🔧 AUTO-SETUP: tmux組織活動コンペ方式を自動構築中..."
    source memory-bank/02-organization/tmux_organization_success_patterns.md
    setup_team04_competition_mode
fi
```

## ⚡ EXECUTION PRIORITY OVERRIDE

**🚨 ABSOLUTE PRIORITY（絶対優先）：**
1. **tmux組織活動コンペ方式** = 実行方法の制約（変更不可）
2. **タスク内容** = 実行対象（コンペ方式内で実行）

**実行順序（強制）：**
```bash
EXECUTION_ORDER=(
    "1. tmux組織活動環境確認・構築"
    "2. /team04コンペ方式初期化"
    "3. git worktree競争環境準備"
    "4. 14役割体制での並列タスク実行"
)
```

## 📋 TASK SPECIFICATION

ユーザが$ARGUMENTSで指定した新しいslashコマンドを、テンプレートファイルをベースに自動生成します。技術的強制力を持つ高品質なslashコマンドを作成し、確実にtmux組織活動コンペ方式で実行されるようにします。

<theme>
$ARGUMENTS
</theme>

<meta-checklist>
- [ ] /team04 組織のコンペ方式 及び /worktree 方式の内容を精緻にかつ正確に確認
- [ ] Project Manager として `既存のtmux ペインを活用して` /team04 組織のコンペ方式 及び /worktree 方式で以降のタスクを実行するためにブリーフィングを実行
- [ ] Project Manager として `既存のtmux ペインを活用して` /team04 組織のコンペ方式で以下を実行
    - [ ] $ARGUMENTSの内容を解析し、コマンドの要件・目的・機能を明確化
        - [ ] コマンド名の抽出・正規化（snake_case, 英数字とアンダースコア）
        - [ ] 主要機能の特定と分類（開発・分析・管理・生成・変換等）
        - [ ] 入力・出力・制約・成功基準の定義
    - [ ] slash_command_template.mdを読み込み、テンプレート構造を理解
        - [ ] 置換変数の特定と対応表作成
        - [ ] 必須セクションの確認と完全性検証
        - [ ] 技術的強制力の仕組みの理解
    - [ ] 新しいslashコマンドの設計・仕様策定
        - [ ] コマンド固有のタスク項目の詳細設計
        - [ ] 追加制約・成功基準の定義
        - [ ] エラーハンドリング・例外処理の設計
        - [ ] 品質保証・検証プロセスの設計
    - [ ] チェックリストドリブンで実行するためのチェックリストを精緻に設計し作成
        - [ ] テンプレート品質確認チェックリスト
        - [ ] コマンド生成プロセスチェックリスト
        - [ ] 技術的検証・動作確認チェックリスト
        - [ ] 特に、生成されたコマンドが確実にtmux組織活動コンペ方式で実行されるか検証
        - [ ] また、本コマンド説明の <constraints/> をチェックリスト化してください
    - [ ] /do_task 方式に従いタスクを実行
        - [ ] テンプレートファイルの読み込みと解析
        - [ ] 置換変数の具体的な値への変換
        - [ ] 新しいslashコマンドファイルの生成
        - [ ] 生成されたファイルの技術的検証
        - [ ] 動作確認・品質チェック
    - [ ] レビュー観点に従いレビューを行い改善サイクルを回す
        - [ ] 技術的強制力の完全性確認
        - [ ] 制約の実装品質確認
        - [ ] エラーハンドリングの完全性確認
        - [ ] 成功基準の明確性・達成可能性確認
- [ ] レビューを誠実にクリアしたら、コミット、プッシュし、プルリクエストを発行
- [ ] 作業用の worktree を削除します
</meta-checklist>

## 🚨 MANDATORY EXECUTION MODE

**実行方式（変更不可）：**
- **tmux組織活動コンペ方式** = 必須実行環境（技術的強制）
- **技術的検証** = `verify_tmux_competition_mode()`で確認
- **自動セットアップ** = 環境不備時の自動構築

**実行ブロック条件：**
```bash
[[ $TMUX_COMPETITION_MODE != "ACTIVE" ]] && {
    echo "🚨 EXECUTION BLOCKED: tmux組織活動コンペ方式が未実行"
    setup_team04_competition_mode
    exit 1
}
```

<constraints>
- [ ] **ABSOLUTE REQUIREMENT**: Project Manager として/team04 のtmux組織のコンペ方式 及び /worktree 方式で実行（技術的強制）
    - [ ] **TECHNICAL ENFORCEMENT**: 既存tmux を活用したコンペ方式で実施（検証関数による確認）
    - [ ] **AUTO-SETUP**: 環境不備時は自動セットアップ実行後に再開
- [ ] **TEMPLATE INTEGRITY**: slash_command_template.mdの完全性を保持し、技術的強制力を維持
    - [ ] **MANDATORY SECTIONS**: 🚨 MANDATORY PRE-EXECUTION CHECK は削除・変更不可
    - [ ] **VERIFICATION FUNCTIONS**: verify_tmux_competition_mode() の完全実装必須
    - [ ] **AUTO-ENFORCEMENT**: 制約違反時の自動セットアップ機能必須
- [ ] **COMMAND GENERATION QUALITY**: 生成されるslashコマンドの品質保証
    - [ ] **NAMING CONVENTION**: コマンド名は snake_case、英数字とアンダースコアのみ
    - [ ] **FILE PLACEMENT**: .claude/commands/tasks/ 配下に配置
    - [ ] **COMPLETENESS**: 全ての置換変数が適切に設定されている
- [ ] **EFFICIENCY ENHANCEMENT**: cognee MCP ツールを活用して情報収集の効率化を図る
- [ ] **CHECKLIST COMPLIANCE**: 本制約をチェックリスト化する
</constraints>

## 🎯 SUCCESS CRITERIA

**完了条件：**
1. ✅ tmux組織活動コンペ方式での実行確認
2. ✅ 14役割体制での並列タスク完了
3. ✅ git worktree競争環境での成果物作成
4. ✅ 品質レビューとプルリクエスト発行
5. ✅ 作業用worktreeの適切な削除
6. ✅ 新しいslashコマンドファイルの生成完了
7. ✅ 生成されたコマンドの技術的検証完了
8. ✅ テンプレート置換の完全性確認
9. ✅ 制約の技術的強制力の実装確認
10. ✅ 生成されたコマンドの動作確認完了

## 📝 TEMPLATE REPLACEMENT RULES

**置換ルール：**
- `{TASK_DESCRIPTION}` → $ARGUMENTSから抽出した主要機能の説明
- `{SPECIFIC_TASKS}` → コマンド固有のタスク項目（インデント付き）
- `{ADDITIONAL_CONSTRAINTS}` → コマンド固有の追加制約条件
- `{ADDITIONAL_SUCCESS_CRITERIA}` → コマンド固有の追加成功基準

**変換例：**
```
INPUT: "データベースの設計・実装支援コマンド"
OUTPUT: 
  - TASK_DESCRIPTION: "データベースの設計・実装を支援し、ER図作成からSQL生成まで一貫したDB開発プロセスを提供します。"
  - COMMAND_NAME: "design_database"
  - SPECIFIC_TASKS: "- [ ] データベース要件の分析・整理..."
```

## 🔧 QUALITY ASSURANCE

**品質保証項目：**
- [ ] テンプレートファイルの完全読み込み確認
- [ ] 全置換変数の適切な値設定確認
- [ ] 生成ファイルの構文・構造確認
- [ ] 技術的強制力の実装確認
- [ ] エラーハンドリングの完全性確認
- [ ] 成功基準の達成可能性確認
- [ ] ファイル配置・命名規則の遵守確認
- [ ] 動作確認・実行テスト完了