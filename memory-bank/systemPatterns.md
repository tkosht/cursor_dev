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