# Google Agent-to-Agent (A2A) プロトコル評価ノート

## 1. 調査目的

- 現行プロジェクトの構想段階において、将来的に複数の特化型AIエージェントを開発・連携させる可能性を視野に入れ、そのための標準プロトコル候補としてGoogle A2Aプロトコルの概要、提供されているサンプルコード、主要な利用パターン、および本プロジェクトへの適合可能性を評価するための基礎情報を収集する。
- A2Aプロトコルが持つ機能や特性が、現時点で想定されるエージェント間連携の要件（もしあれば）に対してどのような利点や課題をもたらしうるかを把握する。

## 2. A2Aプロトコル概要

- Googleが提唱する、異なるAIエージェントフレームワークやシステム間で、能力の発見、タスクの委任、データの交換などを標準化された方法で行うためのオープンプロトコル。
- 主にJSON-RPC 2.0 over HTTP(S) をベースとして通信を行う。
- **主要コンセプト**:
    - **エージェントカード (AgentCard)**: 各エージェントが自身の情報（名前、説明、エンドポイントURL、提供スキル、認証要件、対応機能など）をJSON形式で公開するための標準化されたメタデータ。これにより、他のエージェントやクライアントがエージェントを発見し、その能力を理解できる。
    - **スキル (Skills)**: エージェントが実行可能な具体的な能力や提供するサービスの定義。入力形式、出力形式、期待される動作などが記述される。
    - **タスク (Task)**: クライアントからエージェントへ依頼される具体的な処理要求。一意のIDを持ち、開始から完了 (または失敗・キャンセル) までの一連の状態 (例: `submitted`, `working`, `input-required`, `completed`, `failed`) を通じて管理される。
    - **メッセージ (Message)**: タスクの実行中におけるクライアントとエージェント間の具体的なやり取り。メッセージには役割（`user` または `agent`）があり、内容はテキスト、ファイル、構造化データ（JSON）など様々な形式 (`TextPart`, `FilePart`, `DataPart`, `Artefact`) で構成される。
- [公式GitHubリポジトリ: google/A2A](https://github.com/google/A2A)
- 参考記事:
    - [Google Agent-to-Agent (A2A) Protocol Explained — with Real Working Examples (Shamim Bhuiyan, Medium)](https://medium.com/@shamim_ru/google-agent-to-agent-a2a-protocol-explained-with-real-working-examples-99e362b61ba8)
    - [A2A Python Tutorial — Comprehensive Guide (Cheng Zhang, Medium)](https://medium.com/@zh.milo/a2a-python-tutorial-comprehensive-guide-ffc4a7d36a99)

## 3. `google/A2A` GitHubリポジトリ `samples/python/agents/` 配下の主要サンプル分析

[参考記事: Getting Started with Google A2A: A Hands-on Tutorial for the Agent2Agent Protocol (Heiko Hotz, Medium)](https://medium.com/google-cloud/getting-started-with-google-a2a-a-hands-on-tutorial-for-the-agent2agent-protocol-3d3b5e055127) - この記事では、以下のサンプルが連携するデモUIが紹介されている。

### 3.1. `langgraph` サンプル
    - **フレームワーク**: LangGraph (LangChainベース)
    - **主なデモ内容**: 通貨換算エージェントとして、処理状況をリアルタイムでストリーミング応答する。
    - **A2Aコンセプト実証**: `tasks/sendSubscribe` APIコール、サーバーセントイベント (SSE) を利用した非同期メッセージストリーミング。`capabilities.streaming: true` の活用。
    - **示唆**: 長時間実行タスクや、進捗の可視化が重要な場合に有効なパターン。

### 3.2. `crewai` サンプル
    - **フレームワーク**: CrewAI
    - **主なデモ内容**: 画像生成エージェントとして、結果をファイルとして返す。
    - **A2Aコンセプト実証**: `FilePart` を含む `Artefact` を利用したバイナリデータ（画像ファイルなど）の交換。
    - **示唆**: レポート生成、データエクスポートなど、ファイル形式での成果物が必要な場合に適用可能。

### 3.3. `google_adk` サンプル
    - **フレームワーク**: Google Agent Development Kit (またはそれに類するGoogle製ツール)
    - **主なデモ内容**: 経費精算エージェントとして、ユーザーに追加情報（日付、金額、目的など）を要求するインタラクティブなフォームを表示。
    - **A2Aコンセプト実証**: `DataPart` を利用した構造化データ（フォーム定義）の送信、およびフォーム入力結果の受信。タスクの `input-required` 状態の活用。
    - **示唆**: タスク実行にユーザーの追加入力や選択が必要な場合に、リッチなインタラクションを提供。

### 3.4. その他に存在しうるサンプルカテゴリとその意義
    - **`basic_agent` / `echo_agent`**: A2Aの最小構成を理解するための基本形。
    - **`llm_integration_agent` (例: `ollama_agent`)**: 特定のLLMをA2Aインターフェースでラップし、A2Aネットワーク内でLLMの能力を利用可能にする。
    - **`tool_specific_agent` (例: `calculator_agent`)**: 単純なツールやAPIをA2Aスキルとして提供。
    - **`agent_as_client_sample`**: あるエージェントが他のA2Aエージェントを利用して自身のタスクを達成する、より高度な連携パターン。

## 4. 主要な学習ポイントと本プロジェクトへの考察

- **標準化された連携**: A2Aは、異なる技術基盤で構築されたエージェント間でも、統一された方法で能力を公開し、タスクを依頼し、情報を交換する手段を提供する。これにより、各エージェントを専門性の高い独立したコンポーネントとして開発し、それらを柔軟に組み合わせることが可能になる。
- **多様なデータ形式**: 単純なテキストだけでなく、ファイルや構造化データ（フォームなど）も扱えるため、より複雑で実用的なユースケースに対応できる。
- **非同期処理とストリーミング**: 長時間かかる処理や、リアルタイム性が求められる対話にも対応可能な設計となっている。
- **本プロジェクトでの検討ポイント (構想段階)**:
    - 現状想定している複数のAI機能（もしあれば）を、独立したA2Aエージェントとして開発・分離することで、開発の分担、保守性の向上、特定機能の専門化といったメリットが得られるか。
    - 将来的に外部のA2A準拠エージェントと連携する可能性はあるか。あるいは、本プロジェクトで開発するエージェント群を外部に公開する可能性はあるか。
    - A2Aプロトコルの学習コストや実装の複雑さが、期待されるメリットに見合うか。他の連携手段（カスタムAPI、メッセージキューなど）と比較してどうか。

## 5. 参考資料リンク集

- **公式リポジトリ**:
    - [google/A2A (GitHub)](https://github.com/google/A2A)
    - [A2A Protocol Specification (GitHub)](https://github.com/google/A2A/tree/main/specification/json)
- **解説記事・チュートリアル**:
    - [Heiko Hotz - Getting Started with Google A2A (Medium)](https://medium.com/google-cloud/getting-started-with-google-a2a-a-hands-on-tutorial-for-the-agent2agent-protocol-3d3b5e055127)
    - [Cheng Zhang - A2A Python Tutorial — Comprehensive Guide (Medium)](https://medium.com/@zh.milo/a2a-python-tutorial-comprehensive-guide-ffc4a7d36a99)
    - [Shamim Bhuiyan - Google Agent-to-Agent (A2A) Protocol Explained — with Real Working Examples (Medium)](https://medium.com/@shamim_ru/google-agent-to-agent-a2a-protocol-explained-with-real-working-examples-99e362b61ba8)

## 6. 今後の検討事項 (プロジェクト固有)

- プロジェクトの初期段階（要件定義、基本設計フェーズ）において、複数のAIコンポーネント間の連携方式を検討する際に、A2Aプロトコルを連携オプションの一つとして正式にリストアップする。
- もし、小規模なプロトタイピングが可能であれば、最も関連性の高そうなサンプル（例: 基本的なLLM連携エージェントや、シンプルなツールエージェント）を実際に動作させ、A2Aの概念と実装の感触を掴む。
- A2Aプロトコルの成熟度、コミュニティの活発さ、利用可能なライブラリやツール状況を引き続き注視する。
- プロジェクトで想定される具体的なエージェント間インタラクションのシナリオをいくつか描き出し、それがA2Aプロトコルでどのように実現できるかを机上でシミュレーションしてみる。 