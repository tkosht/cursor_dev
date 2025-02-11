# システムパターン

## アーキテクチャパターン

### 設定管理
1. シングルトンパターン
   - 一意のインスタンス
   - 遅延初期化
   - スレッドセーフ

2. 設定の階層構造
   - モジュール別の設定グループ
   - ドット記法でのアクセス
   - デフォルト値の定義

3. 永続化
   - JSONファイル形式
   - ユーザーホームディレクトリ
   - 自動バックアップ

4. 実装パターン
   ```python
   settings = Settings()
   value = settings.get("module.setting", default="value")
   settings.set("module.setting", "new_value")
   settings.reset("module.setting")
   ```

### ロギング戦略
1. ログレベルの定義
   - DEBUG: 開発時のデバッグ情報
   - INFO: 通常の操作情報
   - WARNING: 注意が必要な状況
   - ERROR: エラー情報

2. ログの構造化
   - JSON形式での出力
   - タイムスタンプ
   - ログレベル
   - モジュール名
   - メッセージ
   - コンテキスト情報

3. ファイル管理
   - ログレベル別のファイル分割
   - ローテーション設定
   - 最大ファイルサイズ: 10MB
   - バックアップ数: 5

4. 実装パターン
   ```python
   self.logger = CustomLogger(__name__)
   self.logger.info("操作の説明", {"key": "value"})
   try:
       # 処理
   except Exception as e:
       self.logger.error(f"エラーの説明: {e}")
       raise CustomError(str(e))
   ```

### エラーハンドリング
1. カスタム例外の定義
   - モジュール固有の例外クラス
   - 明確なエラーメッセージ
   - エラーコンテキストの保持

2. エラー処理パターン
   ```python
   try:
       # 危険な操作
   except Exception as e:
       error_msg = f"操作に失敗: {e}"
       self.logger.error(error_msg)
       raise CustomError(error_msg)
   ```

### UI設計
1. コンポーネント構成
   - メインウィンドウ
   - 検索フレーム
   - 結果表示エリア

2. イベント処理
   - ユーザー操作のログ記録
   - エラー時のフィードバック
   - 非同期処理の状態管理

3. 実装パターン
   ```python
   def _on_action(self) -> None:
       self.logger.info("アクションの開始")
       try:
           # 処理
           self.logger.debug("処理の詳細")
       except Exception as e:
           self.logger.error(f"エラー: {e}")
           messagebox.showerror("エラー", str(e))
   ```

## デザインパターン

### Singleton
- 設定管理
- ログ設定
- データベース接続

### Factory
- ログハンドラーの作成
- UI要素の生成

### Observer
- イベント通知
- UI更新
- ログ監視

## ファイル構造

```
app/
├── __init__.py
├── logger.py
├── search_engine.py
├── ui/
│   ├── __init__.py
│   ├── main_window.py
│   └── components/
└── config/
    └── settings.py

logs/
├── debug/
├── info/
└── error/

tests/
├── __init__.py
├── test_logger.py
├── test_search_engine.py
└── test_settings.py
```

## コーディング規約

### 設定管理
1. シングルトンパターンの使用
2. 階層的な設定構造
3. デフォルト値の提供
4. 設定変更のログ記録

### ロギング
1. 各クラスで独立したロガーインスタンスを使用
2. 適切なログレベルの選択
3. 構造化されたコンテキスト情報の提供
4. エラー時は必ずログを記録

### エラーハンドリング
1. カスタム例外の使用
2. エラーの詳細な記録
3. ユーザーフレンドリーなメッセージ
4. 適切なエラー伝播

### UI実装
1. コンポーネントの適切な分割
2. イベントハンドラーでのログ記録
3. エラー時のユーザーフィードバック
4. 非同期処理の適切な管理

### テスト
1. ユニットテストの作成
2. エッジケースのテスト
3. ログ出力のテスト
4. エラーハンドリングのテスト

## テストパターン

### モックの設定パターン

1. 外部APIのモック
   ```python
   # 正しいパターン
   with patch('app.llm_processor.OpenAI', autospec=True) as mock_class:
       mock_client = MagicMock()
       mock_class.return_value = mock_client
       # APIクライアントの階層的な設定
       mock_client.models = MagicMock()
       mock_client.models.list = MagicMock()
   ```

2. 非同期メソッドのモック
   ```python
   # 正しいパターン
   mock_client.chat.completions.create = AsyncMock(return_value=mock_completion)
   ```

3. 複数回の呼び出しが必要な場合
   ```python
   # 正しいパターン
   mock_validation_response = MagicMock()
   mock_client.messages.create = AsyncMock(return_value=mock_validation_response)
   mock_response = MagicMock()
   mock_response.content = [MagicMock(text="テスト回答")]
   mock_client.messages.create.return_value = mock_response
   ```

### エラーハンドリングパターン

1. 例外の検証
   ```python
   with pytest.raises(LLMProcessorError) as exc_info:
       await processor.generate_response("テスト", [])
   assert "エラーメッセージ" in str(exc_info.value)
   ```

2. タイムアウトの検証
   ```python
   with pytest.raises(LLMProcessorError) as exc_info:
       await processor.generate_response("テスト", context, timeout=1)
   assert "タイムアウト" in str(exc_info.value)
   ```

### 非同期テストパターン

1. 基本的な非同期テスト
   ```python
   @pytest.mark.asyncio
   async def test_async_function():
       result = await async_function()
       assert result == expected
   ```

2. 並行処理のテスト
   ```python
   tasks = [async_function() for _ in range(5)]
   results = await asyncio.gather(*tasks)
   assert all(result == expected for result in results)
   ```

## 統合テストパターン

### TwitterClient + SearchEngine
1. データフロー
   ```mermaid
   flowchart LR
       TC[TwitterClient] -->|ブックマーク取得| SE[SearchEngine]
       SE -->|インデックス構築| IDX[Faissインデックス]
       SE -->|検索実行| RES[検索結果]
   ```

2. テストシナリオ
   ```python
   # 基本フロー
   twitter_client.fetch_bookmarks() -> bookmarks
   search_engine.add_bookmarks(bookmarks)
   search_engine.search(query) -> results

   # エラーケース
   - API制限時の動作
   - ネットワークエラー時の動作
   - 無効なデータ形式
   ```

3. 検証項目
   - ブックマークの正確な取得
   - インデックスへの正確な追加
   - 検索結果の妥当性
   - エラー伝播の確認
   - パフォーマンス要件の充足

### LLMProcessor + SearchEngine
1. データフロー
   ```mermaid
   flowchart LR
       SE[SearchEngine] -->|検索結果| LP[LLMProcessor]
       LP -->|プロンプト生成| PR[Prompt]
       PR -->|LLM呼び出し| RES[生成結果]
   ```

2. テストシナリオ
   ```python
   # 基本フロー
   search_engine.search(query) -> results
   llm_processor.generate_response(query, results) -> response

   # エラーケース
   - LLM APIエラー
   - コンテキスト長超過
   - 無効な検索結果
   ```

3. 検証項目
   - 検索結果の適切な利用
   - プロンプトの適切な生成
   - 回答の品質
   - エラー処理の適切性
   - 応答時間の要件充足

### UI + SearchEngine
1. データフロー
   ```mermaid
   flowchart LR
       UI[UI] -->|検索リクエスト| SE[SearchEngine]
       SE -->|検索結果| UI
       UI -->|結果表示| VW[View]
   ```

2. テストシナリオ
   ```python
   # 基本フロー
   ui.search_and_respond(query) -> response, results
   ui.display_results(results)

   # エラーケース
   - 検索エラー時のUI表示
   - 無効なクエリ
   - 結果表示エラー
   ```

3. 検証項目
   - ユーザー入力の適切な処理
   - 検索結果の正確な表示
   - エラーメッセージの適切な表示
   - UI応答性の確保
   - ユーザビリティ要件の充足

### テスト実装ガイドライン
1. フィクスチャ設計
   ```python
   @pytest.fixture
   def integrated_components():
       """統合テスト用のコンポーネント群を初期化"""
       twitter_client = TwitterClient()
       search_engine = SearchEngine()
       llm_processor = LLMProcessor()
       return twitter_client, search_engine, llm_processor
   ```

2. モック戦略
   ```python
   # 外部APIのモック
   @pytest.fixture
   def mock_twitter_api():
       with patch('tweepy.Client') as mock:
           yield mock

   # LLM APIのモック
   @pytest.fixture
   def mock_llm_api():
       with patch('google.generativeai') as mock:
           yield mock
   ```

3. 非同期処理
   ```python
   @pytest.mark.asyncio
   async def test_async_integration():
       """非同期処理を含む統合テスト"""
       async with AsyncClient() as client:
           # テストコード
   ```

4. パフォーマンス検証
   ```python
   def test_integration_performance():
       """統合テストでのパフォーマンス検証"""
       start_time = time.time()
       # 処理実行
       end_time = time.time()
       assert end_time - start_time < TIMEOUT
   ```

### テストデータ管理
1. テストデータの構造
   ```python
   @pytest.fixture
   def test_bookmarks():
       return [
           {
               "id": "1",
               "text": "テストツイート1",
               "created_at": "2024-01-01"
           },
           # ...
       ]
   ```

2. データセットの規模
   - 小規模（10件未満）: 基本機能テスト用
   - 中規模（100件程度）: 結合動作確認用
   - 大規模（1000件以上）: パフォーマンステスト用

3. エッジケース
   - 特殊文字を含むデータ
   - 長文データ
   - 空データ
   - 重複データ

### 品質基準
1. カバレッジ要件
   - 統合テスト全体で80%以上
   - クリティカルパスは100%
   - エラーハンドリングは100%

2. パフォーマンス要件
   - 検索応答時間: 1秒以内
   - LLM応答時間: 5秒以内
   - メモリ使用量: 2GB以内

3. 信頼性要件
   - エラー発生率: 0.1%以下
   - データ整合性: 100%
   - 回答品質: 90%以上

## アーキテクチャパターン

### 依存性注入
- テスト容易性を考慮したコンストラクタインジェクション
- モックオブジェクトの差し替えが容易な設計

### エラー階層
- アプリケーション固有の例外クラス
- 適切なエラーメッセージとコンテキスト情報

### 非同期処理
- asyncio/awaitパターンの一貫した使用
- 適切なタイムアウト処理 

## パフォーマンステストパターン

### 大規模データセットテスト
1. データ生成パターン
   ```python
   @pytest.fixture(scope="session")
   def large_dataset():
       """大規模テストデータの生成"""
       return [
           {
               "id": str(i),
               "url": f"https://twitter.com/user{i}/status/{i}",
               "text": f"テストツイート {i} " * 10,
               "created_at": str(1234567890 + i),
               "author": f"user{i}",
           }
           for i in range(100000)
       ]
   ```

2. メモリ使用量測定
   ```python
   def test_memory_usage():
       """メモリ使用量の測定"""
       process = psutil.Process()
       initial_memory = process.memory_info().rss
       
       # 処理実行
       
       final_memory = process.memory_info().rss
       memory_increase = (final_memory - initial_memory) / (1024 * 1024)  # MB
       assert memory_increase < MEMORY_LIMIT
   ```

3. 処理時間測定
   ```python
   def test_processing_time():
       """処理時間の測定"""
       start_time = time.time()
       
       # 処理実行
       
       end_time = time.time()
       processing_time = end_time - start_time
       assert processing_time < TIME_LIMIT
   ```

### 同時リクエストテスト
1. 同時実行パターン
   ```python
   async def test_concurrent_requests():
       """同時リクエストの処理"""
       tasks = [
           asyncio.create_task(process_request(i))
           for i in range(CONCURRENT_COUNT)
       ]
       results = await asyncio.gather(*tasks)
       assert len(results) == CONCURRENT_COUNT
   ```

2. リソース競合検証
   ```python
   async def test_resource_contention():
       """リソース競合の検証"""
       shared_resource = SharedResource()
       tasks = [
           asyncio.create_task(shared_resource.process())
           for _ in range(CONCURRENT_COUNT)
       ]
       results = await asyncio.gather(*tasks)
       assert all(result.is_valid for result in results)
   ```

### 長期安定性テスト
1. メモリリーク検出
   ```python
   def test_memory_leak():
       """メモリリーク検出"""
       process = psutil.Process()
       initial_memory = process.memory_info().rss
       
       for _ in range(ITERATION_COUNT):
           # 処理実行とクリーンアップ
           
       final_memory = process.memory_info().rss
       memory_increase = (final_memory - initial_memory) / (1024 * 1024)
       assert memory_increase < LEAK_THRESHOLD
   ```

2. 継続的操作
   ```python
   async def test_continuous_operation():
       """継続的な操作テスト"""
       start_time = time.time()
       error_count = 0
       operation_count = 0
       
       while time.time() - start_time < DURATION:
           try:
               # 処理実行
               operation_count += 1
           except Exception:
               error_count += 1
           
           await asyncio.sleep(INTERVAL)
       
       error_rate = error_count / operation_count
       assert error_rate < ERROR_THRESHOLD
   ```

### テスト設定
1. マーカー定義
   ```python
   def pytest_configure(config):
       """テストマーカーの登録"""
       config.addinivalue_line(
           "markers",
           "performance: パフォーマンステスト"
       )
       config.addinivalue_line(
           "markers",
           "stability: 安定性テスト"
       )
   ```

2. 共通フィクスチャ
   ```python
   @pytest.fixture(scope="session")
   def test_data():
       """テストデータの準備"""
       return generate_test_data()
   
   @pytest.fixture(autouse=True)
   def cleanup():
       """テスト後のクリーンアップ"""
       yield
       cleanup_resources()
   ```

## パフォーマンス監視パターン

### メトリクス収集
1. 時間計測
   ```python
   class Timer:
       def __enter__(self):
           self.start = time.time()
           return self
       
       def __exit__(self, *args):
           self.end = time.time()
           self.duration = self.end - self.start
   ```

2. メモリ監視
   ```python
   class MemoryMonitor:
       def __init__(self):
           self.process = psutil.Process()
       
       def get_memory_usage(self):
           return self.process.memory_info().rss
       
       def check_increase(self, initial, final):
           return (final - initial) / (1024 * 1024)  # MB
   ```

### レポート生成
1. テスト結果フォーマット
   ```python
   def format_test_result(name, duration, memory_usage):
       return {
           "test_name": name,
           "duration": duration,
           "memory_usage": memory_usage,
           "timestamp": time.time()
       }
   ```

2. 結果保存
   ```python
   def save_test_results(results):
       with open("test_results.json", "a") as f:
           json.dump(results, f)
           f.write("\n")
   ``` 