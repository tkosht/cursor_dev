#!/usr/bin/bash

d=$(cd $(dirname $0) && pwd)
cd $d/../


cd dev-tools/external-repos/
if [ ! -d "cognee/" ]; then
    git clone https://github.com/topoteretes/cognee.git
fi


cd cognee/
ln -s ../.env .
git apply $d/mcp_server.patch
docker compose up -d


cd cognee-mcp/
git checkout .
git pull

uv sync --dev --all-extras --reinstall


