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

### オプション2: Railway ⚠️ **有料（月$5〜）**

**メリット:**
- 常時稼働
- 簡単なデプロイ（GitHub連携）
- 環境変数の管理が簡単

**コスト:**
- **無料トライアル**: 初回30日間、$5クレジット（使い切るか30日経過で終了）
- **Free Plan**: 月$1クレジットのみ（実質利用不可）
- **Hobby Plan**: **月$5**（$5分の使用量込み、超過分は従量課金）
- **Pro Plan**: 月$20（$20分のクレジット込み）

⚠️ **注意**: 2024年以降、Railwayは完全無料プランを廃止しました。継続利用には最低月$5が必要です。

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

### オプション3: Render ⚠️ **制限あり無料枠**

**メリット:**
- 無料枠あり（制限あり）
- GitHub連携
- 自動デプロイ

**コスト:**
- **Free tier**: あり（但し制限あり - 750時間/月、15分間非アクティブでスリープ）
- **Starter**: $7/月〜

⚠️ **注意**: 無料枠は15分間非アクティブでスリープするため、Discord Botには不向きです。実質的には有料プラン推奨。

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

### オプション5: Oracle Cloud (Always Free Tier) ✅ **完全無料**

**メリット:**
- **永久無料枠**（Arm CPUベースのVM: 最大4コア、24GB RAM）
- 常時稼働可能
- クレジットカード登録必要だが課金なし
- 高性能（Discord Bot複数台でも余裕）

**コスト:**
- **完全無料**（Always Free Tierは永久無料）

**セットアップ:**
1. [Oracle Cloud](https://www.oracle.com/cloud/free/) にサインアップ
2. Compute → Instances → Create Instance
3. Shape: **VM.Standard.A1.Flex**（Arm、Always Free対象）を選択
4. OS: Ubuntu 22.04
5. SSH鍵を設定してインスタンス作成
6. SSH接続してセットアップ：

```bash
# SSH接続
ssh -i your-key.pem ubuntu@your-instance-ip

# システム更新
sudo apt update && sudo apt upgrade -y

# Python3とgitをインストール
sudo apt install python3 python3-pip git -y

# リポジトリをクローン
git clone https://github.com/pacifico-1106/discordbot.git
cd discordbot

# 依存関係をインストール
pip3 install -r requirements.txt

# 環境変数を設定
cp .env.example .env
nano .env  # APIキーとトークンを設定

# systemdでサービス化
sudo nano /etc/systemd/system/salesbot.service
sudo nano /etc/systemd/system/adminbot.service

# サービスを有効化
sudo systemctl enable salesbot adminbot
sudo systemctl start salesbot adminbot

# 状態確認
sudo systemctl status salesbot
sudo systemctl status adminbot
```

**systemdサービスファイル例** (`/etc/systemd/system/salesbot.service`):
```ini
[Unit]
Description=307-Sales Discord Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/discordbot
ExecStart=/usr/bin/python3 /home/ubuntu/discordbot/sales_bot.py
Restart=always
Environment="PYTHONUNBUFFERED=1"

[Install]
WantedBy=multi-user.target
```

---

### オプション6: Docker + 任意のホスティング

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

## コスト比較（2025年最新版）

| オプション | 初期費用 | 月額費用 | 管理の手間 | 完全無料 | 推奨度 |
|-----------|---------|---------|-----------|---------|--------|
| **Mac mini** | 0円 | **0円** | 中 | ✅ | ★★★★★ |
| **Oracle Cloud** | 0円 | **0円** | 中 | ✅ | ★★★★★ |
| Railway | 0円 | **$5〜** | 低 | ❌ | ★★★☆☆ |
| Render | 0円 | **$7〜** | 低 | ❌ | ★★☆☆☆ |
| AWS Lightsail | 0円 | **$3.50〜** | 中 | ❌ | ★★★☆☆ |
| AWS EC2 | 0円 | **$8〜** | 高 | ❌ | ★★☆☆☆ |

---

## 推奨デプロイ戦略（2025年最新版）

### 💰 完全無料で運用したい場合
1. **Mac mini**（デモ・短期用に最適）
2. **Oracle Cloud Always Free Tier**（長期運用に最適）

### 💳 有料でも簡単に運用したい場合
1. **Railway**（月$5、GitHub連携が簡単）
2. **AWS Lightsail**（月$3.50、安定）

### 🎯 2/27デモ用の推奨構成
- **Mac mini**（追加コストなし、即座に動作確認可能）

### 📈 長期安定運用の推奨構成
- **Oracle Cloud Always Free Tier**（完全無料、高性能、永久利用可能）

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
