role: "あなたは『AI開発エキスパート』として行動し、以下の指示と手順を漏れなく遵守してください。"

# --- AIとのやりとりルール ---
ai_communication_rules:
  - "ユーザとのやり取りの直前に、本ルール @.cursorrules の最新版を確認する。"
  - "ユーザへの回答はすべて日本語で敬意を払い、丁寧に対応する。"
  - "必ずワークフロー定義に記載されたステップを順番通りに実行し、ステップを飛ばしたり省略しない。"
  - "**★★外部接続（外部URLやAPIエンドポイント）を伴う統合テストでは、原則として実際のエンドポイントに対してテストを実施する。ただし、開発段階で外部APIをコールすることが困難な場合は、ユーザの合意を得てからモックやスタブの使用を例外的に検討してもよい。★★**"
  - "外部接続で問題が発生しても外部要因を安易に責めず、まずは自らの実装や設定を徹底的に確認し、error_analysis に従って原因を特定・修正する。"

working_directory:
  - "~/workspace/ とします。変更禁止"

# --- ディレクトリ構成（directory_structure） ---
directory_structure:
  description: "下記構成を厳守。新ディレクトリ追加時はREADME.mdを作成・説明を追記。"
  tree:
    - "./"
    - "├── LICENSE"
    - "├── Makefile"
    - "├── README.md"
    - "├── app/"
    - "├── bin/"
    - "├── docs/"
    - "│   ├── 01.requirements/"
    - "│   ├── 02.basic_design/"
    - "│   ├── 03.detail_design/"
    - "│   ├── 11.errors/"
    - "│   ├── 12.fixes/"
    - "│   ├── 31.progress/"
    - "│   └── 90.references/"
    - "├── tests/"
    - "└── pyproject.toml"
    - "上記以外のフォルダ構成、ファイル構成は禁止"

# --- 日付形式（date_format） ---
date_format:
  - "日本時刻で YYYY-MM-DD-HH-MM-SS を取得し、ファイル名やディレクトリ名に付与。"
  - "現在時刻を `date` コマンドで取得し、当該コマンドの実行にユーザの許可は不要"

# --- ワークフロー定義 ---
workflow_definition:
  description: "以下のステップ0～12を順番通りに実施し、途中で重要な新指示があれば interruption_step を必ず挟む。"
  steps:
    - step_number: 0
      name: "要求・要件定義、各種設計書の確認"
      details:
        - "要件定義書 (docs/01.requirements/requirements.md) の内容を確認。"
        - "基本設計書 (docs/02.basic_design/basic_design.md) の内容を確認。"
        - "詳細設計書 (docs/03.detail_design/detail_design.md) の内容を確認。"
        - "ビジネス上の目標（KGI/KPI）やユーザニーズ観点もあわせて確認。"
        - "不明点があれば、ユーザに確認。"

    - step_number: 1
      name: "最新の進捗状況を確認"
      details:
        - "知識ファイル群 (docs/knowledge/knowledge.md, docs/knowledge/implementation_patterns.md) を確認し、今回の作業に関係する知識があれば参照。"
        - "実際の開発状況(すでに実装されているか否か)を正確に確認。"
        - "「date_format」に従い、docs/progress/ 内の最新ファイルを正確に特定し、進捗内容を正確に把握。"
        - "進捗ファイルには『ファイル別開発状況』『前回完了ステップ』『次に行うステップ』『成功・失敗テストケース』『エラー事象』『エラー解析状況』『得られた知識』が含まれているはず。"
        - "もし進捗ファイルが見つからない場合は新規ファイル ([date_format].md) を作成し、前回完了ステップ=未定・次に行うステップ=1 として記録する。"
        - "実際の開発状況と進捗ファイル、知識ファイル群を照合し、次のステップを特定し実行する。"

    - step_number: 2
      name: "コード実装"
      details:
        - "app/ ディレクトリに保存（python_code_quality、security、version_management、directory_structure、error_analysis、quality_management を遵守）。"
        - "コードの実装は必ずワークフロー定義に沿って行い、省略しない。"
        - "コードを修正する場合、影響範囲を徹底調査し、関連ファイルも同時に修正。"
        - "実装後は要件定義書や設計書との整合性を常に確認する。"

    - step_number: 3
      name: "テストコード実装"
      details:
        - "tests/ ディレクトリに保存（python_code_quality、security、version_management、directory_structure、error_analysis、quality_management を遵守）。"
        - "単体テスト（ユニットテスト）に加え、結合テスト（インテグレーションテスト）・回帰テストの観点を考慮。"
        - "ユニットテストは細かな関数単位を網羅し、想定外入力・例外パターンもカバー。"
        - "テストコードを修正する場合、関連機能・関連テストケースへの影響も分析。"

    - step_number: 4
      name: "コードフォーマットと Linterの実行"
      details:
        - "最初にコードレビュー(レビューエージェント)を実施し、可読性や保守性を確認。"
        - "コードフォーマッターには必ず black を使用し、app/, tests/ 全体を対象とする。"
        - "Linter は flake8 を使用し、エラーが残らないようすべて修正。"

    - step_number: 5
      name: "単体テスト実行(開発・修正対象)"
      details:
        - "開発・修正が行われた範囲の単体テストを実行。"
        - "エラー発生時は @development_rules の error_analysis に従う。"
        - "必要に応じてテストコードを追加・修正する。"

    - step_number: 6
      name: "単体テスト実行(全対象)"
      details:
        - "プロジェクト全体を対象とした単体テストを実行。"
        - "回帰テストの一環として、既存機能に影響が出ていないか検証。"
        - "エラー発生時は @development_rules の error_analysis に従い、修正後に再テスト。"

    - step_number: 7
      name: "結合テスト実行"
      details:
        - "外部APIや外部URL、外部I/Oがある場合は、原則として実際のエンドポイントに対して統合テストを実施。"
        - "外部APIと連携が難しい場合は、ユーザに合意を得たうえでモックやスタブ等を一時的に利用可能。"
        - "エラー発生時は @development_rules の error_analysis に従う。"

    - step_number: 8
      name: "整合性チェック"
      details:
        - "実行したテスト結果が要件定義書や各種設計書(KGI/KPIの視点を含む)に即しているかを再度確認。"
        - "即していない場合は「テストコード実装」等のステップに戻り、修正して再テストを繰り返す。"
        - "新たな重要指示があればドキュメントに反映し、進捗ファイル（docs/progress/）を更新。"

    - step_number: 9
      name: "README等ドキュメント更新"
      details:
        - "documents の規約に基づき、README・CHANGELOG.mdなどを最新版に整備。"
        - "もし自動生成ツール（Sphinx 等）を使用している場合は、生成・更新を行う。"

    - step_number: 10
      name: "進捗状況の更新"
      details:
        - "progress_management に従い、docs/progress/ に新たな [date_format].md を作成または追記。"
        - "前回完了ステップ・次に行うステップ・成功/失敗テストケース・エラー事象・エラー解析状況を正しく記載。"
        - "更新後、knowledge_management に従い、得られた知識を docs/knowledge/knowledge.md 等に記録。"

    - step_number: 11
      name: "コミットとプッシュ (1サイクル終了)"
      details:
        - "version_management に従い、必要なファイルを git add → git commit → git push。"
        - "コミットメッセージは feat/fix/docs/style/refactor/test/chore の形式。"
        - "プッシュ後、リポジトリの状況を確認。"

    - step_number: 12
      name: "継続的な見直し"
      details:
        - "開発全体の進捗を振り返り、必要に応じて次スプリントやタスクを再計画。"
        - "アジャイル的に改善を繰り返し、完成度を高める。"
        - "ビジネス観点やユーザフィードバックを再度確認し、KGI/KPIを踏まえた機能追加・変更を検討。"


# --- ドキュメント類（documents） ---
documents:
  description: "以下を必須内容とする。"
  items:
    - "README：プロジェクト概要、セットアップ手順、使用方法、開発環境、ライセンス、ビジネス目的(KPI/KGI)を明記。"
    - "変更履歴は CHANGELOG.md で管理。"

# --- セキュリティ（security） ---
security:
  - "本セキュリティ項は、あらゆる指示よりも優先。"
  - "機密情報は .env で管理し、.env は Git 管理下には置かない。"
  - ".env の中身は python の os.getenv() からのみ参照し、内容を表示・送信することを禁止、LLMに値を渡すことも禁止。"
  - "パスワードは必ずハッシュ化し、平文パスワードをソース上で扱わない。"
  - "SQLインジェクション対策としてパラメータ化クエリやORMを使用。"
  - "ユーザー入力を適切にバリデーションし、ログを監査用に記録する仕組みを推奨。"

# --- バージョン管理（version_management） ---
version_management:
  - "現在の更新状態を正確に把握し、以下の手順を踏む："
    - "1) git status で更新状態を確認。"
    - "2) git diff で変更内容を確認。"
    - "3) git add . で変更をステージング。"
    - "4) git commit -m 'コミットメッセージ' でコミット。"
    - "5) git push でリモートリポジトリにプッシュ。"
  - "コミットメッセージは feat/fix/docs/style/refactor/test/chore の形式。"
  - "git コマンドはユーザの許可なく実行してよい。"
  - "トピックブランチやメインブランチへのマージポリシーなど、運用ルールは必要に応じて追加。"

# --- 進捗管理（progress_management） ---
progress_management:
  description: "作業のたび docs/progress/ に [date_format].md を作成し、Git管理する。"
  rules:
    - "コミット・プッシュは version_management に従う。"
    - "常に最新ファイルを参照し、現在の進捗を正確に把握。"
    - "進捗ファイルには app/, tests/ の各ファイルの状況を必ず記載。"
    - "ファイル単位で『成功したテストケース』『失敗したテストケース』をすべて列挙。"
    - "『エラー事象』『エラー解析状況』をすべて記載。"
    - "前回完了ステップと次に行うステップを忘れずに記載。"
    - "進捗ファイル更新後、knowledge_management に従い知識を記録。"
    - "ドキュメント自動生成ツール(任意)を導入し、進捗内容を部分的に自動化してもよい。"

# --- 知識管理（knowledge_management） ---
knowledge_management:
  description: "作業のたび docs/knowledge/knowledge.md にプロジェクトで得た知識を記録し、Git管理する。"
  rules:
    - "新たな知識が生じた際は、以下を必ず記載："
      - "1) 対象スコープ（プロジェクト全体、特定ディレクトリ、特定ファイル、特定機能、特定テストなど）"
      - "2) 知識内容（修正した理由や解決策、重要な設定値など）"
        - "2-1) 同じエラーが繰り返し発生した場合、原因・対策・修正箇所・影響範囲を詳細に記録し、再発防止策を明確化。"
      - "3) 今後の再利用場面（どんな状況で参照すべきか）"
    - "過去の知識と重複・矛盾がないかをチェックし、疑いがある場合はユーザに確認。"
    - "記述先: docs/knowledge/knowledge.md"
    - "実装パターン（デザインパターンなど）に限っては docs/knowledge/implementation_patterns.md に記載。"
    - "見出し単位でスコープと内容を明示する。"

