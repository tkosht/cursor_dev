#!/usr/bin/bash

d=$(cd $(dirname $0) && pwd)
cd $d/../


cd dev-tools/external-repos/cognee/cognee-mcp
. .venv/bin/activate
. ../../.env
python src/server.py --host 0.0.0.0 --transport sse

