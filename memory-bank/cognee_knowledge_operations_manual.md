# Cogneeナレッジ運用手順書

## 📋 概要

このドキュメントは、プロジェクトにおけるCogneeナレッジシステムの正式運用手順を定義します。従来のファイルベース知識管理（memory-bank/, docs/, .cursor/rules）からCogneeベースへの移行と日常運用を支援します。

## 🎯 **運用基本方針**

### **1. Cognee-First原則**
- すべての知識アクセスはCogneeから開始
- ファイルベースは段階的廃止対象
- 新規知識はCogneeに直接追加

### **2. 段階的移行方針**
- **Phase 1 (2-4週間)**: Cognee + ファイル併用
- **Phase 2 (2-3週間)**: Cognee主体、ファイル補完
- **Phase 3 (運用開始)**: Cognee単独運用

### **3. 品質保証原則**
- 知識の正確性を最優先
- 継続的な検証と改善
- エラー時の迅速な対応

## 🔍 **日常運用手順**

### **A. 知識の検索・取得**

#### **1. 基本検索パターン**
```python
# 必須ルールの確認
cognee.search("user authorization mandatory rules", "GRAPH_COMPLETION")
cognee.search("testing mandatory rules", "GRAPH_COMPLETION")

# 開発知識の取得
cognee.search("TDD implementation patterns", "GRAPH_COMPLETION")
cognee.search("What are the main development workflows?", "GRAPH_COMPLETION")

# プロジェクト固有知識
cognee.search("A2A protocol implementation", "GRAPH_COMPLETION")
```

#### **2. 検索タイプの使い分け**
- **GRAPH_COMPLETION**: 包括的な回答、要約、ガイダンス
- **INSIGHTS**: 概念間の関係性、知識構造の理解
- **CHUNKS**: 特定ファイルの内容、詳細情報

#### **3. 検索クエリのベストプラクティス**
```python
# ✅ 効果的なクエリ例
"What are the mandatory security rules for this project?"
"How should I implement TDD in this codebase?"
"A2A protocol implementation guidelines"

# ❌ 避けるべきクエリ例
"help"  # 曖昧すぎる
"file.md"  # ファイル名のみ
"code"  # 汎用的すぎる
```

### **B. 知識の追加・更新**

#### **1. 新規知識の追加手順**
```python
# Step 1: 知識の準備
new_knowledge = """
# 新しい開発ルール
## 概要
...具体的な内容...
## 適用範囲
...
## 実装例
...
"""

# Step 2: Cogneeに追加
cognee.cognify(new_knowledge)

# Step 3: 追加確認
status = cognee.cognify_status()
print(f"処理状況: {status}")

# Step 4: 検索テスト
result = cognee.search("新しい開発ルール", "GRAPH_COMPLETION")
print(f"追加確認: {result}")
```

#### **2. 既存知識の更新手順**
```python
# Step 1: 現在の知識確認
current = cognee.search("更新対象の知識", "CHUNKS")

# Step 2: 更新内容の準備
updated_knowledge = """
# 更新された知識
...新しい内容...
"""

# Step 3: 追加（Cogneeは重複を自動統合）
cognee.cognify(updated_knowledge)

# Step 4: 更新確認
result = cognee.search("更新対象の知識", "GRAPH_COMPLETION")
```

### **C. トラブルシューティング**

#### **1. 権限エラーの対処**
```python
# エラー検出
try:
    cognee.cognify("test content")
except PermissionDeniedError:
    # 即座にリセット
    cognee.prune()
    cognee.add_developer_rules()
    # 再試行
    cognee.cognify("test content")
```

#### **2. 検索結果が空の場合**
```python
# Step 1: 処理状況確認
status = cognee.cognify_status()

# Step 2: 処理完了待機
if status != "COMPLETED":
    print("処理中です。しばらく待ってから再試行してください。")

# Step 3: 代替検索
alternative_results = cognee.search("関連キーワード", "CHUNKS")
```

#### **3. 知識の品質問題**
```python
# Step 1: 複数タイプでの検索確認
graph_result = cognee.search("問題の知識", "GRAPH_COMPLETION")
insights_result = cognee.search("問題の知識", "INSIGHTS")
chunks_result = cognee.search("問題の知識", "CHUNKS")

# Step 2: ファイルベースでの照合（移行期間中）
# 必要に応じてファイル参照で確認

# Step 3: 問題報告と修正
# プロジェクトチームに報告し、知識の再追加
```

## 📊 **品質保証プロセス**

### **1. 日次品質チェック**
```python
# 必須項目の確認
daily_checks = [
    ("user authorization mandatory rules", "GRAPH_COMPLETION"),
    ("testing mandatory rules", "GRAPH_COMPLETION"),
    ("A2A protocol implementation", "GRAPH_COMPLETION"),
    ("TDD implementation patterns", "GRAPH_COMPLETION")
]

for query, search_type in daily_checks:
    result = cognee.search(query, search_type)
    if not result or "not contain information" in result:
        print(f"⚠️ 知識不足: {query}")
    else:
        print(f"✅ 正常: {query}")
```

### **2. 週次総合検証**
```python
# 包括的検証
weekly_verification = [
    "What are all the mandatory rules in this project?",
    "Explain the complete development workflow",
    "What are the main architectural patterns?",
    "List all security requirements"
]

for query in weekly_verification:
    result = cognee.search(query, "GRAPH_COMPLETION")
    # 結果の妥当性を手動確認
    print(f"検証結果: {query}")
    print(f"回答: {result[:200]}...")
```

### **3. 知識整合性チェック**
```python
# 関係性の確認
integrity_checks = [
    ("mandatory rules authorization testing", "INSIGHTS"),
    ("TDD development workflow relationship", "INSIGHTS"),
    ("security patterns implementation", "INSIGHTS")
]

for query, search_type in integrity_checks:
    relationships = cognee.search(query, search_type)
    # 関係性の論理的整合性を確認
```

## 🔄 **移行期間中の運用**

### **Phase 1: 併用期間**

#### **標準ワークフロー**
1. **Cogneeで検索**: 最初にCogneeから知識取得
2. **ファイルで補完**: Cogneeに不足があればファイル参照
3. **Cogneeに追加**: ファイルから得た知識をCogneeに追加
4. **検証**: 追加した知識の正確性確認

```python
# 併用期間の標準手順
def get_knowledge_hybrid(topic):
    # Step 1: Cognee検索
    cognee_result = cognee.search(topic, "GRAPH_COMPLETION")
    
    if cognee_result and "not contain information" not in cognee_result:
        return cognee_result
    
    # Step 2: ファイルベース検索（fallback）
    print(f"Cogneeに{topic}の情報が不足。ファイルを確認中...")
    # ファイル参照処理
    
    # Step 3: 不足知識のCognee追加
    # 必要に応じて知識追加
    
    return "併用検索完了"
```

### **Phase 2: 移行期間**

#### **ファイル参照削減**
- Cognee知識の網羅性確認
- ファイル参照の段階的削減
- 知識ギャップの特定と埋め合わせ

### **Phase 3: Cognee単独運用**

#### **ファイルベース廃止準備**
- 全知識のCognee移行完了確認
- ファイルベースシステムの段階的無効化
- 新規メンバーのCogneeオンボーディング

## 📈 **パフォーマンス監視**

### **1. 応答時間の監視**
```python
import time

def monitor_search_performance(query, search_type):
    start_time = time.time()
    result = cognee.search(query, search_type)
    end_time = time.time()
    
    response_time = end_time - start_time
    if response_time > 5.0:
        print(f"⚠️ 応答遅延: {response_time:.2f}秒 - {query}")
    else:
        print(f"✅ 正常応答: {response_time:.2f}秒 - {query}")
    
    return result
```

### **2. 知識カバレッジの監視**
```python
# 重要知識の存在確認
coverage_items = [
    "mandatory rules",
    "development workflows", 
    "A2A protocol",
    "TDD patterns",
    "security requirements",
    "quality standards"
]

coverage_score = 0
for item in coverage_items:
    result = cognee.search(item, "GRAPH_COMPLETION")
    if result and "not contain information" not in result:
        coverage_score += 1

print(f"知識カバレッジ: {coverage_score}/{len(coverage_items)} ({coverage_score/len(coverage_items)*100:.1f}%)")
```

## 🎓 **チーム教育・トレーニング**

### **1. 新規メンバーのオンボーディング**
```python
# 必須知識の段階的学習
onboarding_sequence = [
    ("プロジェクト概要", "What is this project about and what are its main goals?"),
    ("必須ルール", "What are all the mandatory rules I must follow?"),
    ("開発手法", "What development methodologies and patterns should I use?"),
    ("アーキテクチャ", "Explain the system architecture and design patterns"),
    ("品質基準", "What are the quality standards and review processes?")
]

for topic, query in onboarding_sequence:
    print(f"\n📚 学習トピック: {topic}")
    result = cognee.search(query, "GRAPH_COMPLETION")
    print(f"内容: {result}")
```

### **2. 既存メンバーの移行サポート**
- Cognee検索手法のトレーニング
- ファイルベースからの移行支援
- 知識追加・更新の実践指導

## 🔧 **運用ツールとスクリプト**

### **1. 日次運用スクリプト**
```bash
#!/bin/bash
# daily_cognee_check.sh

echo "=== Cognee日次チェック ==="
python3 -c "
import cognee_operations
cognee_operations.daily_quality_check()
cognee_operations.performance_monitor()
cognee_operations.knowledge_coverage_check()
"
```

### **2. 知識追加ヘルパー**
```python
# add_knowledge_helper.py
def add_knowledge_safely(content, category="general"):
    try:
        # 事前チェック
        status = cognee.cognify_status()
        if "ERROR" in str(status):
            cognee.prune()
            cognee.add_developer_rules()
        
        # 知識追加
        cognee.cognify(content)
        
        # 確認
        time.sleep(2)
        verification = cognee.search(content[:50], "CHUNKS")
        if verification:
            print(f"✅ 知識追加成功: {category}")
        else:
            print(f"⚠️ 知識追加要確認: {category}")
            
    except Exception as e:
        print(f"❌ 知識追加失敗: {str(e)}")
        # エラー報告とリトライ処理
```

## 📝 **運用ログとレポート**

### **1. 日次運用ログ**
- 検索クエリ実行回数
- 知識追加・更新件数
- エラー発生回数と内容
- パフォーマンス指標

### **2. 週次品質レポート**
- 知識カバレッジスコア
- 検索精度評価
- ユーザーフィードバック集計
- 改善提案事項

### **3. 月次戦略レビュー**
- 移行進捗状況
- ROI評価
- 次月改善計画
- 他プロジェクト展開検討

---

## 🎯 **成功指標 (KPI)**

### **定量指標**
- **知識カバレッジ**: 95%以上
- **検索成功率**: 90%以上  
- **応答時間**: 3秒以内
- **エラー発生率**: 5%以下

### **定性指標**
- チームメンバーの満足度
- 知識発見の効率性
- 意思決定の迅速性
- 知識の正確性と信頼性

---

この運用手順書により、Cogneeナレッジシステムが効果的に活用され、プロジェクトの知識管理が大幅に改善されることを目指します。