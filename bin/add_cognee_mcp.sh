#!/usr/bin/sh

# claude mcp add cognee --transport sse http://localhost:8000/sse

# repo_dir="$HOME/workspace/dev-tools/external-repos"
# . $repo_dir/.env
# 
# claude mcp add cognee \
#   -- uv --directory $repo_dir/cognee/cognee-mcp run cognee

claude mcp add cognee -- sh bin/run_cognee.sh
