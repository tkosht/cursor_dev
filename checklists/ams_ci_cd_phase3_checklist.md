# AMS CI/CD Phase 3 Checklist

## 📋 CI/CD要件確認
- [x] CI設定ファイル確認 (.github/workflows/ci.yml)
- [ ] 必要な環境変数の確認 (GOOGLE_API_KEY)
- [ ] 対応Pythonバージョン: 3.10, 3.11, 3.12

## 🔧 ローカルCI検証項目

### 1. リンター実行
- [ ] ruff check実行
  ```bash
  poetry run ruff check src/ tests/
  ```
- [ ] black format check実行
  ```bash
  poetry run black --check src/ tests/
  ```

### 2. 型チェック
- [ ] mypy実行
  ```bash
  poetry run mypy src/ --ignore-missing-imports --explicit-package-bases
  ```

### 3. テスト実行
- [ ] ユニットテスト実行（カバレッジ付き）
  ```bash
  poetry run pytest tests/unit/ \
    --cov=src \
    --cov-report=xml \
    --cov-report=term-missing \
    --cov-fail-under=85 \
    -v \
    --timeout=60
  ```

### 4. パフォーマンステスト（追加）
- [ ] パフォーマンステスト依存関係確認
- [ ] パフォーマンステスト実行確認

## 🔍 検証結果

### エラー・警告一覧
- [ ] ruff エラー: 
- [ ] black フォーマットエラー: 
- [ ] mypy 型エラー: 
- [ ] テスト失敗: 
- [ ] カバレッジ不足: 

## ✅ 修正アクション
- [ ] リンターエラー修正
- [ ] フォーマット修正
- [ ] 型エラー修正
- [ ] テスト修正
- [ ] カバレッジ改善

## 📊 最終確認
- [ ] 全リンターパス
- [ ] 型チェックパス
- [ ] 全テストパス
- [ ] カバレッジ85%以上達成
- [ ] CI/CDで実行される全項目がローカルでパス

## 🚀 完了後のアクション
- [ ] 最終コミット作成
- [ ] プッシュ実行
- [ ] GitHub ActionsでのCI実行確認
- [ ] プルリクエストの更新確認