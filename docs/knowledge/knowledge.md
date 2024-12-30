# プロジェクトの知識ベース

## テスト関連

### 非同期処理のテスト
- スコープ：テストコード全般
- 知識内容：
  1. 非同期テストの基本設定
     - `@pytest.mark.asyncio`デコレータを使用
     - `pytest-asyncio`パッケージが必要
     - テストケース関数は`async def`で定義

  2. 非同期HTTPクライアントのテスト
     - `pytest-aiohttp`パッケージを使用
     - `aiohttp_client`フィクスチャでテストクライアントを取得
     - テストサーバーは`aiohttp.web.Application`で実装

  3. モックの設定
     - `AsyncMock`を使用して非同期メソッドをモック
     - コンテキストマネージャー（`__aenter__`と`__aexit__`）の適切な設定が必要
     - レスポンスは非同期関数化する

- 再利用場面：
  - 非同期処理を含むコードのテスト実装時
  - HTTPクライアントのテスト実装時
  - モックを使用したテスト実装時

### エラーハンドリングテスト
- スコープ：例外処理を含むコード全般
- 知識内容：
  1. 基本的なエラーパターン
     - ネットワークエラー：接続失敗、タイムアウト
     - レート制限：429ステータスコード
     - サーバーエラー：500番台のステータスコード

  2. テスト実装のポイント
     - 各エラーに対応する例外クラスを正確に指定
     - `pytest.raises`でエラー発生を検証
     - エラー発生時のシステム状態を確認（モニタリング、ログ等）

  3. テストデータの準備
     - エラー発生のタイミングを制御可能な形で実装
     - 実際のエラー状況を再現できるモックを用意
     - エッジケースも考慮したテストケースを準備

- 再利用場面：
  - エラーハンドリング機能の実装時
  - 外部サービスとの連携機能のテスト時
  - システムの耐障害性テスト時

### 同時実行制御のテスト
- スコープ：並行処理を含むコード全般
- 知識内容：
  1. 基本的なアプローチ
     - `asyncio.sleep`で処理時間をシミュレート
     - `asyncio.gather`で複数タスクを同時実行
     - 実行時間の計測で制御を検証

  2. テスト実装のポイント
     - 同時実行数の制限が正しく機能することを確認
     - リソース使用量の監視
     - デッドロックやレースコンディションの検出

  3. 検証項目
     - 処理の順序性
     - リソースの解放
     - エラー発生時の動作

- 再利用場面：
  - 並行処理の実装時
  - パフォーマンステスト時
  - リソース制御機能のテスト時

# 知識データベース

## XMLの名前空間処理
### スコープ
- プロジェクト全体
- 特に `app/crawlers/url_collector.py` の `_extract_urls_from_sitemap` メソッド

### 知識内容
1. サイトマップXMLの名前空間処理
   - 複数の名前空間パターンが存在する可能性がある
   - 標準的な名前空間: `http://www.sitemaps.org/schemas/sitemap/0.9`
   - 名前空間なしのケースにもフォールバックで対応する必要がある

2. ElementTreeでの名前空間を使用した要素検索
   ```python
   ns = {
       "default": "http://www.sitemaps.org/schemas/sitemap/0.9",
       "sm": "http://www.sitemaps.org/schemas/sitemap/0.9"
   }
   # 名前空間を使用した検索
   element.findall(".//{%s}loc" % namespace)
   ```

### 再利用場面
- XMLファイルの解析時、特に標準的な名前空間を持つXMLの処理
- サイトマップやRSSフィードなどの標準フォーマットの解析
- 複数の名前空間パターンに対応する必要がある場合

## URLの正規化と処理
### スコープ
- プロジェクト全体
- 特に `app/crawlers/url_collector.py`

### 知識内容
1. 相対パスと絶対URLの混在対応
   ```python
   from urllib.parse import urljoin
   
   # 相対パスを絶対URLに変換
   if not url.startswith(('http://', 'https://')):
       url = urljoin(base_url, url.lstrip('/'))
   ```

2. URLの正規化のベストプラクティス
   - スキーム（http/https）の判定
   - 相対パスの正規化
   - クエリパラメータの処理
   - フラグメント（#）の処理

### 再利用場面
- Webクローラーの実装時
- リンク収集機能の実装時
- URL操作が必要な任意の機能実装時

## 非同期処理のテスト
### スコープ
- テストコード全般
- 特に `tests/integration/test_url_collector.py`

### 知識内容
1. aiohttp_clientフィクスチャの活用
   ```python
   @pytest.fixture
   async def test_client(aiohttp_client, test_app):
       return await aiohttp_client(await test_app)
   ```

2. 同時実行数制限のテスト
   ```python
   start_time = asyncio.get_event_loop().time()
   tasks = [async_function() for _ in range(n)]
   await asyncio.gather(*tasks)
   end_time = asyncio.get_event_loop().time()
   assert end_time - start_time >= expected_time
   ```

3. タイムアウトのシミュレーション
   ```python
   async def handle_timeout(request):
       await asyncio.sleep(1)
       return web.Response(text="timeout")
   ```

### 再利用場面
- 非同期APIのテスト実装時
- 並行処理の制限テスト時
- ネットワーク関連の例外処理テスト時

## テストケースの柔軟性
### スコープ
- テストコード全般
- 特に統合テストやE2Eテスト

### 知識内容
1. 環境依存値の比較方法
   ```python
   # 固定値での比較を避ける
   assert url.endswith('/expected/path')
   assert any(url.endswith(path) for path in expected_paths)
   ```

2. テストサーバーの動的URL生成
   ```python
   base_url = str(request.url.origin())
   response_text = f"""
       <url><loc>{base_url}/path</loc></url>
   """
   ```

### 再利用場面
- 環境依存のテストケース実装時
- 動的なURLやパスを扱うテスト時
- マルチ環境対応のテスト実装時 