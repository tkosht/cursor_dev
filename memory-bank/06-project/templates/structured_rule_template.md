# 構造化ルールテンプレート

## 🎯 **適切なルール構造の設計指針**

### **基本構造**
各ルールは以下の6要素を明確に分離して記述する：

```yaml
rule_structure:
  trigger: "いつ適用されるか（具体的な発動条件）"
  scope: "何に対して適用されるか（明確な対象範囲）"
  prerequisites: "どのような状況が前提か（必要な条件）"
  exceptions: "どのような場合に適用されないか（例外条件）"
  criteria: "どう判断するか（客観的な判定基準）"
  action: "具体的に何をするか（実行手順）"
```

## 📋 **構造化ルールの実例**

### **改良版: ユーザー承認必須ルール**

#### **Rule ID**: AUTH-001
#### **Rule Name**: プロジェクト構造変更時のユーザー承認必須

```yaml
trigger:
  - ファイルシステムに新規ディレクトリを作成する時
  - 既存ディレクトリを移動・削除する時
  - プロジェクト構造定義を変更する時

scope:
  includes:
    - プロジェクトルート配下のすべてのディレクトリ
    - README.mdで定義された構造に影響する変更
    - 他のチームメンバーに影響する構造変更
  excludes:
    - 一時的な作業ディレクトリ (例: /tmp, /temp)
    - 個人用キャッシュディレクトリ (例: __pycache__, .git)
    - ビルド成果物ディレクトリ (例: output/, dist/)

prerequisites:
  - プロジェクトがチーム開発環境である
  - README.mdでプロジェクト構造が定義されている
  - 変更が他のメンバーの作業に影響する可能性がある

exceptions:
  emergency_conditions:
    - システム障害の緊急対応時（事後報告必須）
    - セキュリティインシデント対応時（事後報告必須）
  auto_approved_conditions:
    - Gitフック、CI/CDによる自動生成ディレクトリ
    - 既存のテンプレートに従った定型的なディレクトリ作成
  user_roles:
    - プロジェクトオーナーは事前承認なし（事後報告推奨）

criteria:
  user_permission_required:
    - 明示的な「承認」の意思表示
    - 変更内容の具体的理解の確認
    - 影響範囲の認識の確認
  objective_evidence:
    - 変更の必要性を示すデータ
    - 代替案の検討結果
    - 影響範囲の定量的分析

action:
  step1: "事前確認チェックリストの実行"
  step2: "ユーザーへの変更申請（フォーマット使用）"
  step3: "明示的承認の取得"
  step4: "承認内容に従った実装"
  step5: "実装結果の報告"
```

### **改良版: テスト必須化ルール**

#### **Rule ID**: TEST-001
#### **Rule Name**: 自動化機能のテスト必須化

```yaml
trigger:
  - 新しい自動化スクリプトを作成する時
  - 既存の自動化機能を変更する時
  - 自動化機能をプロダクション環境にデプロイする時

scope:
  includes:
    - Pre-commitフック
    - CI/CDパイプライン
    - 品質チェックスクリプト
    - 自動デプロイスクリプト
    - データ処理・変換スクリプト
  excludes:
    - 一回限りの使い捨てスクリプト
    - 個人用のヘルパースクリプト（他者が使用しない）
    - 設定ファイルのみの変更

prerequisites:
  - 自動化機能が他のシステム・人に影響を与える
  - 機能の失敗が業務に支障をきたす可能性がある
  - 継続的に使用される予定である

exceptions:
  rapid_prototyping:
    - プロトタイプ段階（本格運用前）
    - 概念実証（PoC）段階
    - 実験的な機能（明示的にラベル付け）
  emergency_hotfix:
    - 緊急バグ修正（事後テスト追加必須）
  simple_configurations:
    - 設定値のみの変更
    - ログレベルの変更など単純な設定

criteria:
  test_coverage_requirements:
    - 正常系テスト: 必須
    - 異常系テスト: 必須
    - 境界値テスト: データ処理がある場合必須
    - 統合テスト: 他システムと連携する場合必須
  quality_standards:
    - テストカバレッジ: 80%以上
    - 実行時間: 合計5分以内
    - 依存関係: 最小限に抑制

action:
  step1: "自動化機能の影響範囲分析"
  step2: "テスト戦略の策定"
  step3: "テストコードの実装"
  step4: "テストの実行・検証"
  step5: "カバレッジレポートの確認"
  step6: "CI/CDへの統合"
```

## 🔍 **構造化ルール検証のためのCognee最適化**

### **Cogneeでの構造化情報抽出改善**

```python
# 構造化ルール用のカスタムスキーマ
from pydantic import BaseModel
from typing import List, Optional, Dict

class StructuredRule(BaseModel):
    """構造化ルールのスキーマ"""
    rule_id: str
    rule_name: str
    
    trigger: List[str]  # 発動条件
    scope: Dict[str, List[str]]  # includes/excludes
    prerequisites: List[str]  # 前提条件
    exceptions: Dict[str, List[str]]  # 例外条件
    criteria: Dict[str, any]  # 判定基準
    action: Dict[str, str]  # 実行手順

class RuleContext(BaseModel):
    """ルール適用コンテキスト"""
    current_situation: str
    affected_components: List[str]
    user_role: str
    urgency_level: str
    available_alternatives: List[str]
```

### **コンテキスト認識検索の実装**

```python
def context_aware_rule_search(situation, components, user_role):
    """状況に応じたルール検索"""
    
    # 基本的なルール検索
    base_query = f"rules for {situation} affecting {components}"
    rules = cognee.search(base_query, "GRAPH_COMPLETION")
    
    # コンテキスト特化検索
    context_query = f"when {user_role} works on {components} in {situation}, what rules apply and what exceptions exist?"
    context_rules = cognee.search(context_query, "GRAPH_COMPLETION")
    
    # 例外条件の確認
    exception_query = f"exceptions for {situation} rules when {user_role}"
    exceptions = cognee.search(exception_query, "INSIGHTS")
    
    return {
        "applicable_rules": rules,
        "contextual_guidance": context_rules,
        "exceptions": exceptions
    }
```

## 📊 **構造化前後の比較**

### **Before: 構造化前**
```markdown
❌ "すべての自動化機能は、実装と同時に自動テストを作成する"
→ 適用条件不明、例外不明、判定基準曖昧
```

### **After: 構造化後**  
```markdown
✅ "Pre-commitフック作成時は、緊急バグ修正を除き、
   80%カバレッジの正常・異常系テストを事前実装する"
→ 適用条件明確、例外明確、判定基準客観的
```

## 🎯 **Cognee検索の改善効果**

### **構造化前の検索結果**
```python
cognee.search("when do I need user authorization?", "GRAPH_COMPLETION")
# → 曖昧で実用性に欠ける回答
```

### **構造化後の期待される検索結果**
```python
cognee.search("when do I need user authorization?", "GRAPH_COMPLETION")
# → 「ディレクトリ作成時、ただし一時ディレクトリと緊急時は除く」
#   という具体的で実用的な回答
```

## 🛠️ **実装推奨アクション**

### **1. 既存ルールの構造化**
- [ ] 4つの必須ルールを構造化テンプレートで書き直し
- [ ] 各ルールのトリガー・スコープ・例外を明確化
- [ ] 判定基準の客観化

### **2. Cogneeスキーマの最適化**
- [ ] 構造化ルール用のカスタムスキーマ作成
- [ ] コンテキスト認識検索機能の実装
- [ ] ルール適用ガイダンス機能の追加

### **3. 品質検証の強化**
- [ ] 構造化ルールの網羅性チェック
- [ ] コンテキスト別の適用テスト
- [ ] 例外条件の妥当性検証

この構造化により、「間違ったルール適用」「適用忘れ」を大幅に削減し、Cogneeでの適切なコンテキスト・前提条件抽出が可能になります。