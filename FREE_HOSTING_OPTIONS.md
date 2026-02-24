# 完全無料でDiscord Botを運用する方法

## 🎯 結論: Railwayは有料（月$5）です

**2024年以降、RailwayとRenderの無料枠は実質的に使えなくなりました。**

- **Railway**: 無料トライアル30日のみ → その後最低月$5
- **Render**: 無料枠あるが15分非アクティブでスリープ → Discord Botには不向き
- **Vercel**: サーバーレス → Discord Bot（常時稼働必要）には使えない

---

## ✅ 完全無料で運用できる2つの選択肢

### オプション1: Mac mini（現在の環境）⭐ **デモ用推奨**

**メリット:**
- 追加コスト0円
- 既存環境をそのまま利用
- 開発・デバッグが高速
- セットアップ最短（5分で起動可能）

**デメリット:**
- Mac miniの電源が切れるとBotも停止
- ネット接続が切れると停止

**セットアップ:**
```bash
cd ~/Desktop/discordbotpj
pip3 install -r requirements.txt
cp .env.example .env
nano .env  # APIキーとトークンを設定

# Bot起動
python3 sales_bot.py  # Mac mini #1
python3 admin_bot.py  # Mac mini #2
```

**自動起動（Mac再起動時も自動起動）:**
```bash
# launchdを使って自動起動設定
# ~/Library/LaunchAgents/com.tokyo307inc.salesbot.plist を作成
```

**推奨用途:**
- 2/27のAIセミナーデモ
- 開発・テスト環境
- 短期プロジェクト

---

### オプション2: Oracle Cloud Always Free Tier ⭐ **長期運用推奨**

**メリット:**
- **完全無料（永久）**
- クレジットカード登録必要だが課金なし
- 高性能（Arm CPU 4コア、24GB RAM）
- 常時稼働可能
- 2台のBotを同時に動かしても余裕

**デメリット:**
- 初回セットアップに30分程度かかる
- Linux（Ubuntu）の基礎知識が必要
- SSH接続でのサーバー管理

**セットアップ手順:**

#### 1. Oracle Cloudアカウント作成
1. https://www.oracle.com/cloud/free/ にアクセス
2. "Start for free" をクリック
3. メールアドレスとパスワードを設定
4. クレジットカード情報を入力（課金はされません）
5. アカウント作成完了

#### 2. VMインスタンス作成
1. Oracle Cloudコンソールにログイン
2. **Compute** → **Instances** → **Create Instance**
3. 以下の設定を選択：
   - **Name**: discord-bot-server
   - **Image**: Ubuntu 22.04
   - **Shape**: **VM.Standard.A1.Flex**（⚠️ 重要: これがAlways Free対象）
     - OCPUs: 2
     - Memory: 12GB
   - **Virtual cloud network**: デフォルトのまま
   - **SSH keys**: "Generate a key pair for me" を選択してダウンロード
4. **Create** をクリック

#### 3. SSH接続
```bash
# ダウンロードしたSSH鍵のパーミッションを変更
chmod 400 ~/Downloads/ssh-key-*.key

# SSH接続（Public IPはOracle Cloudコンソールで確認）
ssh -i ~/Downloads/ssh-key-*.key ubuntu@<YOUR_PUBLIC_IP>
```

#### 4. サーバーセットアップ
```bash
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
nano .env
# ↑ ここでANTHROPIC_API_KEY、DISCORD_SALES_TOKEN、DISCORD_ADMIN_TOKENを設定
```

#### 5. systemdサービス設定（自動起動）

**Sales Bot サービス:**
```bash
sudo nano /etc/systemd/system/salesbot.service
```

以下の内容を貼り付け：
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
RestartSec=10
Environment="PYTHONUNBUFFERED=1"

[Install]
WantedBy=multi-user.target
```

**Admin Bot サービス:**
```bash
sudo nano /etc/systemd/system/adminbot.service
```

以下の内容を貼り付け：
```ini
[Unit]
Description=307-Admin Discord Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/discordbot
ExecStart=/usr/bin/python3 /home/ubuntu/discordbot/admin_bot.py
Restart=always
RestartSec=10
Environment="PYTHONUNBUFFERED=1"

[Install]
WantedBy=multi-user.target
```

#### 6. サービスを有効化・起動
```bash
# systemdをリロード
sudo systemctl daemon-reload

# サービスを有効化（サーバー再起動時に自動起動）
sudo systemctl enable salesbot adminbot

# サービスを起動
sudo systemctl start salesbot adminbot

# 状態確認
sudo systemctl status salesbot
sudo systemctl status adminbot

# ログ確認
sudo journalctl -u salesbot -f
sudo journalctl -u adminbot -f
```

#### 7. 動作確認
- Discordの `#collaboration` チャンネルで Bot にメンションして動作確認

**推奨用途:**
- 長期安定運用
- 本番環境
- 複数のBotを動かす場合

---

## 🔧 トラブルシューティング

### Oracle Cloud: SSH接続できない
```bash
# セキュリティグループで22番ポートが開いているか確認
# Oracle Cloudコンソール → Networking → Virtual Cloud Networks → Security Lists
```

### Botが起動しない
```bash
# ログを確認
sudo journalctl -u salesbot -n 50
sudo journalctl -u adminbot -n 50

# 環境変数を確認
cat .env

# 手動でBot起動してエラーを確認
cd ~/discordbot
python3 sales_bot.py
```

### プロンプトが生成されない
```bash
# 手動でプロンプトを生成
python3 build_prompts.py

# workspace内にmdファイルがあるか確認
ls -la workspace/sales_md/
ls -la workspace/admin_md/
```

---

## 📊 比較表

| 項目 | Mac mini | Oracle Cloud |
|-----|---------|-------------|
| **コスト** | 0円 | 0円（永久） |
| **セットアップ時間** | 5分 | 30分 |
| **管理の手間** | 低 | 中 |
| **常時稼働** | △（電源ONが必要） | ◎（24/7稼働） |
| **性能** | Mac miniのスペック次第 | 4コア、24GB RAM |
| **インターネット依存** | あり | なし（クラウド上） |
| **推奨用途** | デモ、開発 | 本番、長期運用 |

---

## 🎯 推奨デプロイ戦略

### 2/27 AIセミナーデモ用
→ **Mac mini**（追加コストなし、即座に動作確認可能）

### デモ後の長期運用
→ **Oracle Cloud Always Free Tier**（完全無料、高性能、24/7稼働）

---

## 💡 よくある質問

**Q: Oracle Cloudは本当に無料ですか？**
A: はい。Always Free Tierは永久無料です。クレジットカード登録は必要ですが、Always Free対象リソース（VM.Standard.A1.Flex等）を使う限り課金されません。

**Q: Railwayは無料じゃないんですか？**
A: 2024年以降、Railwayは完全無料プランを廃止しました。30日間の無料トライアル後は最低月$5が必要です。

**Q: Mac miniで十分ですか？**
A: デモや短期利用なら十分です。ただし、Mac miniの電源が切れるとBotも停止するため、長期運用にはOracle Cloudを推奨します。

**Q: Dockerは必要ですか？**
A: 必須ではありません。Mac miniでもOracle Cloudでも、Pythonを直接実行する方が簡単です。Dockerは複数環境で統一したい場合に便利です。

---

**最終更新:** 2026-02-25
**次回レビュー:** デプロイ後の動作確認

---

## 📚 参考リンク

- [Oracle Cloud Always Free Tier](https://www.oracle.com/cloud/free/)
- [Railway Pricing (2025)](https://railway.com/pricing)
- [GitHub Repository](https://github.com/pacifico-1106/discordbot)
