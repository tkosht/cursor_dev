#!/usr/bin/sh

# stdin
claude mcp add sequential-thinking -s project -- npx -y @modelcontextprotocol/server-sequential-thinking

# sse
claude mcp add serena -s project --transport sse http://localhost:9121/sse

# custom script
claude mcp add cognee -s project -- sh bin/run_cognee.sh

