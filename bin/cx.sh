#!/usr/bin/env bash
set -euo pipefail
cmd="$1"; shift || true

# "/ns:name" → "ns/name"
name="${cmd#/}"; name="${name/:/\/}"
tmpl="$HOME/.codex/commands/${name}.md"
[ -f "$tmpl" ] || tmpl=".codex/commands/${name}.md"
[ -f "$tmpl" ] || { echo "No such command: $cmd" >&2; exit 2; }
# echo "$tmpl"; exit 0

rendered="$(cat $tmpl)
<user-requirements>
$*
</user-requirements>
"
# rendered=$(echo $rendered | perl -pe 's/\s*//g')

# echo $rendered

# 承認は都度要求・WS内書込を推奨
# exec codex --ask-for-approval on-request --sandbox workspace-write "$rendered"
echo "$rendered" | codex --dangerously-bypass-approvals-and-sandbox exec

