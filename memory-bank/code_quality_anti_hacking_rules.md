# コード品質アンチハッキング・ルール（絶対遵守）

最終更新: 2025-06-04

## 🚨 基本原則：品質指標への誠実性

### **数値ハッキング絶対禁止令**

品質指標（Flake8、テストカバレッジ、複雑度等）を迂回・偽装する行為は**絶対に禁止**する。

## 🚫 絶対禁止事項

### 1. noqaの濫用禁止

```python
# ❌ 禁止例
import some_module  # noqa: E402
long_line_that_exceeds_79_characters_without_good_reason  # noqa: E501
unused_variable = "test"  # noqa: F841

# ✅ 正しい対応
# 1. import順序の修正
# 2. 行分割による可読性向上
# 3. 未使用変数の削除または適切な使用
```

### 2. カバレッジ除外の濫用禁止

```python
# ❌ 禁止例
def untested_function():  # pragma: no cover
    complex_business_logic()
    return result

# ✅ 正しい対応
# 適切なテストケースの作成
```

### 3. 複雑度回避の偽装禁止

```python
# ❌ 禁止例（意図的な複雑度分散）
def fake_simplification(data):
    return _helper1(data) and _helper2(data) and _helper3(data)

def _helper1(data): return complex_condition1(data)  # 実質的に複雑
def _helper2(data): return complex_condition2(data)
def _helper3(data): return complex_condition3(data)

# ✅ 正しい対応
# 真の責務分離による設計改善
```

## ✅ 例外的許可の厳格基準

### 許可条件（全て満たす場合のみ）

1. **技術的制約**：アーキテクチャ上回避不可能
2. **アーキテクト承認**：技術責任者の明示的承認
3. **期限設定**：明確な解決予定日
4. **代替案検討**：他の解決方法の検討記録
5. **影響範囲限定**：局所的かつ限定的使用

### 許可記録フォーマット

```python
# TODO: 2025-07-01まで - アーキテクト承認済み
# 理由: レガシーシステム連携のための一時的回避
# 代替案: モジュール分離によるリファクタリング（Q3計画）
# 承認者: [architect_name]
# 関連チケット: #1234
import legacy_module  # noqa: E402
```

## 🔧 正しい解決パターン

### 1. Import順序問題の解決

#### ❌ 悪い例
```python
import sys
sys.path.insert(0, "some/path")
from custom_module import something  # noqa: E402
```

#### ✅ 良い例
```python
# conftest.py または適切な設定ファイル
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "modules"))

# テストファイル
from custom_module import something  # クリーンなimport
```

### 2. 長い行の適切な分割

#### ❌ 悪い例
```python
very_long_function_call_with_many_parameters(param1, param2, param3, param4, param5)  # noqa: E501
```

#### ✅ 良い例
```python
very_long_function_call_with_many_parameters(
    param1=value1,
    param2=value2,
    param3=value3,
    param4=value4,
    param5=value5
)
```

### 3. 未使用変数の適切な処理

#### ❌ 悪い例
```python
result = expensive_computation()  # noqa: F841
```

#### ✅ 良い例
```python
# 使用しない場合
_ = expensive_computation()  # 明示的な破棄

# または適切に使用
result = expensive_computation()
logger.debug(f"Computed result: {result}")
return result
```

## 📊 品質監視の強化

### 自動チェック強化

```bash
# CI/CDパイプラインに追加
# 1. noqa使用量の監視
grep -r "# noqa" . --include="*.py" | wc -l > noqa_count.txt

# 2. 品質指標トレンド監視
# 3. 例外使用の定期レビュー
```

### コードレビュー必須項目

- [ ] noqa使用に正当な理由があるか
- [ ] 一時的な例外に期限が設定されているか
- [ ] 代替解決方法が検討されているか
- [ ] アーキテクト承認が得られているか

## 🎯 教訓：今回のケース分析

### 発生した問題
- `# noqa: E402`による品質チェック回避
- 根本問題（import順序）の未解決
- 技術的債務の蓄積

### 採用した解決策
1. **conftest.py**によるパス設定
2. **import順序の正規化**
3. **noqaの完全削除**

### 学んだ原則
- 品質指標は絶対的な基準
- 回避ではなく根本解決を追求
- 一時的な例外も厳格な管理下に置く

## 🚀 実装ガイドライン

### 新規開発時
1. 品質基準を設計段階から考慮
2. アーキテクチャレベルでの品質担保
3. テスタビリティを優先した設計

### 既存コード改善時
1. noqa使用箇所の全数調査
2. 根本原因の分析と解決計画策定
3. 段階的な品質向上の実施

### レビュープロセス
1. 品質指標の確認を必須化
2. 例外使用の正当性検証
3. 長期的な技術的債務への配慮

## 📋 チェックリスト

### 開発者用
- [ ] noqaを使用する前に代替解決方法を検討したか
- [ ] 品質基準違反の根本原因を理解しているか
- [ ] 例外使用に明確な期限と計画があるか

### レビュアー用
- [ ] 品質指標の回避が適切に処理されているか
- [ ] 一時的な例外に適切な管理がされているか
- [ ] 長期的な保守性が考慮されているか

### アーキテクト用
- [ ] 例外承認の影響範囲を評価したか
- [ ] 代替解決方法の実現可能性を検討したか
- [ ] 品質基準の体系的な維持計画があるか

---

**重要**: このルールは品質への誠実性を保つための**最後の砦**です。妥協は技術的債務と組織文化の劣化を招きます。