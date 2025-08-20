import os

import chainlit as cl

# from chainlit.data.sql_alchemy import SQLAlchemyDataLayer
from chainlit.types import ThreadDict
from dotenv import load_dotenv
from passlib.hash import bcrypt

load_dotenv()


@cl.password_auth_callback
def auth(username: str, password: str):
    if username != os.getenv("APP_ADMIN_USER"):
        return None
    if not bcrypt.verify(password, os.getenv("APP_ADMIN_HASH")):
        return None
    return cl.User(identifier=username, metadata={"email": username})


@cl.on_chat_start
async def start():
    cl.user_session.set("cfg", {"model": "gpt-4o", "temperature": 0.3})
    await cl.Message("ようこそ。履歴ペインは左側に出ます（認証＋永続化が前提）。").send()


@cl.on_message
async def on_message(msg: cl.Message):
    await cl.Message(f"""# 受信
- {msg.content}
""").send()


@cl.on_chat_resume
async def on_resume(thread: ThreadDict):
    # 履歴のメッセージは UI に自動復元済み。ここでは状態だけ再構築。
    cl.user_session.set("cfg", thread.get("metadata", {}) or {})
