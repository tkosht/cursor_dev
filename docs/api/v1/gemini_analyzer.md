# GeminiAnalyzer API

## 概要

`GeminiAnalyzer`は、Gemini APIを使用してコンテンツを解析し、エンティティとリレーションシップを抽出するクラスです。

## 初期化

```python
from app.gemini_analyzer import GeminiAnalyzer

analyzer = GeminiAnalyzer(api_key="your_gemini_api_key")
```

### パラメータ

- `api_key` (str): Gemini APIのキー
  - 必須
  - 環境変数`GOOGLE_API_KEY_GEMINI`からも取得可能

### 例外

- `ValidationError`: APIキーが不正な場合

## メソッド

### analyze_content

コンテンツを解析し、エンティティとリレーションシップを抽出します。

```python
result = analyzer.analyze_content(content="分析対象のテキスト")
```

#### パラメータ

- `content` (str): 解析対象のコンテンツ
  - 必須
  - 4096文字以内

#### 戻り値

```python
{
    "entities": ["エンティティ1", "エンティティ2", ...],
    "relationships": ["リレーションシップの説明1", "リレーションシップの説明2", ...]
}
```

#### 例外

- `ValidationError`: コンテンツが不正な形式の場合
- `GeminiAPIError`: API呼び出しに失敗した場合
- `ServiceUnavailable`: サービスが一時的に利用できない場合

### get_metrics

現在のメトリクスを取得します。

```python
metrics = analyzer.get_metrics()
```

#### 戻り値

```python
{
    "api_call": {
        "total_time": float,  # 合計実行時間
        "call_count": int,    # 呼び出し回数
        "min_time": float,    # 最小実行時間
        "max_time": float     # 最大実行時間
    }
}
```

## エラーハンドリング

### リトライ機能

- 一時的なエラーが発生した場合、自動的にリトライを実行
- 最大リトライ回数: 3回
- リトライ間隔: 指数バックオフ（1秒、2秒、4秒）

### エラーレート監視

- 5分間で5回以上のエラーが発生した場合、`ServiceUnavailable`例外を発生
- エラー発生時刻を記録し、古いエラーは自動的に削除

## パフォーマンス最適化

### レート制限

- API呼び出しは1秒に1回に制限
- 制限を超える呼び出しは自動的に待機

### メモリ管理

- 大きなレスポンスは適切にクリーンアップ
- メモリリークを防ぐため、不要なデータは即座に解放

## 使用例

```python
from app.gemini_analyzer import GeminiAnalyzer

# 初期化
analyzer = GeminiAnalyzer(api_key="your_gemini_api_key")

try:
    # コンテンツ解析
    content = """
    株式会社Aは新製品Xを発表し、市場シェア20%を獲得しました。
    競合他社のBは対抗製品Yの開発を発表しています。
    """
    result = analyzer.analyze_content(content)
    
    # 結果の処理
    for entity in result["entities"]:
        print(f"検出されたエンティティ: {entity}")
    
    for relationship in result["relationships"]:
        print(f"検出されたリレーションシップ: {relationship}")
    
    # メトリクスの確認
    metrics = analyzer.get_metrics()
    print(f"API実行時間: {metrics['api_call']['total_time']}秒")

except ValidationError as e:
    print(f"入力エラー: {str(e)}")
except GeminiAPIError as e:
    print(f"API呼び出しエラー: {str(e)}")
except ServiceUnavailable as e:
    print(f"サービス一時停止: {str(e)}")
``` 