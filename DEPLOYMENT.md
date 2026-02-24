# デプロイメントガイド

Discord Bot間自律会話システムのデプロイ方法を説明します。

## ⚠️ 重要: Vercelは使用できません

**Discord Botは常時稼働が必要なため、Vercelでのホスティングは不可能です。**

理由：
- Vercelはサーバーレス（リクエストごとに起動/停止）
- Discord BotはWebSocketで常時接続が必要
- 実行時間制限がある（Free: 10秒、Pro: 60秒）

---

## 推奨デプロイ環境

### オプション1: Mac mini（現在の環境）✅ **推奨**

**メリット:**
- 追加コストなし
- 既存の環境をそのまま利用
- 高速な開発・デバッグ
- ローカルファイルへの直接アクセス

**デメリット:**
- Mac miniの電源が切れるとBotも停止
- 手動でのプロセス管理が必要

**セットアップ:**
```bash
# 1. リポジトリをクローン
cd ~/Desktop
git clone https://github.com/yourusername/discord-bot-system.git
cd discord-bot-system

# 2. 依存パッケージをインストール
pip3 install -r requirements.txt

# 3. 環境変数を設定
cp .env.example .env
nano .env  # API KeyとTokenを設定

# 4. プロンプトを生成
python3 build_prompts.py

# 5. Botを起動
python3 sales_bot.py  # Mac mini #1
python3 admin_bot.py  # Mac mini #2
```

**自動起動設定（macOS）:**
```bash
# launchd を使って自動起動
# ~/Library/LaunchAgents/com.tokyo307inc.salesbot.plist を作成
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.tokyo307inc.salesbot</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/python3</string>
        <string>/Users/taiyo/Desktop/discord-bot-system/sales_bot.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>WorkingDirectory</key>
    <string>/Users/taiyo/Desktop/discord-bot-system</string>
    <key>StandardOutPath</key>
    <string>/tmp/salesbot.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/salesbot.error.log</string>
</dict>
</plist>
```

---

### オプション2: Railway ✅ **クラウド推奨**

**メリット:**
- 常時稼働
- 簡単なデプロイ（GitHub連携）
- 無料枠あり（月500時間）
- 環境変数の管理が簡単

**コスト:**
- Free tier: $5クレジット/月
- Hobby: $5/月〜

**セットアップ:**
1. [Railway](https://railway.app/) にサインアップ
2. GitHubリポジトリを連携
3. 2つのサービスを作成（Sales Bot / Admin Bot）
4. 環境変数を設定：
   - `ANTHROPIC_API_KEY`
   - `DISCORD_SALES_TOKEN` (Sales Botのみ)
   - `DISCORD_ADMIN_TOKEN` (Admin Botのみ)
5. Start Commandを設定：
   - Sales Bot: `python3 sales_bot.py`
   - Admin Bot: `python3 admin_bot.py`

---

### オプション3: Render ✅

**メリット:**
- 無料枠あり
- GitHub連携
- 自動デプロイ

**コスト:**
- Free tier: あり（制限あり）
- Starter: $7/月〜

**セットアップ:**
1. [Render](https://render.com/) にサインアップ
2. New Web Service → GitHubリポジトリを選択
3. 2つのサービスを作成
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `python sales_bot.py`
6. 環境変数を設定

---

### オプション4: AWS EC2 / Lightsail

**メリット:**
- 完全なコントロール
- スケーラブル
- 他のAWSサービスとの統合

**コスト:**
- Lightsail: $3.50/月〜
- EC2 t2.micro: $8/月〜

**セットアップ:**
```bash
# EC2インスタンスにSSH
ssh -i your-key.pem ubuntu@your-instance

# Pythonとgitをインストール
sudo apt update
sudo apt install python3 python3-pip git

# リポジトリをクローン
git clone https://github.com/yourusername/discord-bot-system.git
cd discord-bot-system

# 依存関係をインストール
pip3 install -r requirements.txt

# 環境変数を設定
cp .env.example .env
nano .env

# systemdでサービス化（自動起動）
sudo nano /etc/systemd/system/salesbot.service
```

**systemdサービスファイル例:**
```ini
[Unit]
Description=307-Sales Discord Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/discord-bot-system
ExecStart=/usr/bin/python3 /home/ubuntu/discord-bot-system/sales_bot.py
Restart=always
Environment="PYTHONUNBUFFERED=1"

[Install]
WantedBy=multi-user.target
```

```bash
# サービスを有効化
sudo systemctl enable salesbot
sudo systemctl start salesbot
sudo systemctl status salesbot
```

---

### オプション5: Docker + 任意のホスティング

**メリット:**
- 環境の再現性
- どのプラットフォームでも動作
- 簡単なスケーリング

**Dockerfileを作成:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# プロンプトを生成
RUN python3 build_prompts.py

# デフォルトはSales Bot（環境変数で切り替え可能）
CMD ["python3", "sales_bot.py"]
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  sales-bot:
    build: .
    command: python3 sales_bot.py
    env_file:
      - .env
    restart: unless-stopped

  admin-bot:
    build: .
    command: python3 admin_bot.py
    env_file:
      - .env
    restart: unless-stopped
```

**起動:**
```bash
docker-compose up -d
```

---

## GitHub管理

### 1. リポジトリの作成

```bash
cd ~/Desktop/discordbotpj

# Gitリポジトリを初期化
git init

# リモートリポジトリを追加
git remote add origin https://github.com/yourusername/discord-bot-system.git

# ファイルを追加（.envは除外される）
git add .

# コミット
git commit -m "Initial commit: Discord Bot System Phase 1 & 2"

# プッシュ
git push -u origin main
```

### 2. GitHub Secretsの設定

リポジトリの Settings → Secrets and variables → Actions で以下を設定：

- `ANTHROPIC_API_KEY`
- `DISCORD_SALES_TOKEN`
- `DISCORD_ADMIN_TOKEN`

### 3. .gitignoreの確認

以下のファイルがGitHubにプッシュされないことを確認：
- `.env`（機密情報）
- `__pycache__/`
- `*.pyc`

---

## 環境変数の管理

### Mac mini（ローカル）
`.env` ファイルを使用（既に実装済み）

### クラウドサービス
各サービスのダッシュボードで環境変数を設定：
- Railway: Settings → Variables
- Render: Environment → Environment Variables
- AWS: EC2のユーザーデータまたは`.env`ファイル

---

## モニタリング

### ログ管理

**ローカル（Mac mini）:**
```bash
# 標準出力をファイルに保存
python3 sales_bot.py > logs/sales.log 2>&1 &
python3 admin_bot.py > logs/admin.log 2>&1 &
```

**クラウド:**
- Railway: 自動でログを収集
- Render: ダッシュボードでログ確認
- AWS: CloudWatch Logsと連携

### ヘルスチェック

Discord Botの稼働状況を確認：
```python
# healthcheck.py（別途作成可能）
import discord
import os

# Botのステータスを確認するスクリプト
```

---

## コスト比較

| オプション | 初期費用 | 月額費用 | 管理の手間 | 推奨度 |
|-----------|---------|---------|-----------|--------|
| Mac mini | 0円 | 0円 | 中 | ★★★★★ |
| Railway | 0円 | 0円〜$5 | 低 | ★★★★☆ |
| Render | 0円 | 0円〜$7 | 低 | ★★★★☆ |
| AWS Lightsail | 0円 | $3.50〜 | 中 | ★★★☆☆ |
| AWS EC2 | 0円 | $8〜 | 高 | ★★☆☆☆ |

---

## 推奨デプロイ戦略

### 開発・テスト環境
- Mac miniでローカル実行（無料、高速デバッグ）

### 本番環境
- **短期（デモ用）**: Mac mini + launchd（自動起動）
- **長期（安定運用）**: Railway または Render（簡単、低コスト）

---

## トラブルシューティング

### Botが起動しない
1. `.env` ファイルが正しく設定されているか確認
2. 環境変数が読み込まれているか確認: `python3 -c "import os; print(os.getenv('ANTHROPIC_API_KEY'))"`
3. Discord Botのトークンが有効か確認

### プロンプトが生成されない
1. `workspace/sales_md/` と `workspace/admin_md/` にファイルがあるか確認
2. 手動で生成: `python3 build_prompts.py`

### クラウドでの環境変数エラー
1. サービスのダッシュボードで環境変数が設定されているか確認
2. 環境変数名が正確か確認（大文字小文字区別）

---

**最終更新:** 2026-02-25
**次回レビュー:** デプロイ後の動作確認
