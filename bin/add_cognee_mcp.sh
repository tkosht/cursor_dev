#!/usr/bin/sh

# claude mcp add cognee --transport sse http://localhost:8000/sse

repo_dir="$HOME/workspace/dev-tools/external-repos"
. $repo_dir/.env

claude mcp add cognee \
  -- uv --directory $repo_dir/cognee/cognee-mcp run cognee

#   -s project \
#   -e ENV=local \
#   -e TOKENIZERS_PARALLELISM=false \
#   -e LLM_API_KEY="$LLM_API_KEY" \
#   -e EMBEDDING_PROVIDER=$EMBEDDING_PROVIDER \
#   -e EMBEDDING_MODEL=$EMBEDDING_MODEL \
#   -e EMBEDDING_DIMENSIONS=$EMBEDDING_DIMENSIONS \
#   -e EMBEDDING_MAX_TOKENS=$EMBEDDING_MAX_TOKENS \

