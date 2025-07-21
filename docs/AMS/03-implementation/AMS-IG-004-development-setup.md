# AMS-IG-004: 開発環境セットアップガイド

## 1. 前提条件

### 1.1 システム要件
- **OS**: Linux/macOS/Windows (WSL2推奨)
- **Python**: 3.11以上
- **メモリ**: 8GB以上推奨（LLM処理のため）
- **ディスク**: 10GB以上の空き容量

### 1.2 必要なアカウント
- [ ] Google Cloud Platform (Gemini API)
- [ ] GitHub (ソースコード管理)
- [ ] Docker Hub (オプション：コンテナ利用時)

## 2. 初期セットアップ

### 2.1 プロジェクトクローン
```bash
# リポジトリのクローン
git clone https://github.com/your-org/article-market-simulator.git
cd article-market-simulator

# 開発ブランチの作成
git checkout -b feature/your-feature-name
```

### 2.2 Python環境構築
```bash
# Python 3.11のインストール確認
python --version  # Python 3.11.x

# 仮想環境の作成
python -m venv venv

# 仮想環境の有効化
# Linux/macOS:
source venv/bin/activate
# Windows:
.\venv\Scripts\activate

# pipのアップグレード
pip install --upgrade pip setuptools wheel
```

### 2.3 依存関係のインストール
```bash
# 基本パッケージ
pip install -r requirements.txt

# 開発用パッケージ
pip install -r requirements-dev.txt

# 確認
pip list
```

## 3. 必要なファイル構成

### 3.1 requirements.txt
```txt
# Core dependencies
langchain>=0.1.0
langchain-google-genai>=0.0.11
langgraph>=0.0.50
asyncio>=3.11.0
aiohttp>=3.9.0

# Web framework
fastapi>=0.109.0
uvicorn>=0.27.0
websockets>=12.0

# Data processing
pydantic>=2.5.0
numpy>=1.26.0
pandas>=2.1.0

# Utilities
python-dotenv>=1.0.0
rich>=13.7.0  # Better CLI output
typer>=0.9.0  # CLI framework
httpx>=0.26.0  # Async HTTP

# Logging and monitoring
structlog>=24.1.0
prometheus-client>=0.19.0
```

### 3.2 requirements-dev.txt
```txt
# Testing
pytest>=7.4.0
pytest-asyncio>=0.23.0
pytest-cov>=4.1.0
pytest-timeout>=2.2.0
pytest-benchmark>=4.0.0

# Code quality
black>=23.12.0
isort>=5.13.0
flake8>=7.0.0
mypy>=1.8.0
pylint>=3.0.0

# Documentation
mkdocs>=1.5.0
mkdocs-material>=9.5.0
mkdocstrings[python]>=0.24.0

# Development tools
ipython>=8.19.0
jupyter>=1.0.0
pre-commit>=3.6.0
```

### 3.3 .env.example
```bash
# LLM Configuration
LLM_PROVIDER=gemini
GEMINI_API_KEY=your-api-key-here
GEMINI_MODEL=gemini-2.5-flash

# Optional: Alternative LLM providers
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key

# Application Configuration
LOG_LEVEL=INFO
ENVIRONMENT=development
DEBUG=true

# Performance Settings
MAX_CONCURRENT_PERSONAS=10
SIMULATION_TIMEOUT=300
CACHE_ENABLED=true

# Database (Future)
DATABASE_URL=sqlite:///ams_dev.db
REDIS_URL=redis://localhost:6379

# Monitoring
ENABLE_METRICS=true
METRICS_PORT=8000
```

### 3.4 プロジェクト構造作成スクリプト
```bash
#!/bin/bash
# scripts/setup_project_structure.sh

# Create directory structure
mkdir -p src/{core,plugins,personas,visualization,utils}
mkdir -p tests/{unit,integration,e2e,fixtures,performance}
mkdir -p docs/{api,guides,architecture}
mkdir -p scripts
mkdir -p data/{cache,logs,results}

# Create __init__.py files
find src tests -type d -exec touch {}/__init__.py \;

# Create basic configuration files
touch src/config.py
touch src/constants.py
touch tests/conftest.py

# Create .gitignore
cat > .gitignore << EOF
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
.env

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/
.mypy_cache/

# IDE
.idea/
.vscode/
*.swp
*.swo

# Project specific
data/cache/
data/logs/
data/results/
*.log
*.db

# OS
.DS_Store
Thumbs.db
EOF

echo "Project structure created successfully!"
```

## 4. 開発ツール設定

### 4.1 VS Code設定
```json
// .vscode/settings.json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": [
    "tests"
  ],
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true
  }
}
```

### 4.2 Pre-commit設定
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-json
      - id: check-merge-conflict

  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
        args: ["--profile", "black"]

  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
        args: ["--max-line-length=88", "--extend-ignore=E203"]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

インストール:
```bash
pre-commit install
pre-commit run --all-files  # 初回チェック
```

### 4.3 Makefile（実装開始時に作成予定）
実装開始時に、プロジェクトのルートディレクトリに以下の内容でMakefileを作成する予定です：

```makefile
# Makefile (実装開始時に作成)
.PHONY: help install test lint format clean run

help:
	@echo "Available commands:"
	@echo "  install    - Install all dependencies"
	@echo "  test       - Run all tests"
	@echo "  lint       - Run linting checks"
	@echo "  format     - Format code"
	@echo "  clean      - Clean cache files"
	@echo "  run        - Run development server"

install:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	pre-commit install

test:
	pytest tests/unit -v --cov=src --cov-report=html

test-integration:
	pytest tests/integration -v

test-all:
	pytest tests -v --cov=src --cov-report=html

lint:
	flake8 src tests
	mypy src tests
	pylint src

format:
	black src tests
	isort src tests

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .coverage htmlcov .mypy_cache

run:
	uvicorn src.main:app --reload --port 8000

docker-build:
	docker build -t ams:latest .

docker-run:
	docker run -p 8000:8000 --env-file .env ams:latest
```

**注意**: このMakefileは実装開始時に作成してください。

## 5. API キー設定

### 5.1 Gemini API キー取得
1. [Google AI Studio](https://makersuite.google.com/app/apikey)にアクセス
2. 「Get API Key」をクリック
3. プロジェクトを選択または作成
4. APIキーをコピー

### 5.2 環境変数設定
```bash
# .envファイルの作成
cp .env.example .env

# エディタで.envを開いてAPIキーを設定
# GEMINI_API_KEY=your-actual-api-key-here
```

### 5.3 APIキー検証スクリプト
```python
# scripts/verify_setup.py
import os
import sys
from dotenv import load_dotenv
import google.generativeai as genai

def verify_setup():
    """開発環境のセットアップを検証"""
    
    # 環境変数の読み込み
    load_dotenv()
    
    # Python バージョンチェック
    if sys.version_info < (3, 11):
        print("❌ Python 3.11以上が必要です")
        return False
    print("✅ Python version:", sys.version)
    
    # APIキーチェック
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your-api-key-here":
        print("❌ GEMINI_API_KEYが設定されていません")
        return False
    print("✅ GEMINI_API_KEY is set")
    
    # API接続テスト
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content("Hello, this is a test")
        print("✅ Gemini API connection successful")
    except Exception as e:
        print(f"❌ Gemini API connection failed: {e}")
        return False
    
    # パッケージチェック
    required_packages = ["langchain", "langgraph", "fastapi", "pytest"]
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} is installed")
        except ImportError:
            print(f"❌ {package} is not installed")
            return False
    
    print("\n🎉 All checks passed! Environment is ready.")
    return True

if __name__ == "__main__":
    verify_setup()
```

実行:
```bash
python scripts/verify_setup.py
```

## 6. 開発ワークフロー

### 6.1 日次開発フロー
```bash
# 1. 最新の変更を取得
git pull origin main

# 2. 仮想環境を有効化
source venv/bin/activate

# 3. 依存関係の更新確認
pip install -r requirements.txt

# 4. 開発作業
# ...

# 5. テスト実行
pytest tests/unit -v

# 6. コード整形
black src tests

# 7. コミット
git add .
git commit -m "feat: implement persona generation logic"

# 8. プッシュ
git push origin feature/your-feature-name
```

### 6.2 トラブルシューティング

#### Python環境の問題
```bash
# 仮想環境の再作成
deactivate
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### APIキーの問題
```bash
# 環境変数の確認
python -c "import os; print(os.getenv('GEMINI_API_KEY')[:10] + '...')"

# .envファイルの再読み込み
python -c "from dotenv import load_dotenv; load_dotenv(override=True)"
```

#### パッケージの競合
```bash
# 依存関係の確認
pip check

# キャッシュクリア
pip cache purge

# 再インストール
pip install --force-reinstall -r requirements.txt
```

## 7. 次のステップ

1. **環境構築完了後**
   - `scripts/verify_setup.py`を実行して確認
   - サンプルコードの実行テスト

2. **開発開始**
   - AMS-IG-001のチェックリストに従って実装開始
   - テスト駆動開発の実践

3. **継続的な改善**
   - 開発中に発見した環境問題の記録
   - セットアップガイドの更新

---

更新日: 2025-07-21
作成者: AMS Implementation Team