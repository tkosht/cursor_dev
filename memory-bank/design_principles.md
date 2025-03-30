# 設計・実装原則

## 基本原則
*   **KISS (Keep It Simple, Stupid):** シンプルで理解しやすい設計・コードを心がける。
*   **DRY (Don't Repeat Yourself):** コードの重複を避け、共通化・再利用可能なモジュールを作成する。
*   **YAGNI (You Aren't Gonna Need It):** 現時点で不要な機能は実装しない。
*   **SOLID原則 (クラス設計):**
    *   **S**ingle Responsibility Principle (単一責任の原則)
    *   **O**pen/Closed Principle (開放/閉鎖の原則)
    *   **L**iskov Substitution Principle (リスコフの置換原則)
    *   **I**nterface Segregation Principle (インターフェース分離の原則)
    *   **D**ependency Inversion Principle (依存性逆転の原則)
*   **明確性:** コードは意図が明確に伝わるように記述する（命名規則、コメント、docstring）。
*   **保守性:** 将来の変更やデバッグが容易になるように考慮する。
*   **テスト容易性:** 単体テストがしやすいように設計する（依存性の注入など）。

## コーディング規約
*   [python.mdc](mdc:.cursor/rules/python.mdc) に定義された規約を厳守する。
    *   Type Hint, black, flake8, isort, Google Docstrings, 命名規則, etc.

## セキュリティ
*   [project.mdc](mdc:.cursor/rules/project.mdc) のセキュリティルールを遵守する。
    *   機密情報の扱いに注意し、環境変数を利用する。
    *   入力値のバリデーション、エスケープ処理を適切に行う。

## その他
*   (プロジェクト固有の設計原則があれば追記) 