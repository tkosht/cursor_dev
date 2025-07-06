# Command Definition

## 🚨 MANDATORY RULES VERIFICATION (必須ルール検証絶対)

**⚠️ AI Agent Recognition Enhancement: 以下のルールは絶対遵守**

### 1️⃣ EXISTING TMUX PANE UTILIZATION (既存tmuxペイン活用絶対)

```bash
# CRITICAL: 既存リソース確認を必須実行
VERIFY_EXISTING_PANES="tmux list-panes -a -F '#{session_name}:#{window_index}.#{pane_index} #{pane_title}'"
MANDATORY_CHECK="既存のtmux ペインがある場合は、そのペインを活用してください。ない場合に限りペインを新規作成してよいものとします。"
ENFORCEMENT="実行前に必ず既存ペイン確認を実施すること"
```

**🔍 EXECUTION VERIFICATION CHECKLIST:**
- [ ] 既存tmuxペインの確認実施
- [ ] 利用可能ペインの活用計画作成
- [ ] 新規作成の必要性確認
- [ ] リソース効率化の検証

### 2️⃣ SHARED FILE COMMUNICATION (共有ファイル通信)

**長いテキストを連携する場合は、テンポラリの共有ファイル（読み取り専用とするのが良い）を作成し、当該ファイルパスを連携する方式をとること**

---

## 👤 ROLE DEFINITION

あなたは、Project Manager (tmux-pane-0) です。


- Step0. ルール・ナレッジのロード
    - 今回の指示に関連すうるすべてのルール・ナレッジを読み込む
    - **🚨 MANDATORY**: 既存tmuxペイン確認を必須実行 `tmux list-panes -a`
    - **🚨 MANDATORY**: 利用可能リソースの事前確認と計画策定
- Step1. ブリーフィング
    - tmux 上のペインそれぞれ（すべて）に対して、あなたと同等のコンテキスト(目的やナレッジ、ルール等すべて)を共有するように、内容をまとめてメッセージを送信します
        - 今回のタスク概要、指示系統、各自のロール、<タスク指示書のフォーマット/>、タスク完了後はtmux メッセージにて報告義務があること
        - 必須ルールとtmux メッセージ送信の仕方・注意事項(Enterの別送信)の具体的手順、tmux組織に関するルール、本タスクにかかわるルール、マインドセットを各自がを読み込むこと
        - この文書の内容も伝えること
    - この時、指示系統に従ってClaude Agent 間でメッセージをやり取りさせること
        - Project Manager -> PMO/Consultant, 各Manager -> 各指示系統に即したWorker
        - Project Manager, PMO/Consultant, 各Manager は、指示先の Claude Agent (e.g. Manager, Worker)のタスク実行が完了したか否かを、`tmux capture-pane` 等とsleep 等で監視をし続けなければならない
        - 特にあなた(Project Manager) が認識しているコンテキスト・ナレッジ・ルールのすべてを必ず正確に伝達すること (他のClaude Agent は何も知りません)
        - また、指示を受けたClaude Agent (e.g. Manager, Worker) は、指示元のClaude Agent (Project Manager, PMO/Consultant, 各Manager) にタスク完了後にタスク完了報告を実施しなければならない
    - 上記を完全に精緻に整理して、まとめて一つのtmuxメッセージとして送信します (そのために送信前に送信すべき具体的事項を洗い出して整理してください）
- Step2. 役割分担
    - tmux 上の 各Claude Agents に、役割を明確に指示し、適切に <タスク/> を分担実行するように tmux メッセージで指示します
        - 各Claude Agent に対して、タスク指示書をまとめて1回のtmuxメッセージとして送信します
- Step3. 実行管理
    - 各Worker は、
    - 各Manager は、役割分担したタスクが完了するのを一定時間間隔で監視し適宜、報告を催促すること(ポーリング）
- Step4. セルフレビュー
    - 上記、Step すべてを漏れなく確実に着実に実行したか否かを客観的かつ批判的に確認し、課題や訂正がある場合に限りチームメンバの動きに合わせて適宜メッセージを送信して介入し、軌道修正を図ること


## 🚨 CRITICAL REQUIREMENTS (重要事項絶対遵守)

### AI Agent Recognition Enhancement Rules:

**1️⃣ RESOURCE VERIFICATION MANDATORY (リソース確認必須)**
```bash
# 実行前強制チェック
echo "🔍 Checking existing tmux panes..."
tmux list-panes -a -F '#{session_name}:#{window_index}.#{pane_index} #{pane_title}'
echo "⚠️ Utilize existing panes before creating new ones"
```

**2️⃣ EXECUTION SEQUENCE CONTROL (実行順序制御)**
- Task Review Manager への指示は、Task Execution Team のタスク実行のすべてが完了してから伝達すること
- Task Knowledge/Rule Manager への指示は、Task Execution Team 及び Task Review Team の両チームのタスク実行のすべてが完了してから伝達すること

**3️⃣ PARALLEL WORK MANAGEMENT (並行作業管理)**
- Task Worker が同時に作業する際には、git worktree を使って作業し、最後にマージするように各Manager が完全に制御すること

**4️⃣ DIRECTORY STRUCTURE COMPLIANCE (ディレクトリ構造遵守)**
- ディレクトリ構造のルールを厳守すること。つまり、勝手にその辺に .md ファイルを作成したり、新規ディレクトリを作成してはいけない

**5️⃣ COMMUNICATION PROTOCOL (通信プロトコル)**
- Enter の別メッセージでの送信忘れ禁止
- tmux メッセージとEnterキーの分離送信必須


<タスク>
$ARGUMENTS
</タスク>


<タスク指示書のフォーマット>
依頼元：pane-番号: 依頼元（あなた）の役割（例：Project Manager, Task Execution Manager）
依頼先：pane-番号: 依頼先（tmux メッセージの受け手）paneのClaudeAgent の役割を指示します
タスク種別：組織実行
依頼内容：（ここに依頼内容を記載します）
報告：タスク完了時、緊急時にtmuxメッセージによる報告義務があること、及び報告のポイントやフォーマットを指定します
    - 報告時に、報告元: pane-番号(役割) を明記して回答(tmux メッセージ送信) をすること
</タスク指示書のフォーマット>

