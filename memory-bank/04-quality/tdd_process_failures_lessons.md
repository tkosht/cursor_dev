# TDDプロセス失敗事例と改善ナレッジ

このドキュメントは、**実際のTDD実践で発生した問題**から得られた重要な学習事項を体系化し、**今後必ず読み込み適用すべきルール**として整理したものです。

## 🚨 発見された重大な問題

### 問題1: API仕様理解不足によるテスト失敗 ⭐⭐⭐⭐⭐

**発生事象**:
```python
# ❌ 失敗したテスト - 間違った前提条件
def test_create_with_invalid_id_types_raises_validation_error(self, invalid_id):
    # Given: 空文字列は無効なidという前提（間違い）
    skill_data = {"id": "", "name": "Test", "description": "Test", "tags": ["test"]}
    
    # When/Then: ValidationErrorが発生すると期待（間違い）
    with pytest.raises(ValidationError):  # ❌ 実際には発生しない
        AgentSkill(**skill_data)
```

**根本原因**:
- **API仕様の事前確認不足**: テストを書く前にAgentSkillの実際の動作を確認していない
- **推測ベースのテスト作成**: ドキュメントや実装を見ずに「こうあるべき」で書いた
- **Red段階の不備**: 失敗するテストを書いていない（偶然成功してしまう）

### 問題2: カバレッジ目標大幅未達 ⭐⭐⭐⭐⭐

**現状**: 53% （目標90%から37ポイント不足）

**問題の詳細**:
- `base_agent.py`: 37%カバレッジ（63%未実装）
- `simple_agent.py`: 68%カバレッジ（32%未実装）
- 重要な分岐・エラーハンドリングがテストされていない

### 問題3: pytest設定不備による警告 ⭐⭐⭐

**発生警告**:
```
PytestUnknownMarkWarning: Unknown pytest.mark.unit
```

**原因**: `conftest.py`でマーカーを定義したが、`pytest.ini`や`pyproject.toml`での登録が不足

## 📋 緊急改善ルール（必須適用）

### ルール1: API仕様確認プロセスの義務化 ⭐⭐⭐⭐⭐

**実装前必須手順**:
```bash
# 1. 実際のAPI動作確認
python -c "from module import Class; obj = Class(**test_data); print(obj)"

# 2. バリデーション境界値の確認
python -c "
from module import Class
from pydantic import ValidationError

test_cases = [None, '', 123, [], {}]
for case in test_cases:
    try:
        obj = Class(field=case)
        print(f'{case}: ✅ 受け入れ可能')
    except ValidationError as e:
        print(f'{case}: ❌ ValidationError - {e}')
"

# 3. 結果をテストケースに反映
```

### ルール2: Red-Green-Refactor厳格実践 ⭐⭐⭐⭐⭐

**Red段階（失敗確認）**:
```bash
# 1. 失敗するテストを作成
def test_should_fail():
    assert False  # 必ず失敗

# 2. 失敗を確認
poetry run pytest tests/path/to/test.py::test_should_fail -v
# Expected: FAILED

# 3. 実装なしでの失敗確認
poetry run pytest tests/path/to/test.py::test_real_case -v
# Expected: ImportError or AssertionError
```

**Green段階（最小実装）**:
```bash
# 1. テストが通る最小限の実装
def minimum_implementation():
    return "minimum working code"

# 2. テスト成功確認
poetry run pytest tests/path/to/test.py::test_real_case -v
# Expected: PASSED
```

**Refactor段階（改善確認）**:
```bash
# 1. コード改善
# 2. 全テスト実行で回帰なし確認
poetry run pytest tests/ -v
# Expected: All PASSED
```

### ルール3: カバレッジ品質ゲート ⭐⭐⭐⭐⭐

**実装時必須確認**:
```bash
# 1. カバレッジ測定
poetry run pytest tests/ --cov=src --cov-report=term-missing

# 2. 品質ゲート確認
# - 単体テスト: 最低90%
# - 新規コード: 100%
# - クリティカルパス: 100%

# 3. 不足箇所の特定と対応
# Missing列で未実装行を確認し、テスト追加
```

### ルール4: pytest設定完全化 ⭐⭐⭐⭐

**`pyproject.toml`必須設定**:
```toml
[tool.pytest.ini_options]
markers = [
    "unit: 単体テスト（高速・独立）",
    "integration: 統合テスト（中速・依存あり）",
    "e2e: E2Eテスト（低速・完全シナリオ）",
    "slow: 実行時間の長いテスト",
]
addopts = [
    "-v",
    "--strict-markers",
    "--cov=src",
    "--cov-fail-under=90",
]
```

## 🔧 即座実行すべき修正アクション

### アクション1: 失敗テストの正確な修正
```python
# ❌ Before: 間違った前提
@pytest.mark.parametrize("invalid_id", ["", 123, [], {}])

# ✅ After: API仕様確認後の正確な前提
@pytest.mark.parametrize("invalid_id", [None, 123, [], {}])  # ""は除外
```

### アクション2: カバレッジ向上テスト追加
```python
# 未カバレッジ箇所のテスト追加
def test_error_handling_branch():
    """エラーハンドリング分岐のテスト"""
    
def test_edge_case_boundary():
    """境界値・エッジケースのテスト"""
```

### アクション3: 設定修正
```bash
# pytest.ini または pyproject.toml でマーカー登録
```

## 📚 継続実践ルール

### 毎回のTDDサイクルで確認すべき項目

**Red段階チェックリスト**:
- [ ] API仕様を実際に確認したか？
- [ ] テストが本当に失敗するか確認したか？
- [ ] 失敗理由は期待通りか？

**Green段階チェックリスト**:
- [ ] 最小限の実装で実装したか？
- [ ] テストが成功することを確認したか？
- [ ] 他のテストに影響していないか？

**Refactor段階チェックリスト**:
- [ ] コードの重複を削除したか？
- [ ] 可読性を改善したか？
- [ ] 全テストが通ることを確認したか？

### 品質指標の継続監視

**毎日確認**:
```bash
# 1. 全テスト実行
poetry run pytest tests/ -v

# 2. カバレッジ確認
poetry run pytest tests/ --cov=src --cov-report=term-missing

# 3. 品質指標
# - テスト成功率: 100%
# - カバレッジ: 90%+
# - 実行時間: <10秒（単体テスト）
```

## 🎯 成功のための重要原則

### 原則1: 推測禁止・確認必須
- コードを書く前に必ずAPIの動作を確認
- ドキュメントより実装を信頼
- 期待と現実のギャップを測定

### 原則2: 小さなステップでの前進
- 巨大なテストケースを作らない
- 1つのテストで1つの側面のみ検証
- 失敗・成功・改善の明確な区別

### 原則3: 品質指標の継続監視
- カバレッジ・成功率・実行時間の監視
- 劣化の早期発見と対処
- 改善のサイクル化

---

**このナレッジは今後すべてのTDD実践で必須適用し、プロジェクト開始時に必ず読み込むものとする。**

---

**作成日**: TDD実践でのテスト失敗・カバレッジ不足発見時
**更新日**: TDD品質問題発生時に継続更新
**対象**: 全開発者、TDD実践者
**緊急度**: 最高（immediate action required） 