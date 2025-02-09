FROM python:3.12-slim

# 必要なパッケージのインストール
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Poetry のインストール
RUN curl -sSL https://install.python-poetry.org | python3 -

# 作業ディレクトリの設定
WORKDIR /app

# 依存関係ファイルのコピー
COPY pyproject.toml poetry.lock* ./

# Poetry の設定（仮想環境を作成しない）
RUN poetry config virtualenvs.create false

# 依存関係のインストール
RUN poetry install --no-root --no-interaction

# ソースコードのコピー
COPY . .

# 開発サーバーのポート
EXPOSE 7860

# 開発用コマンド
CMD ["poetry", "run", "python", "-m", "app"] 