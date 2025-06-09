#!/usr/bin/bash

d=$(cd $(dirname $0) && pwd)
cd $d/../


cd dev-tools/external-repos/cognee/cognee-mcp
uv sync --dev --all-extras --reinstall

. .venv/bin/activate

. ./.env
python src/server.py --transport sse

