#!/bin/bash
# Cognee Migration Wrapper Script

# Get script directory and change to workspace root
d=$(cd $(dirname $0) && pwd)
cd $d/../

# Set environment variables for Cognee
export PYTHONPATH="$(pwd)/dev-tools/external-repos/cognee:$PYTHONPATH"

# Load Cognee environment variables
if [ -f "dev-tools/external-repos/cognee/.env" ]; then
    set -a
    source dev-tools/external-repos/cognee/.env
    set +a
fi

# Run the migration script in workspace's poetry environment
poetry run python scripts/cognee_migration.py "$@"