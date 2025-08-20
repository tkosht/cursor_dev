poetry run python - <<'PY'
from passlib.hash import bcrypt
from getpass import getpass
print(bcrypt.hash(getpass('Password: '), rounds=12))
PY


