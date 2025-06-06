default: all

all: up install

install: install-poetry install-claudecode

install-poetry:
	docker compose exec app bash bin/install_poetry.sh

install-claudecode:
	docker compose exec app bash bin/install_claudecode.sh

# ==========
# interaction tasks
bash:
	docker compose exec app bash

poetry:
	docker compose exec app bash -i -c 'SHELL=/usr/bin/bash poetry shell'

python: up
	docker compose exec app python

# switch mode
cpu gpu:
	@rm -f compose.yml
	@ln -s docker/compose.$@.yml compose.yml

mode:
	@echo $$(ls -l compose.yml | awk -F. '{print $$(NF-1)}')


# ==========
# docker compose aliases
up:
	docker compose up -d
	docker compose exec app sudo service docker start

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

clean: clean-logs clean-poetry clean-npm clean-container

clean-poetry:
	rm -rf .venv poetry.lock

clean-npm:
	rm -rf .npm-global

clean-logs:
	rm -rf logs/*.log

clean-container:
	docker compose down --rmi all
	rm -rf app/__pycache__

clean-repository: clean-poetry clean-logs
	rm -rf app/* tests/* data/*

