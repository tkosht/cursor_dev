# エラーハンドリング機能の詳細設計

## 1. クラス設計

### 1.1 AdaptiveCrawler クラス

#### メソッド: _handle_error
```python
async def _handle_error(
    self,
    error: Union[str, Exception],
    context: Dict[str, Any]
) -> Dict[str, Any]:
    """エラーを処理

    Args:
        error: エラーメッセージまたは例外オブジェクト
        context: エラーコンテキスト

    Returns:
        エラー分析結果の辞書
    """
    try:
        # 1. エラーログの出力
        self._log_error(f'エラー発生: {str(error)}')
        self._log_debug(f'エラーコンテキスト: {context}')

        # 2. LLMによるエラー分析
        error_analysis = await self.llm_manager.analyze_error(
            self.default_model,  # 使用するモデル
            str(error)  # エラーメッセージ
        )

        # 3. 分析結果のログ出力
        self._log_info(f'エラー分析結果: {error_analysis}')

        # 4. リトライ戦略の決定
        should_retry = error_analysis.get('should_retry', False)
        if should_retry:
            self._log_info('リトライを実行します')
            if self.retry_count < self.max_retries:
                self.retry_count += 1
                await self._retry_with_backoff()
        else:
            self._log_info('リトライをスキップします')

        # 5. 結果の返却
        return {
            'error': str(error),
            'context': context,
            'analysis': error_analysis,
            'should_retry': should_retry,
            'retry_count': self.retry_count
        }

    except Exception as e:
        # 6. エラー処理中の例外をハンドリング
        self._log_error(f'エラー処理中に例外が発生: {str(e)}')
        return {
            'error': str(error),
            'context': context,
            'analysis': {'error': 'エラー分析に失敗しました'},
            'should_retry': False,
            'retry_count': self.retry_count
        }
```

## 2. エラー分析の詳細

### 2.1 エラーコンテキスト
```python
{
    'url': str,              # クロール対象URL
    'target_data': Dict,     # 取得対象データ
    'retry_count': int,      # リトライ回数
    'error': str,            # エラーメッセージ
    'timestamp': str,        # エラー発生時刻
    'request_headers': Dict  # リクエストヘッダー
}
```

### 2.2 エラー分析結果
```python
{
    'error_type': str,       # エラーの種類
    'severity': str,         # 深刻度
    'description': str,      # エラーの説明
    'should_retry': bool,    # リトライ判断
    'suggested_action': str, # 推奨アクション
    'recovery_steps': List   # 回復手順
}
```

## 3. リトライ戦略

### 3.1 バックオフ計算
```python
delay = self.retry_delay * (2 ** self.retry_count)  # 指数バックオフ
```

### 3.2 リトライ条件
- リトライ回数が上限未満
- エラー分析でリトライ推奨
- 一時的なエラーと判断

## 4. ログ出力仕様

### 4.1 ログレベルと内容
- ERROR
  - エラーの発生
  - エラー処理中の例外
- DEBUG
  - エラーコンテキスト
  - 詳細なスタックトレース
- INFO
  - 分析結果
  - リトライ判断
  - バックオフ時間
- WARNING
  - 分析失敗
  - リトライ上限到達

### 4.2 ログフォーマット
```
%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

## 5. テスト仕様

### 5.1 ユニットテスト
```python
@pytest.mark.asyncio
async def test_handle_error():
    # テストケース1: 404エラー
    error = "404 Not Found"
    context = {
        'url': 'https://example.com',
        'target_data': {'key': 'value'},
        'retry_count': 0
    }
    result = await crawler._handle_error(error, context)
    assert result['error'] == error
    assert result['context'] == context
    assert 'analysis' in result
    assert isinstance(result['should_retry'], bool)
    assert isinstance(result['retry_count'], int)

    # テストケース2: 接続エラー
    # テストケース3: タイムアウト
    # テストケース4: LLM分析失敗
```

### 5.2 統合テスト
```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_error_handling_integration():
    # 1. クロール実行
    with pytest.raises(aiohttp.ClientError):
        await crawler.crawl(url, target_data)
    
    # 2. エラー分析結果の検証
    error_analysis = await crawler._handle_error(
        '404 Not Found',
        {'url': url, 'target_data': target_data}
    )
    assert isinstance(error_analysis, dict)
    assert all(key in error_analysis for key in [
        'error', 'context', 'analysis',
        'should_retry', 'retry_count'
    ])
``` 