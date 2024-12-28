default: all

all: up install

install: poetry-install

poetry-install:
	docker compose exec app bash bin/poetry_install.sh

# ==========
# interaction tasks
bash:
	docker compose exec app bash

poetry:
	docker compose exec app bash -i -c 'SHELL=/usr/bin/bash poetry shell'

demo:
	docker compose exec app bash -i -c 'SHELL=/usr/bin/bash poetry run bash bin/run_demo.sh'

python: up
	docker compose exec app python

# switch mode
cpu gpu:
	@rm -f compose.yml
	@ln -s docker/compose.$@.yml compose.yml

mode:
	@echo $$(ls -l compose.yml | awk -F. '{print $$(NF-1)}')


# ==========
# general tasks
pip: _pip commit

_pip:
	docker compose exec app python -m pip install -r requirements.txt         # too slow

commit:
	@echo "$$(date +'%Y/%m/%d %T') - Start $@"
	docker commit experiment.app experiment.app:latest
	@echo "$$(date +'%Y/%m/%d %T') - End $@"

save: commit
	@echo "$$(date +'%Y/%m/%d %T') - Start $@"
	docker save experiment.app:latest | gzip > data/experiment.app.tar.gz
	@echo "$$(date +'%Y/%m/%d %T') - End $@"

load:
	@echo "$$(date +'%Y/%m/%d %T') - Start $@"
	docker load < data/experiment.app.tar.gz
	@echo "$$(date +'%Y/%m/%d %T') - End $@"

# ==========
# docker compose aliases
up:
	docker compose up -d

active:
	docker compose up

ps images down:
	docker compose $@

im:images

build:
	docker compose build

build-no-cache:
	docker compose build --no-cache

reup: down up

clean: clean-logs clean-poetry clean-container

clean-poetry:
	rm -rf .venv poetry.lock

clean-logs:
	rm -rf log/*.log

clean-container:
	docker compose down --rmi all
	rm -rf app/__pycache__

.PHONY: help
help: ## ヘルプを表示
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: install
install: ## 依存パッケージをインストール
	poetry install

.PHONY: update
update: ## 依存パッケージを更新
	poetry update

.PHONY: lint
lint: ## コードをチェック
	poetry run flake8 app tests
	poetry run mypy app tests

.PHONY: format
format: ## コードをフォーマット
	poetry run black app tests
	poetry run isort app tests

.PHONY: test
test: ## ユニットテストを実行
	poetry run pytest tests --ignore=tests/integration

.PHONY: test-integration
test-integration: ## 統合テストを実行
	poetry run pytest tests/integration -v

.PHONY: test-all
test-all: test test-integration ## 全てのテストを実行

.PHONY: coverage
coverage: ## カバレッジレポートを生成
	poetry run pytest --cov=app tests --cov-report=html

.PHONY: clean
clean: ## 一時ファイルを削除
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .coverage
	rm -rf htmlcov
	find . -type d -name "__pycache__" -exec rm -rf {} +

.PHONY: run
run: ## アプリケーションを実行
	poetry run python -m app

