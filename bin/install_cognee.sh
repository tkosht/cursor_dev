#!/usr/bin/bash

d=$(cd $(dirname $0) && pwd)
cd $d/../


cd dev-tools/external-repos/
if [ ! -d "cognee/" ]; then
    git clone https://github.com/topoteretes/cognee.git
fi


cd cognee/cognee-mcp
git checkout .
git pull
git apply $d/mcp_server.patch

uv sync --dev --all-extras --reinstall

