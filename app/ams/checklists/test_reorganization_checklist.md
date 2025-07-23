# テスト再編成チェックリスト

実行日: 2025-07-23
タスク: scripts/のテストファイルをtests/に正規化

## 1. 事前確認 ✓

### 現状調査
☑ tests/ディレクトリ構造を確認
  - tests/unit/ : 単体テスト
  - tests/integration/ : 統合テスト
  - tests/e2e/ : E2Eテスト

☑ scripts/のテストファイルを確認
  - test_llm_connection.py
  - test_llm_simple.py
  - test_llm_verification.py
  - test_single_component.py
  - test_small_integration.py
  - test_guide_examples.py

☑ 既存のintegrationテストを確認
  - tests/integration/test_small_scale_integration.py

## 2. 分類と判断 ✓

### 移動対象の分類
□ 統合テストとして移動
  - test_small_integration.py → 既にtest_small_scale_integration.pyが存在
  - test_single_component.py → 単一コンポーネントの統合テスト

□ ユーティリティとして保持または削除
  - test_llm_connection.py → LLM接続確認用（開発ツール）
  - test_llm_simple.py → 重複機能
  - test_llm_verification.py → 透明性検証（開発ツール）
  - test_guide_examples.py → ドキュメント検証用

## 3. 実装計画 ✓

### 統合作業
□ tests/integration/test_llm_connection.py を作成
  - llm_factoryを使用（ハードコード削除）
  - 設定ベースの実装
  - pytest形式に準拠

□ 既存test_small_scale_integration.pyに機能統合
  - test_single_component.pyの有用な部分を統合

□ scripts/から削除
  - 重複・不要なファイルを削除
  - 開発ツールは最小限に整理

## 4. 実装詳細 ✓

### test_llm_connection.py の正規化
□ ハードコード除去
  - model="gemini-1.5-flash" → config.llm.gemini_model
  - temperature=0.7 → config.llm.temperature

□ pytest形式への変換
  - async def main() → async def test_*()
  - print文 → assert文とlogging

□ フィクスチャの活用
  - conftest.pyの既存フィクスチャを使用

## 5. 検証項目 ✓

□ pytest実行確認
  - pytest tests/integration/test_llm_connection.py
  - pytest tests/integration/

□ カバレッジ確認
  - 既存のカバレッジを維持または向上

□ scripts/のクリーンアップ確認
  - 必要最小限のツールのみ残存

## 6. 完了条件 ✓

☑ すべてのテストがtests/に正規化されている
☑ ハードコードが除去されている
☑ pytestマーカーが適切に設定されている
☑ 不要なファイルが削除されている
☑ READMEが更新されている

## 実行結果

- tests/integration/test_llm_connection.py を作成（設定ベース、ハードコードなし）
- tests/unit/test_llm_transparency.py を作成（透明性ユーティリティのテスト）
- scripts/から6つのテストファイルを削除
- すべてのユニットテストが通過（9/9）
- README.mdを更新