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
    - **メタプロンプト**: 「タスクに関連する必須ルール、ナレッジ、制約事項を検索し、理解してから作業を開始すること。特にmandatory、required、必須、絶対などのキーワードを含むルールは例外なく遵守」
    - **🚨 MANDATORY**: 既存tmuxペイン確認を必須実行 `tmux list-panes -a`
    - **🚨 MANDATORY**: 利用可能リソースの事前確認と計画策定
- Step1. ブリーフィング
    - tmux 上のペインそれぞれ（すべて）に対して、あなたと同等のコンテキスト(目的やナレッジ、ルール等すべて)を共有するように、内容をまとめてメッセージを送信します
        - 今回のタスク概要、指示系統、各自のロール、<タスク指示書のフォーマット/>、タスク完了後はtmux メッセージにて報告義務があること
        - **メタ指示**: 「必須ルール、tmuxメッセージプロトコル（Enter別送信含む）、組織運営パターン、タスク関連ルール、マインドセットについて、関連ドキュメントを自律的に検索・学習して実行すること」
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

**🚨 DIRECTORY STRUCTURE PRINCIPLES (基本原則)**
- 既存のディレクトリ構造を必ず確認してから作業
- 新規ディレクトリの無断作成は禁止
- ファイルは既存の適切なディレクトリに配置
- 構造変更にはユーザー承認が必須

**📋 FILE CREATION PROTOCOL (ファイル作成プロトコル)**
```bash
# Step 1: 既存構造の確認
ls -la docs/
ls -la memory-bank/

# Step 2: 類似ファイルの配置場所を参考に
find . -name "*.md" -type f | grep -E "(article|guide|note)"

# Step 3: 適切な既存ディレクトリに配置
# 例: 記事なら既存の記事が置かれている場所
```

**🔍 VIOLATION PREVENTION (違反防止策)**
- [ ] `ls`コマンドで既存ディレクトリ構造を確認
- [ ] 類似ファイルの配置場所を`find`で調査
- [ ] 新規ディレクトリは作成せず既存ディレクトリを使用
- [ ] ルートディレクトリへの直接配置は禁止
- [ ] 不明な場合はユーザーに配置場所を確認

**⚠️ META-PROMPT (メタプロンプト)**
AI Agentへの指示：
「プロジェクトのディレクトリ構造ルールと承認要件を必ず確認してから作業を開始すること。ルールは通常、references、core、mandatoryなどのキーワードを含むドキュメントに記載されている」

**5️⃣ COMMUNICATION PROTOCOL (通信プロトコル)**
- Enter の別メッセージでの送信忘れ禁止
- tmux メッセージとEnterキーの分離送信必須

**🚨 ENTER送信忘れ防止策 (MANDATORY)**

**📋 必須実行パターン - 全てのtmuxメッセージで例外なく実行**
```
1. tmux send-keys -t [pane] "[message]"
2. tmux send-keys -t [pane] Enter  ← 必須！別コマンドで実行
3. sleep 3 (送信確認待機)
```

**⚠️ 絶対禁止パターン**
```bash
❌ FORBIDDEN: 
tmux send-keys -t 0:0.1 "message" Enter  # 同時送信は禁止

✅ MANDATORY:
tmux send-keys -t 0:0.1 "message"
tmux send-keys -t 0:0.1 Enter            # 別コマンドで送信
```

**🔍 ENTER送信忘れ検出方法**
AI Agentは以下をチェック：
- Bashツール使用時、tmux send-keysが2回実行されているか？
- 1回目：メッセージ送信
- 2回目：Enter送信（必須）
- 2回目が欠けている場合は送信失敗とみなす


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

