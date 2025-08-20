#!/usr/bin/sh

d=$(cd $(dirname $0) && pwd)
cd $d/../

prompt_debug='
<依頼>
@docs/01.requirements/ai_agent_execution_rules.md に完全に従い、以下を完全に遂行してください。
1. AMS(app/ams/)サブプロジェクトの開発状況を事実をもとに確認してください。
2. そもそも、テストケースが要件定義、基本設計に適切に従っているかをレビューし、適切に誠実に改善してください。
3. 次に、poetry run pytest -v . 等で、テスト状況を確認し適切に誠実にエラー解析し解決に導いてください。
4. エラー解決したタイミングで、デグレード確認を実施します。(必須)
5. <ゴール設定/> の完了条件を満たすまで、上記1.～4. を繰り返す
</依頼>

<ゴール設定>
1. すべてのテストが正しいこと、すべてのテストが適切に誠実に通ること、及び同じ実現方法がある場合はよりシンプルな構造になっていること、が完了条件です。
</ゴール設定>

<制約>
1. @docs/01.requirements/ai_agent_execution_rules.md を精緻に確認し完全に従い、以下を完全に遂行してください。
2. すべてをチェックリストドリブンで実行するために完全なチェックリストファイルを作成・更新しながら、進捗が明確になるようにしてください。
3. 完了条件が満たされるまで、繰り返し適切なエラー解析・改善・デグレード確認をしてください。
4. 同じ実現方法がある場合は、よりシンプルな構造になるようにレビューし改善してください。
</制約>
'

prompt_degradecheck='
<依頼>
`poetry run pytest -v .` を実行し、すべてが正常にパスするかをチェックする
</依頼>

<条件>
1. FAIL, ERROR, SKIP 等がなく、すべて PASSED になることのみを合格(OK)とみなす。一つでもFAIL, ERROR, SKIPがあれば不合格(NG)とする
</条件>

<output-format>
only output "OK" xor "NG" at the last line
</output-format>
'


export PATH=./node_modules/.bin/:$PATH
agent="codex --dangerously-bypass-approvals-and-sandbox exec"
# agent="claude --dangerously-skip-permissions"
# agent="cursor-agent"

while :
do
    # debugging
    echo "$prompt_debug" | $agent

    # degrade checking
    CHECKED=$(echo "$prompt_degradecheck" | $agent)
    echo "$CHECKED"
    STATUS=$(echo "CHECKED" | tail -n 1)
    echo "-----"
    echo "$STATUS"
    break
done

