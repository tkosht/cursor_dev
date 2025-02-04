# 開発ルール集

# --- 基本ルール ---
basic_rules:
  - 実装や修正をしたら、必ず app/ 全体で以下をチェックしてください。修正の繰り返しにより、整合性やルールが遵守されていない可能性が高いためです。 以下のそれぞれに対して、本当にその修正や対応でよいのか、3段階の推敲を繰り返してください。
    1. 各ファイル・各クラス・各メソッドに対して、要件定義書や各種設計書と対応が取れていますか？  無駄、モレはないですか？
      1-1. DRY原則、SOLID原則、YAGNI原則、KISS原則すべてに従っていますか？
      1-2. その場しのぎの修正や実装になっていないですか？ デグレしていないですか？
      1-3. 無駄なメソッドや不要な実装はありませんか？
      1-4. 本当に無駄かどうかも慎重に丁寧に確認しましたか？
    2. 機能・結合テストでのモックは禁止です。モックを作った機能・結合テストは削除してください。  

env_file:
  - `.env` の参照および編集を禁止
  - Python プログラムを介してのみ参照のみを許可

# --- Pythonコード品質（python_code_quality） ---
python_coding_rules:
  basic_conventions:
    - "Python 3.10～3.12 を使用。"
    - "ライブラリは poetry 管理。"
    - "DRY、SOLID、YAGNI、KISSのすべての原則を遵守。"
  coding_conventions:
    - "snake_case（変数・関数）、PascalCase（クラス）、UPPER_SNAKE_CASE（定数）。"
    - "プライベートには先頭アンダースコアを付加。"
    - "docstring は Google スタイル、typing モジュールを使わない型ヒントを積極利用。"
    - "1行79文字以内、インデント4スペース。"
  must_rules:
    - "コードに環境変数や.env, .env.test の値を直接記録してはならない。"
    - "結合・統合テストでは、.env.test を参照。"

# --- コメントルール（comment_rules） ---
comment_rules:
  - "コメントに、テスト対応や要件などを含めて、なぜその実装でなければならないかを記載。"
  - "そうでない場合は、コメントになぜその実装にしたのかとその実装のメリット・デメリットを記載。"

# --- エラー解析（error_analysis） ---
error_analysis:
  description: "障害時は対象部分と周辺を調査し、アブダクションで原因を特定・解消。"
  rules:
    - "データ、ログ、実装、設定などの利用可能なすべての客観情報を元に直接・根本的要因を追究し、関連箇所も洗い出す。"
    - "修正の前に必ず docs/development/code_status.md を参照し、コード開発状況を確認。"
    - "局所修正だけでなく関連コードも含めて impact analysis（影響範囲分析）を実施し、無駄を省く。"
    - "import エラーが発生した場合は、本当にインポートすべきか、呼び出し側を改修すべきかを精査・整理した上で適切に修正。"
    - "安易にコード追加や削除をせず、本当に追加・削除すべきか、変更すべきか代替案はないか、推敲に推敲を重ねた上で適切に修正。最新の実装を参照して、コードの修正を行う。"
    - "**★★外部接続エラーも含め、まずは自らの実装・設定を優先的に点検し、外部要因と断定する前に可能な限り原因を切り分けること。★★**"
    - "3回以上解決できない場合は docs/errors/ と docs/fixes/ に [date_format].md を作成し記録。"

# --- テスト実行（testing_rules） ---
testing_rules:
  - "pytest で デバッグログが精緻に出力されるようコマンドを調整してテストを実行。"
  - "カバレッジレポートを出力し、目標カバレッジを下回る場合はテストコードや実装コードを見直す。"
  - "すべてのテストファイル・テストケースがPASSし、ユニットテストカバレッジ80%以上で自動完了。"
  - "エラー発生時は error_analysis に従う。"
  - "回帰テストは、一部だけのテストを禁止し、すべてのテストケースを対象に実行しすべてPASSすること。"
