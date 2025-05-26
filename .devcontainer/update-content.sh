#!/bin/bash
set -e

# Install project dependencies using Poetry
poetry install --no-root

echo "update-content.sh finished." 