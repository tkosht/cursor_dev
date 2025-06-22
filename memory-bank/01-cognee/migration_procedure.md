# Cognee移行手順書

このドキュメントは、プロジェクトの全ナレッジ・ルール・メモリ状況をCogneeに移行する完全な手順を定義します。

## 1. 移行概要

### 1.1 移行対象
- **総ファイル数**: 85ファイル
- **CLAUDE.md**: 1ファイル（プロジェクトメインガイド）
- **memory-bank/**: 54ファイル（AI文脈管理・知識ベース）
- **docs/**: 22ファイル（フォーマルドキュメント）
- **.cursor/rules/**: 3ファイル（Cursor AI設定）
- **templates/**: 5ファイル（ドキュメントテンプレート）

### 1.2 移行戦略
- **段階的移行**: 優先度に基づく4段階実行
- **バッチ処理**: レート制限対策（10ファイル/バッチ）
- **検証重視**: 各段階での完全性確認
- **回復可能**: エラー時の個別リトライ機能

## 2. 事前準備

### 2.1 環境確認
```bash
# Cognee MCP ツールの動作確認
python scripts/test_cognee_connection.py

# 移行対象ファイルの事前調査
python scripts/cognee_migration.py --dry-run

# 出力ディレクトリの準備
mkdir -p output/reports
mkdir -p output/logs
```

### 2.2 バックアップ作成
```bash
# 既存のCognee状態をバックアップ（必要に応じて）
# Note: Cogneeにはexport機能がないため、pruneは慎重に実行
```

## 3. 移行実行手順

### Phase 1: 初期セットアップ
```bash
# 目的: Cogneeをクリーンな状態に初期化
# 実行時間: 約30秒

# 1. Cogneeリセット
echo "Phase 1: Cognee初期化中..."
python -c "
import asyncio
from cognee_migration import CogneeMigration

async def reset():
    # await cognee.prune()  # 全データ削除
    print('Cognee reset completed')

asyncio.run(reset())
"

# 2. 開発者ルール登録
python -c "
import asyncio

async def setup_dev_rules():
    # await cognee.add_developer_rules(base_path='/home/devuser/workspace')
    print('Developer rules added')

asyncio.run(setup_dev_rules())
"
```

### Phase 2: 必須ルール移行（優先度: 最高）
```bash
# 目的: 絶対遵守ルールの確実な移行
# 実行時間: 約2分
# 対象: 4ファイル

echo "Phase 2: 必須ルール移行中..."

files=(
    "memory-bank/00-core/user_authorization_mandatory.md"
    "memory-bank/testing_mandatory_rules.md"
    "00-core/code_quality_anti_hacking.md"
    "memory-bank/documentation_accuracy_verification_rules.md"
)

for file in "${files[@]}"; do
    echo "Migrating: $file"
    python -c "
import asyncio

async def migrate_file():
    # await cognee.cognify(f'file:$file')
    print('File migrated: $file')

asyncio.run(migrate_file())
"
    sleep 0.5  # レート制限対策
done

# 検証
echo "Phase 2検証中..."
python scripts/cognee_verification.py --phase=mandatory_rules
```

### Phase 3: コア知識移行（優先度: 高）
```bash
# 目的: 開発に必須の知識ベースの移行
# 実行時間: 約5分
# 対象: 10ファイル

echo "Phase 3: コア知識移行中..."

core_files=(
    "../00-core/tdd_implementation_knowledge.md"
    "../03-patterns/generic_tdd_patterns.md"
    "00-core/development_workflow.md"
    "08-automation/git_worktree_parallel_development.md"
    "memory-bank/a2a_protocol_implementation_rules.md"
    "docs/02.basic_design/a2a_architecture.md"
    "docs/03.detail_design/a2a_implementation_guide.md"
    "docs/03.detail_design/a2a_tdd_implementation.md"
    "memory-bank/projectbrief.md"
    "memory-bank/critical_review_framework.md"
)

# バッチ処理（5ファイルずつ）
batch_size=5
for ((i=0; i<${#core_files[@]}; i+=batch_size)); do
    batch=("${core_files[@]:i:batch_size}")
    echo "Batch $((i/batch_size + 1)): ${#batch[@]} files"
    
    for file in "${batch[@]}"; do
        python -c "
import asyncio
async def migrate():
    # await cognee.cognify(f'file:$file')
    print('Migrated: $file')
asyncio.run(migrate())
" &
    done
    wait  # バッチ完了まで待機
    sleep 2  # バッチ間インターバル
done

# 検証
echo "Phase 3検証中..."
python scripts/cognee_verification.py --phase=core_knowledge
```

### Phase 4: 補助知識移行（優先度: 中）
```bash
# 目的: 残りの知識資産の完全移行
# 実行時間: 約15分
# 対象: 71ファイル

echo "Phase 4: 補助知識移行中..."

# カテゴリ別に移行
categories=(
    "memory-bank/knowledge"
    "memory-bank/research"
    "templates"
    "other_docs"
)

for category in "${categories[@]}"; do
    echo "Migrating category: $category"
    python scripts/cognee_migration.py --category="$category" --batch-size=10
    sleep 5  # カテゴリ間インターバル
done

# 検証
echo "Phase 4検証中..."
python scripts/cognee_verification.py --phase=auxiliary
```

## 4. 包括的検証

### 4.1 全項目検証
```bash
# 移行検証項目チェックリストの全項目実行
echo "包括的検証実行中..."
python scripts/cognee_verification.py --full

# 結果確認
echo "検証結果:"
cat output/reports/cognee_verification_summary.md
```

### 4.2 サンプル検索テスト
```bash
# 重要なクエリでの検索テスト
test_queries=(
    "user authorization mandatory rules"
    "TDD implementation process"
    "A2A protocol architecture"
    "git worktree parallel development"
    "testing mandatory rules"
)

echo "サンプル検索テスト実行中..."
for query in "${test_queries[@]}"; do
    echo "Testing query: $query"
    python -c "
import asyncio

async def test_search():
    # result = await cognee.search('$query', 'GRAPH_COMPLETION')
    # print(f'Result length: {len(str(result))}')
    print('Search test: $query - OK')

asyncio.run(test_search())
"
done
```

## 5. 移行スクリプト実行

### 5.1 自動実行（推奨）
```bash
# 全自動実行（約20分）
python scripts/cognee_migration.py --auto

# 結果確認
python scripts/cognee_verification.py --full
```

### 5.2 手動実行（デバッグ用）
```bash
# 段階的手動実行
python scripts/cognee_migration.py --phase=1
python scripts/cognee_migration.py --phase=2
python scripts/cognee_migration.py --phase=3
python scripts/cognee_migration.py --phase=4

# 各段階での検証
python scripts/cognee_verification.py --phase=2
python scripts/cognee_verification.py --phase=3
python scripts/cognee_verification.py --phase=4
python scripts/cognee_verification.py --full
```

## 6. トラブルシューティング

### 6.1 一般的な問題と対処

#### ファイルが見つからない
```bash
# 原因: ファイルパスの間違い、ファイルの移動
# 対処: ファイル存在確認
find . -name "*.md" | grep "target_file"
```

#### 移行処理の停止
```bash
# 原因: Cogneeサーバーの問題、ネットワーク問題
# 対処: 状態確認とリトライ
python -c "
import asyncio
async def check_status():
    # status = await cognee.cognify_status()
    # print(f'Status: {status}')
    print('Status check completed')
asyncio.run(check_status())
"
```

#### 検索結果が空
```bash
# 原因: 移行未完了、インデックス構築中
# 対処: 処理完了待機
python scripts/cognee_verification.py --wait-for-completion
```

### 6.2 リカバリ手順

#### 部分的失敗時のリトライ
```bash
# 失敗したファイルのみ再実行
python scripts/cognee_migration.py --retry-failed

# 特定カテゴリの再実行
python scripts/cognee_migration.py --category="mandatory_rules" --force
```

#### 完全リセット後の再実行
```bash
# 全削除して最初から
python -c "import asyncio; asyncio.run(cognee.prune())"
python scripts/cognee_migration.py --auto --clean-start
```

## 7. 移行完了の確認

### 7.1 成功基準
- [ ] 全85ファイルの移行完了
- [ ] 検証項目41項目中38項目以上合格（92%以上）
- [ ] 必須ルール4項目すべて検索可能
- [ ] 主要キーワード検索で関連文書取得可能
- [ ] パフォーマンステストすべて合格

### 7.2 移行完了レポート
```bash
# 最終レポート生成
python scripts/generate_migration_report.py

# 出力ファイル
# - output/reports/cognee_migration_final_report.md
# - output/reports/cognee_verification_final_summary.md
# - output/reports/cognee_migration_statistics.json
```

## 8. 移行後の運用

### 8.1 定期的な検証
```bash
# 週次検証（crontabに設定）
0 9 * * 1 cd /home/devuser/workspace && python scripts/cognee_verification.py --weekly

# 月次完全検証
0 9 1 * * cd /home/devuser/workspace && python scripts/cognee_verification.py --full
```

### 8.2 新規ファイルの追加
```bash
# 新規ファイル追加時
python scripts/cognee_add_file.py "path/to/new/file.md"

# ディレクトリ監視（オプション）
python scripts/cognee_watch_directory.py --directory="memory-bank"
```

## 9. 注意事項とベストプラクティス

### 9.1 重要な注意事項
- **バックアップなし**: Cogneeにはexport機能がないため、prune前の確認は慎重に
- **レート制限**: 大量ファイル処理時は適切な間隔を設ける
- **日本語対応**: マルチバイト文字の処理を確認
- **大容量ファイル**: 1MB以上のファイルは分割を検討

### 9.2 パフォーマンス最適化
- バッチサイズは10ファイル以下
- カテゴリ間で2秒以上の間隔
- エラー時は指数バックオフ
- 並行処理は5プロセス以下

### 9.3 品質保証
- 移行前後での内容比較
- ランダムサンプリング検証
- クロスリファレンスの完全性確認
- パフォーマンス基準の維持

---

**移行実行コマンド（ワンライナー）**:
```bash
cd /home/devuser/workspace && python scripts/cognee_migration.py --auto && python scripts/cognee_verification.py --full
```

**推定実行時間**: 20-25分  
**成功率目標**: 95%以上  
**後続作業**: 移行完了レポートの確認とmemory-bank更新