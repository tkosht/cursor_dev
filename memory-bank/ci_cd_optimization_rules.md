# CI/CD最適化ルール

## 🎯 目標とメトリクス

### パフォーマンス目標

| 指標 | 目標値 | 現在値 | 備考 |
|------|--------|--------|------|
| ビルド時間 | < 2分 | 45秒 | ✅ 達成 |
| テスト実行時間 | < 1分 | 30秒 | ✅ 達成 |
| デプロイ時間 | < 3分 | - | 未実装 |
| フィードバック時間 | < 5分 | 2分 | ✅ 達成 |

## 📋 必須コンポーネント

### 1. GitHub Actions設定

**基本構成**:
```yaml
name: CI
on:
  push:
    branches: [main, develop, feature/*]
    paths:  # パスフィルタで無駄なビルドを防ぐ
      - 'app/**'
      - 'tests/**'
      - 'pyproject.toml'
      - '.github/workflows/**'
  pull_request:
    branches: [main]
```

### 2. キャッシュ戦略

**必須キャッシュ**:
```yaml
- name: Cache dependencies
  uses: actions/cache@v4
  with:
    path: |
      ~/.cache/pypoetry
      ~/.cache/pip
      ~/.local
    key: ${{ runner.os }}-poetry-${{ hashFiles('**/poetry.lock') }}
    restore-keys: |
      ${{ runner.os }}-poetry-
```

### 3. マトリックステスト

**推奨構成**:
```yaml
strategy:
  matrix:
    python-version: ['3.10', '3.11', '3.12']
    os: [ubuntu-latest]  # 必要に応じてmacOS, Windowsも追加
  fail-fast: false  # 1つ失敗しても他は継続
```

## 🚀 最適化テクニック

### 1. 並列実行

**テストの並列化**:
```yaml
- name: Run tests in parallel
  run: |
    poetry run pytest tests/ \
      -n auto \  # CPUコア数に応じて自動調整
      --dist loadscope \  # モジュール単位で分散
      --cov=app
```

### 2. 段階的実行

**早期失敗の実装**:
```yaml
steps:
  # 1. 最速のチェックを最初に
  - name: Syntax check
    run: python -m py_compile app/**/*.py
  
  # 2. 静的解析（中速）
  - name: Linting
    run: poetry run flake8 app/ --select=E9,F63,F7,F82
  
  # 3. フルテスト（最遅）
  - name: Full test suite
    run: poetry run pytest
```

### 3. 条件付き実行

**スキップ条件**:
```yaml
- name: Deploy
  if: |
    github.ref == 'refs/heads/main' &&
    github.event_name == 'push' &&
    !contains(github.event.head_commit.message, '[skip deploy]')
  run: ./deploy.sh
```

## 📊 品質ゲート

### 必須チェック項目

```yaml
- name: Quality Gates
  run: |
    # 1. テストカバレッジ
    poetry run pytest --cov=app --cov-fail-under=85
    
    # 2. コード品質
    poetry run flake8 app/ tests/
    poetry run black --check app/ tests/
    poetry run isort --check app/ tests/
    
    # 3. 型チェック
    poetry run mypy app/ --ignore-missing-imports
    
    # 4. セキュリティ
    poetry run bandit -r app/
    poetry run safety check
```

### 結果の可視化

```yaml
- name: Upload coverage reports
  uses: codecov/codecov-action@v4
  with:
    file: ./coverage.xml
    fail_ci_if_error: true
    verbose: true

- name: Comment PR
  uses: actions/github-script@v7
  with:
    script: |
      github.issues.createComment({
        issue_number: context.issue.number,
        owner: context.repo.owner,
        repo: context.repo.repo,
        body: '✅ All quality checks passed!'
      })
```

## 🔧 ローカル開発との同期

### Pre-commitフック

**.pre-commit-config.yaml**:
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3.11
  
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
  
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
```

### Make タスク

**Makefile**:
```makefile
.PHONY: test lint format quality

test:
	poetry run pytest tests/ -v --cov=app

lint:
	poetry run flake8 app/ tests/
	poetry run mypy app/ --ignore-missing-imports

format:
	poetry run black app/ tests/
	poetry run isort app/ tests/

quality: format lint test
	@echo "✅ All quality checks passed!"
```

## 🐳 Docker最適化

### マルチステージビルド

```dockerfile
# ビルドステージ
FROM python:3.11-slim as builder
WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev

# 実行ステージ
FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY app/ ./app/
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]
```

### レイヤーキャッシュ活用

```dockerfile
# 依存関係を先にコピー（変更が少ない）
COPY pyproject.toml poetry.lock ./
RUN poetry install

# アプリケーションコードは最後に（変更が多い）
COPY app/ ./app/
COPY tests/ ./tests/
```

## 📈 モニタリングとアラート

### ビルド時間の追跡

```yaml
- name: Record build time
  run: |
    echo "BUILD_TIME=$(($(date +%s) - $START_TIME))" >> $GITHUB_ENV
    
- name: Send metrics
  run: |
    curl -X POST https://metrics.example.com/ci \
      -d "build_time=$BUILD_TIME" \
      -d "status=${{ job.status }}"
```

### 失敗時の通知

```yaml
- name: Notify on failure
  if: failure()
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    text: 'CI failed on ${{ github.ref }}'
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

## 🔄 継続的な改善

### メトリクス収集

**追跡すべき指標**:
1. ビルド時間の推移
2. テスト実行時間
3. 失敗率
4. キャッシュヒット率
5. 並列度の効果

### 定期的な見直し

**月次レビュー項目**:
- [ ] 不要なステップの削除
- [ ] 新しいツールの評価
- [ ] キャッシュ戦略の最適化
- [ ] 並列度の調整
- [ ] 依存関係の更新

## 🚨 アンチパターン

### 避けるべき実装

1. **全ファイルでのビルドトリガー**
   ```yaml
   # ❌ 悪い例
   on: push
   
   # ✅ 良い例
   on:
     push:
       paths: ['app/**', 'tests/**']
   ```

2. **キャッシュなしの実行**
   ```yaml
   # ❌ 毎回フルインストール
   - run: pip install -r requirements.txt
   
   # ✅ キャッシュ活用
   - uses: actions/cache@v4
   ```

3. **直列実行**
   ```yaml
   # ❌ 順番に実行
   - run: test1 && test2 && test3
   
   # ✅ 並列実行
   - run: test1 &
   - run: test2 &
   - run: test3 &
   - run: wait
   ```

## 📝 チェックリスト

### 新規プロジェクトでの設定

- [ ] GitHub Actions ワークフロー作成
- [ ] パスフィルタ設定
- [ ] キャッシュ設定
- [ ] マトリックステスト設定
- [ ] 品質ゲート実装
- [ ] 通知設定
- [ ] ローカル開発環境との同期
- [ ] ドキュメント更新

---

*このドキュメントは、CI/CDパイプラインの最適化における実践的なルールをまとめています。プロジェクトの成長に応じて継続的に更新してください。*