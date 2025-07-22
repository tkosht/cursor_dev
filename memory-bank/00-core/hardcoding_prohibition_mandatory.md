# ハードコード絶対禁止ルール

**作成日**: 2025-07-23
**重要度**: CRITICAL - 絶対遵守

## 🚫 ハードコード禁止事項

### 1. 絶対にハードコードしてはいけないもの
```bash
HARDCODE_FORBIDDEN=(
    "API keys"              # APIキー
    "Model names"           # モデル名（gemini-1.5-flash等）
    "URLs/Endpoints"        # API エンドポイント
    "Credentials"          # 認証情報
    "File paths"           # 絶対パス
    "Port numbers"         # ポート番号
    "Timeout values"       # タイムアウト値
    "Max tokens"           # トークン制限
    "Temperature"          # 温度パラメータ
)
```

### 2. 正しい実装パターン

#### ❌ 違反例
```python
# NEVER DO THIS
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",  # ハードコード違反！
    temperature=0.7,           # ハードコード違反！
    max_tokens=1000           # ハードコード違反！
)
```

#### ✅ 正しい例
```python
# ALWAYS DO THIS
from src.config import get_config

config = get_config()
llm = ChatGoogleGenerativeAI(
    model=config.llm.gemini_model,      # 設定から取得
    temperature=config.llm.temperature,  # 設定から取得
    max_tokens=config.llm.max_tokens    # 設定から取得
)

# または llm_factory を使用
from src.utils.llm_factory import create_llm
llm = create_llm()  # すべての設定が自動適用される
```

### 3. テストコードでの適用

```python
# テストでも設定を使用
@pytest.fixture
def test_llm():
    """テスト用LLMフィクスチャ"""
    return create_llm()  # ハードコードなし

# パラメータ化テスト
@pytest.mark.parametrize("model", [
    pytest.param(None, id="default"),  # デフォルト設定を使用
])
def test_llm_functionality(model):
    llm = create_llm(model=model)
    # テスト実行
```

### 4. 環境変数とデフォルト値

```python
# 環境変数 → 設定ファイル → デフォルト値の優先順位
import os

# ❌ 違反
timeout = 60  # ハードコード

# ✅ 正しい
timeout = int(os.getenv("TIMEOUT", config.llm.timeout))
```

### 5. 検出パターン

```bash
# CI/CDで検出すべきパターン
HARDCODE_PATTERNS=(
    'model="gemini-[0-9]'
    'temperature=[0-9]'
    'max_tokens=[0-9]'
    'timeout=[0-9]'
    'port=[0-9]'
    '/home/[^"]*'  # 絶対パス
)
```

## 📋 チェックリスト

プルリクエスト前の確認：
1. ✓ モデル名が設定から取得されているか
2. ✓ パラメータが設定から取得されているか
3. ✓ パスが相対パスまたは設定値か
4. ✓ 環境固有の値がハードコードされていないか
5. ✓ テストコードでもハードコードがないか

## 🔧 実装ガイドライン

1. **新規ファイル作成時**
   - 必ず config をインポート
   - llm_factory を優先使用

2. **既存コード修正時**
   - ハードコードされた値を発見したら即座に修正
   - 設定への移行を優先

3. **レビュー時**
   - ハードコードを見逃さない
   - 設定の一元管理を確認

## 🚨 違反時の対処

1. **即座に修正**: ハードコードを発見したら直ちに修正
2. **設定追加**: 必要な設定項目が不足している場合は config.py に追加
3. **ドキュメント更新**: 新しい設定項目は README に記載

---

**このルールは絶対です。例外は認められません。**