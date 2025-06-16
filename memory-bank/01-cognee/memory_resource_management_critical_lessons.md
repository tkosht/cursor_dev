# Cogneeメモリリソース管理 - 重大教訓

**作成日**: 2025-06-15  
**重要度**: ★★★★★ CRITICAL  
**問題**: Cognee大量登録によるメモリ消費異常（30GiB）

## 🚨 発生した重大問題

### 問題概要
- **発生日時**: 2025-06-15 22:17頃
- **原因**: memory-bank配下の複数ファイルを短時間で連続cognify
- **影響**: Cogneeサーバーが30GiBの仮想メモリを消費
- **症状**: システム全体のメモリ不足、パフォーマンス劣化

### 具体的な問題行動
```bash
# ❌ 危険な実行パターン（実際に行った誤った行動）
mcp__cognee__cognify --data /home/devuser/workspace/memory-bank/00-core/user_authorization_mandatory.md
mcp__cognee__cognify --data /home/devuser/workspace/memory-bank/00-core/testing_mandatory.md
mcp__cognee__cognify --data /home/devuser/workspace/memory-bank/00-core/code_quality_anti_hacking.md
mcp__cognee__cognify --data /home/devuser/workspace/memory-bank/00-core/development_workflow.md
mcp__cognee__cognify --data /home/devuser/workspace/memory-bank/00-core/tdd_implementation_knowledge.md
# ... 連続実行により30GiBメモリ消費
```

### 観測された異常
- **メモリ消費**: 30.9GiB仮想メモリ（通常の数百倍）
- **CPU使用率**: 101.5%（CPU集約的処理）
- **処理時間**: 19分以上の長時間処理
- **システム影響**: 利用可能メモリが62GiB → 22GiBまで減少

## 🛡️ 絶対禁止事項

### ❌ 絶対にやってはいけないこと
1. **短時間での複数ファイル連続cognify**
   ```bash
   # ❌ このような連続実行は禁止
   for file in memory-bank/**/*.md; do
       mcp__cognee__cognify --data "$file"  # 危険
   done
   ```

2. **大容量ファイルの無計画な一括登録**
   ```bash
   # ❌ 大きなディレクトリの一括処理は禁止
   mcp__cognee__cognify --data /home/devuser/workspace/memory-bank/
   ```

3. **メモリ消費監視なしでの長時間処理**
   ```bash
   # ❌ リソース監視なしでの実行は禁止
   mcp__cognee__cognify --data large_file.md  # 監視なし
   ```

4. **処理状況確認なしでの次ファイル登録**
   ```bash
   # ❌ cognify_statusチェックなしでの連続実行は禁止
   mcp__cognee__cognify --data file1.md
   mcp__cognee__cognify --data file2.md  # 前の処理完了待ちなし
   ```

## ✅ 安全な実行プロトコル

### 単一ファイル登録の安全手順
```bash
# ✅ 正しい単一ファイル登録手順
echo "=== Cognee安全登録プロトコル ==="

# 1. 事前リソース確認
echo "メモリ使用量確認:"
free -h

# 2. Cogneeステータス確認
echo "Cognee処理状況確認:"
mcp__cognee__cognify_status

# 3. 単一ファイル登録（小さなファイルから）
echo "ファイルサイズ確認:"
ls -lh target_file.md

# 4. 登録実行
echo "登録開始:"
mcp__cognee__cognify --data target_file.md

# 5. 処理完了まで待機（必須）
echo "処理完了待機中..."
while [ "$(mcp__cognee__cognify_status)" != "completed" ]; do
    echo "処理中... $(date)"
    sleep 30
    free -h  # メモリ監視
done

# 6. 成功確認
echo "登録確認:"
mcp__cognee__search --search_query "登録したファイル内容" --search_type "CHUNKS"
```

### 複数ファイル登録の安全手順
```bash
# ✅ 複数ファイルの安全な段階的登録
files=(
    "memory-bank/00-core/user_authorization_mandatory.md"
    "memory-bank/00-core/testing_mandatory.md"
    # 必要最小限のファイルのみ
)

for file in "${files[@]}"; do
    echo "=== $file 登録開始 ==="
    
    # ファイルサイズ確認
    echo "ファイルサイズ: $(ls -lh "$file" | awk '{print $5}')"
    
    # メモリ確認
    echo "登録前メモリ状況:"
    free -h
    
    # 登録実行
    mcp__cognee__cognify --data "$file"
    
    # 完了まで待機（重要）
    echo "処理完了待機中..."
    sleep 60  # 最低1分待機
    
    # メモリ状況再確認
    echo "登録後メモリ状況:"
    free -h
    
    # メモリ使用量チェック
    mem_used=$(free | awk 'NR==2{printf "%.1f", $3/$2*100}')
    if (( $(echo "$mem_used > 70.0" | bc -l) )); then
        echo "⚠️ メモリ使用率が${mem_used}%に達しました。処理を一時停止します。"
        echo "手動でメモリ状況を確認してから継続してください。"
        break
    fi
    
    echo "=== $file 登録完了 ==="
    echo "次のファイル処理まで追加待機..."
    sleep 120  # ファイル間で2分間隔
done
```

## 📊 リソース監視要件

### 必須監視項目
```bash
# 1. メモリ使用量監視
watch -n 10 'free -h'

# 2. Cogneeプロセス監視
watch -n 10 'ps aux | grep cognee | grep -v grep'

# 3. ディスク使用量監視
watch -n 30 'df -h'
```

### 緊急停止基準
- **メモリ使用率**: 70%を超えた場合は即座に停止
- **処理時間**: 5分以上応答がない場合は停止検討
- **CPU使用率**: 100%が10分以上継続する場合は停止

## 🔧 トラブルシューティング

### メモリ不足時の対処法
```bash
# 1. Cogneeプロセス確認
ps aux | grep cognee

# 2. 必要に応じてプロセス停止
# ⚠️ 注意: 処理中のデータ損失の可能性
pkill -f cognee

# 3. メモリクリア
sudo sync
sudo echo 3 > /proc/sys/vm/drop_caches

# 4. 再起動検討
# システム全体の再起動も検討
```

### 部分的回復手順
```bash
# 1. 処理済みファイル確認
mcp__cognee__search --search_query "user authorization" --search_type "CHUNKS"

# 2. 未処理ファイル特定
# 手動で確認し、リストアップ

# 3. 段階的再開
# 上記の安全手順に従って一つずつ再実行
```

## 📋 予防策チェックリスト

### 実行前チェック（必須）
- [ ] 対象ファイルサイズの確認（10MB以下推奨）
- [ ] 現在のメモリ使用率確認（50%以下推奨）
- [ ] Cogneeプロセス状況確認（アイドル状態）
- [ ] 処理時間の見積もり（1ファイル最大5分）

### 実行中監視（必須）
- [ ] メモリ使用率の継続監視
- [ ] CPU使用率の監視
- [ ] 処理完了状況の定期確認
- [ ] 異常発生時の即座停止準備

### 実行後確認（必須）
- [ ] 登録内容の検索確認
- [ ] メモリ使用量の正常化確認
- [ ] システム全体の動作確認
- [ ] 次回実行までの適切な間隔確保

## 🎯 推奨代替戦略

### 小規模段階的アプローチ
1. **必須ファイルのみ**: 5ファイル以下から開始
2. **1日1-2ファイル**: 毎日少しずつ追加
3. **週次バッチ**: 週末に3-5ファイルをまとめて処理
4. **月次メンテナンス**: 月1回の大規模整理

### 選択的登録戦略
```bash
# Phase 1: 絶対必須（3ファイル）
priority_1=(
    "memory-bank/00-core/user_authorization_mandatory.md"
    "memory-bank/00-core/testing_mandatory.md"
    "memory-bank/00-core/code_quality_anti_hacking.md"
)

# Phase 2: 高重要度（週次、5ファイル）
priority_2=(
    "memory-bank/00-core/development_workflow.md"
    "memory-bank/00-core/tdd_implementation_knowledge.md"
    "memory-bank/01-cognee/mandatory_utilization_rules.md"
    "memory-bank/01-cognee/knowledge_operations_manual.md"
    "memory-bank/06-project/context/active_context.md"
)

# Phase 3: 通常重要度（月次、残り）
```

## 📚 学習事項

### 重要な教訓
1. **Cogneeは軽量ツールではない**: 大量のメモリと処理時間を消費
2. **並列処理の危険性**: 複数ファイルの同時処理は制御不能なリソース消費
3. **監視の重要性**: リソース監視なしでの大規模操作は極めて危険
4. **段階的アプローチの必要性**: 一度に大量処理するのではなく段階的実行が必須

### 今後の方針
1. **保守的なアプローチ**: 常に最小限から開始
2. **十分な監視**: 各段階でのリソース確認
3. **十分な時間確保**: 処理時間の余裕を持った計画
4. **代替手段の準備**: ファイルシステム検索の併用維持

---

## 🚨 追加重大教訓（2025-06-16更新）

### 並列実行によるデッドロックリスク
**発生日時**: 2025-06-16 13:34頃  
**問題**: 複数ファイルの並列cognify実行による潜在的デッドロック

#### 危険な実行パターン
```bash
# ❌ 危険: 並列実行（デッドロックリスク）
mcp__cognee__cognify --data file1.md
mcp__cognee__cognify --data file2.md  # 前の処理が未完了時の並列実行
```

#### 症状・リスク
- 処理がハングアップする可能性
- メモリ消費の指数的増加
- システム全体の応答停止

#### 根本原因
- Cogneeの内部処理でファイル間の依存関係やロック機構
- バックグラウンド処理の競合状態
- メモリ共有リソースへの同時アクセス

### ✅ 絶対安全プロトコル（更新版）
```bash
# ✅ 正しい順次実行手順
echo "=== 順次登録プロトコル ==="

# 1. 単一ファイル登録
mcp__cognee__cognify --data file1.md

# 2. 【重要】完了確認まで待機
while [[ "$(mcp__cognee__cognify_status | grep -c 'DATASET_PROCESSING_COMPLETED')" -eq 0 ]]; do
    echo "処理中... $(date)"
    sleep 10
done

# 3. 動作確認
mcp__cognee__search --search_query "test query" --search_type "GRAPH_COMPLETION"

# 4. 次のファイル処理（必ず前のファイル完了後）
mcp__cognee__cognify --data file2.md
```

### 教訓・学習事項（追加）
1. **処理完了確認の絶対必要性**: `DATASET_PROCESSING_COMPLETED`確認は省略不可
2. **並列実行の完全禁止**: どんなに小さなファイルでも並列実行は危険
3. **ユーザー指摘の重要性**: 専門知識を持つユーザーからの警告は最優先
4. **不正確な提案の危険性**: 処理状況を正確に把握せずに次のアクションを提案するのは危険

---

**重要**: このドキュメントは実際に発生した重大問題の記録です。今後のCognee運用時には必ずこの教訓を参照し、安全なプロトコルに従ってください。メモリ不足によるシステム障害は、開発作業全体に深刻な影響を与える可能性があります。