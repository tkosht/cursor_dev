# 進捗管理テンプレート

## 1. プロジェクト概要
```yaml
project:
  name: "企業情報クローラー"
  phase: "実装フェーズ"
  status: "進行中"
  last_updated: "YYYY-MM-DD HH:MM:SS"
```

## 2. 実装状況

### 2.1 機能実装
```yaml
features:
  crawler:
    base:
      status: "完了"
      coverage: 95%
      issues: 0
    company:
      status: "実装中"
      coverage: 80%
      issues: 2
    news:
      status: "未着手"
      coverage: 0%
      issues: 0

  database:
    models:
      status: "完了"
      coverage: 90%
      issues: 0
    migrations:
      status: "完了"
      coverage: 100%
      issues: 0

  error_handling:
    status: "実装中"
    coverage: 75%
    issues: 1
```

### 2.2 テスト実装
```yaml
tests:
  unit_tests:
    total: 50
    implemented: 45
    passing: 43
    coverage: 85%

  integration_tests:
    total: 10
    implemented: 8
    passing: 7
    coverage: 70%

  e2e_tests:
    total: 5
    implemented: 0
    passing: 0
    coverage: 0%
```

### 2.3 ドキュメント
```yaml
documentation:
  requirements:
    status: "完了"
    reviewed: true
    last_updated: "YYYY-MM-DD"

  basic_design:
    status: "完了"
    reviewed: true
    last_updated: "YYYY-MM-DD"

  detailed_design:
    status: "更新中"
    reviewed: false
    last_updated: "YYYY-MM-DD"

  api_docs:
    status: "未着手"
    reviewed: false
    last_updated: null
```

## 3. 課題管理

### 3.1 現在の課題
1. 重要度：高
   - 内容：CompanyCrawlerのURL設定がハードコードされている
   - 対応状況：対応中
   - 期限：YYYY-MM-DD
   - 担当者：開発者A

2. 重要度：中
   - 内容：テストカバレッジが目標に達していない
   - 対応状況：未着手
   - 期限：YYYY-MM-DD
   - 担当者：開発者B

### 3.2 解決済み課題
1. 完了日：YYYY-MM-DD
   - 内容：BaseCrawlerのエラーハンドリング実装
   - 対応者：開発者A
   - レビュアー：レビュアーB

## 4. 次のアクション

### 4.1 優先タスク
1. CompanyCrawlerの設定外部化
   - 担当：開発者A
   - 期限：YYYY-MM-DD
   - 見積：2日

2. テストカバレッジの向上
   - 担当：開発者B
   - 期限：YYYY-MM-DD
   - 見積：3日

### 4.2 将来タスク
1. ニュースクローラーの実装
   - 優先度：中
   - 見積：5日
   - 前提条件：CompanyCrawler完了

2. 監視機能の実装
   - 優先度：低
   - 見積：3日
   - 前提条件：なし

## 5. メトリクス

### 5.1 コード品質
```yaml
metrics:
  code_quality:
    lint_errors: 0
    lint_warnings: 2
    complexity: 15
    maintainability: "A"

  test_quality:
    coverage: 85%
    passing_rate: 95%
    flaky_tests: 1

  performance:
    response_time_avg: "2.5s"
    memory_usage: "150MB"
    cpu_usage: "25%"
```

### 5.2 進捗状況
```yaml
progress:
  planned_features: 20
  implemented_features: 15
  completion_rate: 75%
  
  planned_tests: 65
  implemented_tests: 53
  test_completion_rate: 81%
  
  estimated_completion: "YYYY-MM-DD"
  actual_progress: "予定通り"
``` 