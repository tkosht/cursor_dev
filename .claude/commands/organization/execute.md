# Command Difinition
- Step1. ブリーフィング
    - tmux 上のペインそれぞれ（すべて）に対して、以下を伝えること
        - 今回のタスク概要、指示系統、各自のロール、<タスク指示書のフォーマット/>、タスク完了後はtmux メッセージにて報告義務があることを伝える
        - 必須ルールとtmux メッセージ送信の仕方・注意事項の具体的手順、tmux組織に関するルール、本タスクにかかわるルール、マインドセットを各自がを読み込むように指示します
    - この時、指示系統に従ってClaude Agent 間でメッセージをやり取りさせること
        - Project Manager -> PMO/Consultant, 各Manager -> 各指示系統に即したWorker
        - Project Manager, PMO/Consultant, 各Manager は、指示先の Claude Agent (e.g. Manager, Worker)のタスク実行が完了したか否かを、`tmux capture-pane` とsleep 等で監視をし続けなければならない
        - また、指示を受けたClaude Agent (e.g. Manager, Worker) は、指示元のClaude Agent (Project Manager, PMO/Consultant, 各Manager) にタスク完了後にタスク完了報告を実施しなければならない
    - 上記を完全に精緻に整理して、まとめて一つのtmuxメッセージとして送信します (そのために送信前に送信すべき具体的事項を洗い出して整理してください）
- Step2. 役割分担
    - tmux 上の 各Claude Agents に、適切に <タスク/> を分担実行するように tmux メッセージで指示します
        - タスク指示書をまとめて一つのtmuxメッセージとして送信します
- Step3. 実行管理
    - 各Worker は、
    - 各Manager は、役割分担したタスクが完了するのを一定時間間隔で監視し適宜、報告を催促すること(ポーリング）


<タスク>
$ARGUMENTS
</タスク>

<タスク指示書のフォーマット>
依頼元：pane-番号: 依頼元（あなた）の役割（例：Project Manager, Task Execution Manager）
依頼先：pane-番号: 依頼先（tmux メッセージの受け手）paneのClaudeAgent の役割を指示します
タスク種別：組織実行
依頼内容：（ここに依頼内容を記載します）
報告：タスク完了時、緊急時にtmuxメッセージによる報告義務があること、及び報告のポイントやフォーマットを指定します

</タスク指示書のフォーマット>
