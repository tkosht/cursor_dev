# app.py
import gradio as gr
import json, os, uuid, time

STORE = "threads.json"

def load_store():
    if os.path.exists(STORE):
        with open(STORE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_store(store):
    with open(STORE, "w", encoding="utf-8") as f:
        json.dump(store, f, ensure_ascii=False, indent=2)

def list_threads(store):
    # 左ペイン表示用 [(title, id), ...]
    items = []
    for tid, t in sorted(store.items(), key=lambda kv: kv[1]["created_at"], reverse=True):
        title = t.get("title") or f"(無題) {tid[:8]}"
        items.append((title, tid))
    return items

def new_thread(store):
    tid = str(uuid.uuid4())
    store[tid] = {"title": "新規スレッド", "created_at": time.time(), "messages": []}
    save_store(store)
    return tid, list_threads(store), []

def delete_thread(store, tid):
    if tid in store:
        store.pop(tid)
        save_store(store)
    # 代替スレッド選択
    next_tid = next(iter(store.keys()), "")
    messages = store.get(next_tid, {}).get("messages", []) if next_tid else []
    return next_tid, list_threads(store), messages

def rename_thread(store, tid, new_title):
    if tid in store:
        store[tid]["title"] = new_title.strip() or store[tid]["title"]
        save_store(store)
    return list_threads(store)

def select_thread(store, tid):
    msgs = store.get(tid, {}).get("messages", [])
    return msgs

def user_submit(store, tid, user_text, history):
    # ダミー応答（ここにLLM呼び出しを入れ替え）
    assistant = f"🧠: 「{user_text}」を受信。これはダミー応答です。"
    new_pair = [user_text, assistant]

    # Chatbot履歴（pairs）を更新
    history = (history or []) + [new_pair]

    # スレッドに保存
    if tid not in store:
        tid, _, _ = new_thread(store)
    store[tid]["messages"] = history
    # タイトル自動生成（初回のみ）
    if store[tid].get("title", "").startswith("新規") and user_text:
        store[tid]["title"] = user_text[:20]
    save_store(store)
    return history

with gr.Blocks(title="Gradio Chat Threads") as demo:
    store_state = gr.State(load_store())        # 全スレッド辞書（セッション内）
    current_tid = gr.State("")                  # 現在のスレッドID

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### 📂 スレッド")
            thread_list = gr.Dropdown(choices=[], label="スレッド一覧", interactive=True)
            btn_new = gr.Button("＋ 新規")
            btn_del = gr.Button("🗑️ 削除")
            rename_box = gr.Textbox(label="名称変更", placeholder="新しいタイトル")
            btn_ren = gr.Button("✏️ 変更")

        with gr.Column(scale=3):
            gr.Markdown("### 💬 会話")
            chat = gr.Chatbot(label="Chat", height=520)  # messages=(user, assistant) リスト
            user_in = gr.Textbox(label="あなたの発話", placeholder="メッセージを入力してEnter", lines=2)
            btn_send = gr.Button("送信", variant="primary")

    # 起動時：スレ一覧を描画
    def _init(store):
        items = list_threads(store)
        default_tid = items[0][1] if items else ""
        messages = store.get(default_tid, {}).get("messages", []) if default_tid else []
        return gr.update(choices=items, value=default_tid), default_tid, messages

    demo.load(_init, inputs=[store_state], outputs=[thread_list, current_tid, chat])

    # 新規
    def _new(store):
        tid, items, msgs = new_thread(store)
        return items, tid, msgs
    btn_new.click(_new, inputs=[store_state], outputs=[thread_list, current_tid, chat])

    # 選択変更
    def _select(store, tid):
        return select_thread(store, tid), tid
    thread_list.change(_select, inputs=[store_state, thread_list], outputs=[chat, current_tid])

    # 削除
    def _del(store, tid):
        tid2, items, msgs = delete_thread(store, tid)
        return gr.update(choices=items, value=tid2), tid2, msgs
    btn_del.click(_del, inputs=[store_state, current_tid], outputs=[thread_list, current_tid, chat])

    # リネーム
    def _ren(store, tid, title):
        items = rename_thread(store, tid, title)
        return gr.update(choices=items), ""
    btn_ren.click(_ren, inputs=[store_state, current_tid, rename_box], outputs=[thread_list, rename_box])

    # 送信
    def _send(store, tid, text, history):
        if not text.strip():
            return gr.update(), ""
        history = user_submit(store, tid, text.strip(), history)
        return history, ""
    btn_send.click(_send, inputs=[store_state, current_tid, user_in, chat], outputs=[chat, user_in])
    user_in.submit(_send, inputs=[store_state, current_tid, user_in, chat], outputs=[chat, user_in])

if __name__ == "__main__":
    demo.launch()

