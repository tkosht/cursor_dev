import os
from passlib.hash import bcrypt
from dotenv import load_dotenv

load_dotenv()

# 保存済みハッシュ（.env などから取得）
STORED = os.getenv("APP_ADMIN_HASH")

def verify(username, password):
    # username照合は割愛
    return bcrypt.verify(password, STORED)

print(verify("admin", "admin"))
