FROM python:3.11-slim

# 作業ディレクトリを設定
WORKDIR /app

# 依存パッケージファイルをコピー
COPY requirements.txt .

# 依存パッケージをインストール
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションファイルをコピー
COPY . .

# プロンプトを事前生成（workspace内にmdファイルがある場合）
RUN python3 build_prompts.py || echo "Prompts will be generated at runtime"

# 環境変数（デフォルト値、実行時に上書き可能）
ENV PYTHONUNBUFFERED=1

# デフォルトコマンド（docker runで上書き可能）
CMD ["python3", "sales_bot.py"]
