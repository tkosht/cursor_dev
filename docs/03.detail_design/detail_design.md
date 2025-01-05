# 詳細設計書

本書では、「docs/02.basic_design/basic_design.md」で示した基本設計をもとに、各コンポーネント（クラス・メソッド）の詳細な役割やデータフロー、インターフェース仕様などを示します。  
「docs/01.requirements/requirements.md」の要件を踏まえ、さらに「development_rules.md」のルールに準拠しながら、DRY/SOLID/YAGNI/KISS 原則を遵守する形で設計を行っています。

---

## 1. アプリケーション全体構造

- app/  
  - content_fetcher.py  
  - content_parser.py  
  - gemini_analyzer.py  
  - market_analyzer.py  
  - neo4j_manager.py  
  - knowledge_repository.py  
  - ほか共通ユーティリティファイル（utils/ ディレクトリなど）  
- tests/  
  - (各クラス・メソッド用のテストスクリプト)

---

## 2. ContentFetcher

### 2.1 クラス概要
- ファイル名: app/content_fetcher.py
- クラス名: ContentFetcher
- 役割: 指定されたURLもしくはファイルパスからHTML等のソースを取得する。

### 2.2 メソッド一覧

--------------------------------------------------------------------------------
| メソッド名         | 引数                              | 戻り値                   | 概要                                            |
|--------------------|-----------------------------------|--------------------------|-------------------------------------------------|
| fetch_html         | url: str                          | str                      | HTTPでアクセスしHTMLソースを取得。             |
| _verify_response   | response_status_code: int         | bool                     | ステータスコードを確認、200系以外ならFalseを返す|
| fetch_from_file    | file_path: str                    | str                      | ローカルファイルからテキストを読み込み、返す。 |
--------------------------------------------------------------------------------

### 2.3 メソッド詳細

#### 2.3.1 fetch_html(url: str) -> str
- 処理内容:  
  1. HTTPリクエストを送信  
  2. タイムアウトまたはエラー発生時はリトライ（リトライ回数を決め、一定回数失敗で例外発生）  
  3. ステータスコードを確認（_verify_responseで確認）  
  4. 問題ない場合はレスポンスボディを文字列として返却  

- エラー時のハンドリング:  
  - タイムアウト・接続エラーは適宜ログ出力し、例外（例: ConnectionError）を送出する。  
  - ステータスコード不正の場合は ValueError などを送出。

#### 2.3.2 _verify_response(response_status_code: int) -> bool
- 処理内容:  
  - 200～299の範囲内かチェックし、範囲外なら False を返す。

#### 2.3.3 fetch_from_file(file_path: str) -> str
- 処理内容:  
  1. ローカルファイルを開き、文字列として読み込む。  
  2. 読み込み失敗時は FileNotFoundError や IOError 等を送出。  

---

## 3. ContentParser

### 3.1 クラス概要
- ファイル名: app/content_parser.py
- クラス名: ContentParser
- 役割: 取得したHTMLやテキストから本文・見出し等を抽出し、不要要素を削除して正規化する。

### 3.2 メソッド一覧

--------------------------------------------------------------------------------
| メソッド名               | 引数               | 戻り値         | 概要                                                 |
|--------------------------|--------------------|----------------|------------------------------------------------------|
| parse_html               | raw_html: str      | Dict[str, str] | HTMLをパースし本文やタイトル、日付などを抽出して返す。|
| _remove_unwanted_tags    | soup: BeautifulSoup| BeautifulSoup  | 広告やスクリプトなど不要なタグを除外する。           |
| _normalize_text          | text: str         | str            | 改行や空白などを整形して見やすい文章にする。         |
--------------------------------------------------------------------------------

### 3.3 メソッド詳細

#### 3.3.1 parse_html(raw_html: str) -> Dict[str, str]
- 処理内容:  
  1. BeautifulSoup 等を用いてHTMLをパース。  
  2. _remove_unwanted_tags() を呼び出して不要要素を除去。  
  3. タイトル・本文・日付等を抽出し、_normalize_text() で整形。  
  4. 返却用の dict 例: {"title": "...", "content": "...", "date": "..."}  

- エラー時のハンドリング:  
  - HTML解析失敗時は ValueError を送出し、上位でキャッチ・ログ出力。

#### 3.3.2 _remove_unwanted_tags(soup: BeautifulSoup) -> BeautifulSoup
- 処理内容:  
  - スクリプトタグ・広告セクションなどを除外。  
  - 必要に応じて NavigableString の不要部分もフィルタリング。

#### 3.3.3 _normalize_text(text: str) -> str
- 処理内容:  
  - 改行文字や全角スペースの統一。  
  - 「連続スペース」削除などを行い、本文を読みやすい形に整形。

---

## 4. GeminiAnalyzer

### 4.1 クラス概要
- ファイル名: app/gemini_analyzer.py
- クラス名: GeminiAnalyzer
- 役割: Gemini(gemini-2.0-flash-exp)のAPIを呼び出し、解析結果を得る。

### 4.2 メソッド一覧

--------------------------------------------------------------------------------
| メソッド名         | 引数                        | 戻り値                | 概要                                                      |
|--------------------|-----------------------------|-----------------------|-----------------------------------------------------------|
| analyze_content    | content: str               | Dict[str, Any]        | Geminiに問い合わせ、内容を解析した結果をdictで返す。     |
| _construct_prompt  | content: str               | str                   | contentを基にプロンプトを生成する。                       |
| _call_gemini_api   | prompt: str                | str                   | 実際にHTTPリクエストを発行し、レスポンスを文字列で取得。   |
--------------------------------------------------------------------------------

### 4.3 メソッド詳細

#### 4.3.1 analyze_content(content: str) -> Dict[str, Any]
- 処理内容:  
  1. _construct_prompt(content) でプロンプト文字列を生成。  
  2. _call_gemini_api(prompt) でGeminiに問い合わせ、結果を受け取る。  
  3. レスポンスをJSON等に変換して要点やトレンドなどを抽出し、Dictにまとめて返す。  

- セキュリティ上の考慮:
  - APIキーは .env 中の GOOGLE_API_KEY_GEMINI を os.getenv() 経由で取得。  
  - ログ出力にAPIキーを含めない。

#### 4.3.2 _construct_prompt(content: str) -> str
- 処理内容:  
  - 入力コンテンツを含めた指示文を整形し、ノイズ削除の方針や解析観点などを付与する。  
  - Geminiが広告や不要要素を混ぜないように補足情報を入れる。

#### 4.3.3 _call_gemini_api(prompt: str) -> str
- 処理内容:  
  1. Geminiエンドポイント（gemini-2.0-flash-exp）へHTTPリクエストを送信。  
  2. レスポンスを文字列で取得して返す。

- エラー時のハンドリング:
  - 接続エラーやステータスコードエラーを検出し、例外を送出。  
  - リトライは必要に応じて実施。

---

## 5. MarketAnalyzer

### 5.1 クラス概要
- ファイル名: app/market_analyzer.py
- クラス名: MarketAnalyzer
- 役割: GeminiAnalyzerから得た結果を元に、市場影響度やエンティティ、関係性などを抽出し、最終形式（dictなど）に再まとめる。

### 5.2 メソッド一覧

--------------------------------------------------------------------------------
| メソッド名              | 引数                          | 戻り値             | 概要                                                                  |
|-------------------------|-------------------------------|--------------------|-------------------------------------------------------------------------|
| process_gemini_output   | gemini_result: Dict[str, Any] | Dict[str, Any]     | GeminiAnalyzerの解析結果から市場影響度、関連企業、関係性などを抽出する。|
| _extract_entities       | gemini_result: Dict[str, Any] | List[Dict[str, str]] | 企業名や製品名などのエンティティリストを抽出する。                      |
| _detect_relationships   | gemini_result: Dict[str, Any] | List[Dict[str, Any]] | エンティティ間の関係性と強度を特定し、リストとして返す。                |
| _calculate_impact_score | gemini_result: Dict[str, Any] | float              | 市場影響度(0.0～1.0)を数値で算出する。                                  |
--------------------------------------------------------------------------------

### 5.3 メソッド詳細

#### 5.3.1 process_gemini_output(gemini_result: Dict[str, Any]) -> Dict[str, Any]
- 処理内容:
  1. _extract_entities() でエンティティ（企業名、製品etc.）を抽出。  
  2. _detect_relationships() でエンティティ間の関係性を抽出。  
  3. _calculate_impact_score() で市場影響度を算出。  
  4. 結果を{"entities": [...], "relationships": [...], "impact": float, ...} のようなdict でまとめる。

#### 5.3.2 _extract_entities(gemini_result: Dict[str, Any]) -> List[Dict[str, str]]
- 処理内容:
  - GeminiAnalyzerからのキーやフラグをもとに、「企業名」「キーワード」「製品」を抽出。  
  - 文字列クリーニングや重複除去などを行い、List[Dict]形式にまとめる。

#### 5.3.3 _detect_relationships(gemini_result: Dict[str, Any]) -> List[Dict[str, Any]]
- 処理内容:
  - エンティティ同士が「INFLUENCES」「COMPETES」「PARTICIPATES」など、どの関係に当てはまるかを判定。  
  - 関係の説明や強度を含めたDictをリストへ。

#### 5.3.4 _calculate_impact_score(gemini_result: Dict[str, Any]) -> float
- 処理内容:
  - Gemini出力に含まれる市場影響度やLLM上のスコアを総合し、0.0～1.0の範囲に正規化して返す。

---

## 6. Neo4jManager

### 6.1 クラス概要
- ファイル名: app/neo4j_manager.py
- クラス名: Neo4jManager
- 役割: Neo4jへの接続管理および生のCypherクエリ実行。クエリパラメータ化によりCypherインジェクションを防ぐ。

### 6.2 メソッド一覧

--------------------------------------------------------------------------------
| メソッド名         | 引数                              | 戻り値            | 概要                                                 |
|--------------------|-----------------------------------|-------------------|------------------------------------------------------|
| __init__           | なし (内部でos.getenv取得)         | None              | クラス生成時にNeo4jへ接続する初期化処理を行う。      |
| create_node        | label: str, properties: dict       | None              | 指定ラベル・プロパティを持つノードを作成する。       |
| create_relationship| start_id: str, end_id: str, rel_type: str, properties: dict | None | 指定ノード同士にリレーションを作成する。             |
| update_node        | node_id: str, properties: dict     | None              | 指定ノードのプロパティを更新する。                   |
| close_connection   | なし                               | None              | 接続解除                                            |
--------------------------------------------------------------------------------

### 6.3 メソッド詳細

#### 6.3.1 __init__()
- 処理内容:
  1. os.getenv("neo4j_user"), os.getenv("neo4j_pswd") 等の環境変数を取得。  
  2. パスワードはログやLLMへは出力禁止。  
  3. Neo4jドライバ（例: neo4j.GraphDatabase.driver）を生成しセッション確立。

- セキュリティ:
  - ユーザー名やパスワードはコミットやログへの記載禁止。  
  - 予期せぬ外部要因と断定する前に自ら設定を確認する。

#### 6.3.2 create_node(label: str, properties: dict) -> None
- 処理内容:
  - "CREATE (n:Label { ... }) RETURN n" のような形でCypherクエリを実行。  
  - properties はパラメータバインドで安全に設定。  

#### 6.3.3 create_relationship(
    start_id: str,
    end_id: str,
    rel_type: str,
    properties: dict
  ) -> None
- 処理内容:
  - 指定ノードID（_idなどユニークプロパティ）をもとに、"MATCH (a), (b) WHERE a.id=$start_id AND b.id=$end_id CREATE (a)-[:REL_TYPE { ... }]->(b)" を実行。  
  - rel_type は "INFLUENCES" などを想定。  
  - 同様にパラメータバインドを使い、インジェクションを防ぐ。

#### 6.3.4 update_node(node_id: str, properties: dict) -> None
- 処理内容:
  - Node IDをキーにマッチし、必要なプロパティを更新。  
  - "MATCH (n) WHERE n.id=$node_id SET n += $properties" など。

#### 6.3.5 close_connection() -> None
- 処理内容:
  - セッションをクローズし、ドライバをクローズ。

---

## 7. KnowledgeRepository

### 7.1 クラス概要
- ファイル名: app/knowledge_repository.py
- クラス名: KnowledgeRepository
- 役割: Neo4jManagerのメソッドを利用して、分析結果のCRUD操作をまとめて行う。重複チェックや時系列管理等をカプセル化。

### 7.2 メソッド一覧

--------------------------------------------------------------------------------
| メソッド名        | 引数                                   | 戻り値           | 概要                                       |
|-------------------|----------------------------------------|------------------|--------------------------------------------|
| store_analysis    | analysis_result: Dict[str, Any]        | None             | MarketAnalyzerの出力をもとにノードやリレーションシップを作成。 |
| _check_duplicate  | node_label: str, node_id: str          | bool             | 既存ノード重複チェック (同一IDかどうか)。  |
| _update_timestamp | node_label: str, node_id: str          | None             | クエリで timestamp プロパティを更新。      |
--------------------------------------------------------------------------------

### 7.3 メソッド詳細

#### 7.3.1 store_analysis(analysis_result: Dict[str, Any]) -> None
- 処理内容:
  1. analysis_result から "entities", "relationships", "impact" などを取得。  
  2. "entities" をループし、既存ノード有無をチェック(_check_duplicate)。  
     - 重複がなければNeo4jManager.create_node() で作成。  
     - あれば update_node() で更新。  
     - 必要に応じて timestamp を _update_timestamp()。  
  3. "relationships" をループし、start_id, end_id, rel_type などで Neo4jManager.create_relationship() を呼ぶ。  
  4. すべて完了後、問題なければ終了。

#### 7.3.2 _check_duplicate(node_label: str, node_id: str) -> bool
- 処理内容:
  - Neo4jへクエリを送り、該当 id を持つノードが存在するかをチェック。  
  - 存在すれば True、なければ False を返す。

#### 7.3.3 _update_timestamp(node_label: str, node_id: str) -> None
- 処理内容:
  - 現在時刻（Pythonの datetime.now() など）を "YYYY-MM-DD-HH-MM-SS" 形式で生成し、ノードの timestamp プロパティを上書き。

---

## 8. ユーティリティ・共通処理

- 共通例外ハンドリング:  
  - エラー解析（error_analysis）ルールに従い、例外の特定とログ出力を行うための関数。  
- ログ設定:  
  - Pythonの logging モジュールで INFO/DEBUG/ERROR ログを出力。  
  - 機密情報が含まれないように注意。

---

## 9. データフロー

1. ContentFetcher がURLまたはファイルからHTMLソースを取得 (fetch_html or fetch_from_file)。  
2. ContentParser がHTMLソースを解析し、本文やタイトルを抽出。  
3. GeminiAnalyzer が抽出結果のテキストをGeminiにわたし、解析結果を取得。  
4. MarketAnalyzer がGemini解析結果からエンティティ・関係性・市場影響度を抽出。  
5. KnowledgeRepository がその結果をNeo4jManager を介してNeo4jに保存・更新。  

---

## 10. テスト設計の補足

- ユニットテスト(app/)  
  - ContentFetcherのfetch_html, fetch_from_file などをテストし、接続エラー・想定外URLなどの例外ケースを検証。  
  - ContentParserはHTML要素を含む仮の文字列を入力に、本文抽出・不要タグ削除が正しく行われるかを確認。  
  - GeminiAnalyzerはHTTPリクエスト部の疎通に加え、mockで固定レスポンスを返さずに単体テストを行うこと（※機能・結合テストでモック禁止のため、単体では内部ロジック最小化テスト可）。  
  - MarketAnalyzerはGemini出力の形を想定したdictを入力に、エンティティ抽出・関係性抽出・impact計算などが正しいか確認。  
  - Neo4jManagerはローカルやテスト用のNeo4jを用いて接続テストし、クエリが正常に実行されるかをチェック。  
- 結合テスト、統合テスト(tests/)  
  - 実際にGeminiサービスにアクセスし、HTML→ContentParser→GeminiAnalyzer→MarketAnalyzer→KnowledgeRepository という一連の流れが動作するか。  
  - 外部URL取得を行っても、モックやスタブの利用は禁止（実際のURL・APIエンドポイントを使用）。

---

## 11. 運用上の留意点
- Pythonバージョンは 3.10～3.12 を使用し、ライブラリ管理は Poetry。  
- フォーマッターは black、Linterは flake8。  
- カバレッジ80％以上を目指し、常に DRY/SOLID/YAGNI/KISS 原則を確認。  
- セキュリティや環境変数関連は .env のみで管理し、os.getenv() 以外のアクセスや.env内容を表示しない。

以上の詳細設計をもとに、ワークフロー定義(「step_number: 2」以降)のプロセスに従って実装・テストを着実に進めてください。
