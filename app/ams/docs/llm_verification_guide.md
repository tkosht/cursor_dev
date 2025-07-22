# LLM動作検証ガイド

## 概要

LLMが実際に動作していることを透明性を持って確認するためのガイドです。
モックやダミーレスポンスではなく、実際のAPI呼び出しであることを検証可能にします。

## 検証方法

### 1. 基本的な接続確認

```bash
# AMSディレクトリから実行
cd /home/devuser/workspace/app/ams

# シンプルな接続テスト
PYTHONPATH=. python scripts/test_llm_simple.py

# 詳細な接続テスト（推奨）
PYTHONPATH=. python scripts/test_llm_connection.py
```

### 2. 透明性を確保した検証

```bash
# 内部処理を可視化した検証
PYTHONPATH=. python scripts/test_llm_verification.py

# 詳細レポートを保存する場合
SAVE_VERIFICATION_REPORT=true PYTHONPATH=. python scripts/test_llm_verification.py
```

**注意**: 
- `PYTHONPATH=.` を指定して、srcディレクトリのインポートを有効にします
- .envファイルは親ディレクトリ（/home/devuser/workspace）から自動的に読み込まれます

## 検証プロセスの詳細

### test_llm_verification.py の検証項目

1. **環境変数検証**
   - APIキーの存在確認（値は表示しない）
   - キーのハッシュ値を記録

2. **ユニークチャレンジテスト**
   - タイムスタンプエコー: 一意の値を返すことを確認
   - 計算問題: 動的に生成された問題を解く
   - 文字数カウント: チャレンジIDの文字数を数える

3. **レイテンシ分析**
   - API呼び出しの応答時間を測定
   - 実際のAPIは通常100ms以上かかる
   - モックは通常10ms未満で応答

4. **レート制限チェック**
   - 連続呼び出しでの挙動確認
   - 実際のAPIは安定したレイテンシを示す

### 判定基準

- **✅ 実際のLLM API**
  - 真正性スコア ≥ 80%
  - 平均レイテンシ > 100ms
  - レイテンシの分散 < 5000ms

- **❌ 疑わしい動作**
  - 検証テストの合格率が低い
  - レスポンスが異常に速い
  - レスポンス時間が不安定

## コード内での透明性確保

### TransparentLLM クラスの使用

```python
from src.utils.llm_transparency import TransparentLLM
from src.utils.llm_factory import create_llm

# 通常のLLMを透明化ラッパーで包む
base_llm = create_llm()
transparent_llm = TransparentLLM(base_llm, enable_verification=True)

# 使用方法は通常のLLMと同じ
response = await transparent_llm.ainvoke("こんにちは")

# 検証サマリーを取得
summary = transparent_llm.get_verification_summary()
print(f"Total calls: {summary['total_calls']}")
print(f"Average latency: {summary['average_latency_ms']}ms")
```

### verify_llm_call デコレータ

```python
from src.utils.llm_transparency import verify_llm_call

@verify_llm_call
async def my_llm_function(prompt: str):
    llm = create_llm()
    return await llm.ainvoke(prompt)

# 実行時に自動的に検証情報が出力される
```

### LLMCallTracker の使用

```python
from src.utils.llm_transparency import get_llm_tracker

tracker = get_llm_tracker()
tracker.reset()

# LLM呼び出しを記録
tracker.track_call(
    prompt="テストプロンプト",
    response="テストレスポンス",
    model="gemini-1.5-flash",
    latency_ms=523,
    tokens={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}
)

# 詳細レポートを出力
tracker.print_detailed_report()
```

## セキュリティ考慮事項

### ❌ してはいけないこと

- `.env` ファイルの内容を表示
- APIキーの値を出力
- 環境変数の完全な値を記録

### ✅ 推奨される方法

- APIキーの存在確認のみ
- ハッシュ値での識別
- 機能テストによる動作確認
- レイテンシとレスポンスパターンの分析

## トラブルシューティング

### APIキーが設定されていない場合

```bash
# .envファイルの存在確認
ls -la .env

# 環境変数の設定状態確認（値は表示しない）
python -c "import os; print('GOOGLE_API_KEY:', 'SET' if os.getenv('GOOGLE_API_KEY') else 'NOT SET')"

# dotenvを使った確認
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('GOOGLE_API_KEY:', 'SET' if os.getenv('GOOGLE_API_KEY') else 'NOT SET')"
```

### APIキーが無効/期限切れの場合

エラーメッセージ例：
```
API key expired. Please renew the API key.
```

対処法：
1. Google AI Studio (https://makersuite.google.com/app/apikey) で新しいAPIキーを生成
2. .envファイルまたは環境変数を更新
3. **重要**: APIキーの値を直接表示したり、コミットしたりしないこと

### レスポンスが遅い場合

- ネットワーク接続を確認
- APIのレート制限を確認
- リージョンによるレイテンシを考慮

### 検証が失敗する場合

1. 詳細レポートを保存して分析
2. 各検証テストの結果を確認
3. レイテンシパターンを確認

## まとめ

LLMの動作検証は、単に「動く」ことを確認するだけでなく、
実際のAPIを使用していることを透明性を持って証明することが重要です。

このガイドのツールを使用することで：
- 内部処理の可視化
- 実際のAPI呼び出しの証明
- パフォーマンス特性の記録
- セキュリティを保った検証

が可能になります。