# GitHub セットアップガイド

## 1. GitHubリポジトリの作成

### オプションA: GitHub Webから作成
1. https://github.com/new にアクセス
2. リポジトリ名: `discord-bot-system` （または任意の名前）
3. **Private** を選択（推奨：機密情報を含むため）
4. "Add a README file" のチェックを外す
5. "Create repository" をクリック

### オプションB: GitHub CLIから作成
```bash
# GitHub CLIをインストール（まだの場合）
brew install gh

# ログイン
gh auth login

# リポジトリを作成（プライベート）
gh repo create discord-bot-system --private --source=. --remote=origin
```

---

## 2. ローカルリポジトリの初期化とプッシュ

```bash
# プロジェクトディレクトリに移動
cd ~/Desktop/discordbotpj

# Gitリポジトリを初期化（まだの場合）
git init

# リモートリポジトリを追加（GitHubで作成したリポジトリのURL）
git remote add origin https://github.com/YOUR_USERNAME/discord-bot-system.git

# ブランチ名をmainに変更（必要な場合）
git branch -M main

# すべてのファイルを追加（.gitignoreで除外されたファイルは自動的に無視される）
git add .

# 初回コミット
git commit -m "Initial commit: Discord Bot System with Phase 1 & 2 complete

- Discord.py Bot implementation (Sales & Admin)
- Claude Sonnet 4.6 integration
- Automatic prompt generation from workspace md files
- Loop prevention (max 3 rallies)
- Conversation history management
- Environment variable support (.env)
- Docker support
- Comprehensive documentation"

# GitHubにプッシュ
git push -u origin main
```

---

## 3. セキュリティチェック

プッシュ前に以下を必ず確認：

```bash
# .envファイルがgitignoreされているか確認
cat .gitignore | grep .env

# 追跡されているファイルを確認（.envが含まれていないこと）
git ls-files | grep .env

# もし.envが追跡されている場合は削除
git rm --cached .env
git commit -m "Remove .env from tracking"
```

---

## 4. GitHub Secretsの設定（CI/CD用、オプション）

リポジトリの **Settings → Secrets and variables → Actions** で以下を設定：

### Secrets
- `ANTHROPIC_API_KEY`: あなたのAnthropic APIキー
- `DISCORD_SALES_TOKEN`: Sales BotのDiscordトークン
- `DISCORD_ADMIN_TOKEN`: Admin BotのDiscordトークン

### 設定方法
1. リポジトリのページで "Settings" タブをクリック
2. 左側メニューから "Secrets and variables" → "Actions" を選択
3. "New repository secret" をクリック
4. Name に `ANTHROPIC_API_KEY`、Secret に実際のAPIキーを入力
5. "Add secret" をクリック
6. 残りのsecretsも同様に追加

---

## 5. .envファイルの再作成（デプロイ先で実行）

GitHubからクローンした後、各環境で`.env`ファイルを作成：

```bash
# リポジトリをクローン
git clone https://github.com/YOUR_USERNAME/discord-bot-system.git
cd discord-bot-system

# .envファイルを作成
cp .env.example .env

# .envファイルを編集して実際の値を設定
nano .env
# または
code .env
```

`.env` ファイルに以下を設定：
```bash
ANTHROPIC_API_KEY=sk-ant-api_ここに実際のキー
DISCORD_SALES_TOKEN=ここに実際のトークン
DISCORD_ADMIN_TOKEN=ここに実際のトークン
```

---

## 6. 継続的な更新

### コードを変更した場合

```bash
# 変更内容を確認
git status
git diff

# 変更をステージング
git add .

# コミット（意味のあるメッセージを付ける）
git commit -m "Add: 新機能の説明"
# または
git commit -m "Fix: バグ修正の説明"
# または
git commit -m "Update: 変更内容の説明"

# GitHubにプッシュ
git push
```

### リモートから最新を取得

```bash
# 最新の変更を取得
git pull origin main
```

---

## 7. ブランチ戦略（オプション）

開発とデモ用に分けたい場合：

```bash
# 開発用ブランチを作成
git checkout -b development

# 変更をコミット
git add .
git commit -m "Development: 新機能のテスト"

# 開発ブランチをプッシュ
git push -u origin development

# mainブランチにマージ（準備ができたら）
git checkout main
git merge development
git push
```

---

## 8. .gitignoreの確認

以下のファイルが**含まれていない**ことを確認：

```bash
# 追跡されているファイル一覧を表示
git ls-files

# 以下が含まれていてはいけない：
# - .env
# - __pycache__/
# - *.pyc
# - .DS_Store
```

もし誤って追加されている場合：

```bash
# ファイルを追跡から削除（ファイル自体は残す）
git rm --cached <ファイル名>

# 例：
git rm --cached .env
git rm -r --cached __pycache__

# コミット
git commit -m "Remove sensitive files from tracking"
git push
```

---

## 9. README.mdの更新

リポジトリの顔となるREADME.mdを確認：

```bash
# README.mdを確認
cat README.md

# 必要に応じて編集
nano README.md

# 変更をコミット
git add README.md
git commit -m "Update README.md"
git push
```

---

## 10. トラブルシューティング

### プッシュできない場合

```bash
# リモートの変更を先に取得
git pull origin main --rebase

# 再度プッシュ
git push
```

### コミット履歴をやり直したい場合

```bash
# 直前のコミットをやり直す
git commit --amend -m "新しいコミットメッセージ"

# 強制プッシュ（注意：チームで使っている場合は避ける）
git push --force
```

### 誤ってトークンをコミットしてしまった場合

```bash
# 1. 直ちにDiscord/AnthropicでトークンをRegenerate（無効化）
# 2. 履歴から削除（git filter-branchまたはBFG Repo-Cleaner使用）
# 3. GitHubに連絡してキャッシュをクリア

# 簡易的な方法（小規模リポジトリの場合）
# リポジトリを削除して再作成し、クリーンな状態から開始
```

---

## チェックリスト

プッシュ前に以下を確認：

- [ ] `.env` ファイルがgitignoreされている
- [ ] Discord TokenやAPI Keyが**コードに直接書かれていない**
- [ ] `.env.example` に実際のトークンが**含まれていない**
- [ ] README.mdが最新の状態
- [ ] コミットメッセージが明確
- [ ] 不要なファイル（ログ、キャッシュ等）が含まれていない

---

**最終更新:** 2026-02-25
