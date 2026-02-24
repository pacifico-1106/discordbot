# Discord Bot間自律会話システム

307-Sales Bot と 307-Admin Bot が Discord 上で自律的に会話できるシステムです。

## 概要

- 2つのAI Bot（Sales / Admin）がDiscord上でメンション経由で会話
- Anthropic Claude API（**Sonnet 4.6** 最新モデル）を使用
- Bot同士が最大3往復まで自動でやり取り
- 人間からの指示でワークフローを開始
- workspace内のmdファイルから自動でシステムプロンプトを生成

## システム構成

```
discordbotpj/
├── sales_bot.py              # Sales Bot メインスクリプト
├── admin_bot.py              # Admin Bot メインスクリプト
├── build_prompts.py          # システムプロンプト生成スクリプト ✨NEW
├── shared/
│   ├── claude_client.py      # Claude API共通ラッパー
│   └── config.py             # 設定値（トークン、チャンネルID等）
├── prompts/
│   ├── sales_system.md       # Sales Bot システムプロンプト（自動生成）
│   └── admin_system.md       # Admin Bot システムプロンプト（自動生成）
├── workspace/
│   ├── sales_md/             # Sales Bot用のmdファイル群（9ファイル）
│   └── admin_md/             # Admin Bot用のmdファイル群（8ファイル）
├── requirements.txt
├── .env.example
└── README.md
```

## セットアップ手順

### 1. 依存パッケージのインストール

```bash
cd ~/Desktop/discordbotpj
pip3 install -r requirements.txt
```

### 2. 環境変数の設定

`.env.example` をコピーして `.env` を作成し、Anthropic API Keyを設定：

```bash
cp .env.example .env
```

`.env` ファイルを編集：

```bash
# Anthropic API Key（要設定）
ANTHROPIC_API_KEY=sk-ant-xxxxx

# Discord Bot Tokens（既に設定済み）
DISCORD_SALES_TOKEN=MTQ3NTg0NjYyMDk2Nzk5MzQyNA.GjfjRG.tMYhO5QPy6QhV_rTPil0plQDg4r_s5uxoLQLN0
DISCORD_ADMIN_TOKEN=MTQ3NTg0ODIzODQyNTk2NDY2Ng.Gql2Ma.NYukFP9W3K9Pwdt3eGsdfkMhEyNP7YI_IQNBfo
```

### 3. システムプロンプトの生成 ✨

workspace内のmdファイルからシステムプロンプトを生成：

```bash
python3 build_prompts.py
```

これにより以下のファイルが生成されます：
- `prompts/sales_system.md` (約1,415行、56KB)
- `prompts/admin_system.md` (約1,337行、52KB)

**注意**: Bot起動時に自動生成されるため、手動実行は任意です。

## 起動方法

### Mac mini #1（Sales Bot）で実行

```bash
cd ~/Desktop/discordbotpj
python3 sales_bot.py
```

### Mac mini #2（Admin Bot）で実行

```bash
cd ~/Desktop/discordbotpj
python3 admin_bot.py
```

## 使い方

### 基本的な使い方

1. Discord の `#collaboration` チャンネルで以下のように指示：

```
@307-Sales 長崎県のコワーキングスペース業界を調査して。
完了したら @307-Admin に法務・コンプライアンス観点でレビューを依頼して
```

2. Sales Bot が調査結果を投稿し、Admin Bot にメンション
3. Admin Bot が自動で応答
4. 必要に応じて最大3往復まで自動でやり取り
5. 3往復目で自動的に「📋 まとめ」で締めくくり

### 動作例

```
人間: @307-Sales 競合他社の動向を調査して、@307-Admin にリスク評価を依頼して

Sales Bot: [調査結果を投稿]
          @307-Admin この内容についてリスク評価をお願いします

Admin Bot: [リスク評価を返信]
          いくつか追加で確認したい点があります...

Sales Bot: [追加情報を返信]

Admin Bot: 📋 まとめ
          [最終的な評価とまとめ]
```

## 主要機能

### Phase 1（実装完了）✅

- Discord.py による Bot 起動
- メンション検知と自動応答
- Bot間の自律的な会話
- ループ防止機構（最大3往復）
- 会話履歴の管理（最大20件）
- Claude API 連携（Sonnet 4.6）

### Phase 2（実装完了）✅

- workspace内のmdファイルからシステムプロンプト自動生成
- build_prompts.py による結合スクリプト
- Bot間連携ルールの統合
- 詳細な人格設定（IDENTITY, SOUL, MEMORY等）
- Bot起動時の自動プロンプト生成

### Phase 3（今後実装）

- Google Drive連携
- Web検索機能（Brave API）
- より高度なツール連携

## 設定情報

### Discord情報

- **サーバー**: 307 AI Team（ID: 1475845134242283613）
- **Bot A（307-Sales）**
  - Bot ID: 1475846620967993424
  - メンション: `<@1475846620967993424>`
- **Bot B（307-Admin）**
  - Bot ID: 1475848238425964666
  - メンション: `<@1475848238425964666>`

### チャンネル情報

- `#sales-work`: 1475845642432811070
- `#admin-work`: 1475845713106829398
- `#collaboration`: 1475845750939320523

## トラブルシューティング

### Botが起動しない

1. 環境変数が正しく設定されているか確認
2. `pip3 list` で必要なパッケージがインストールされているか確認
3. Discord Bot のトークンが有効か確認

### Botが反応しない

1. Discord Developer Portal で以下の Intent が有効か確認：
   - MESSAGE CONTENT INTENT
   - SERVER MEMBERS INTENT
2. Bot がサーバーに招待されているか確認
3. Bot に必要な権限が付与されているか確認

### Claude API エラー

1. API Key が正しく設定されているか確認
2. Anthropic のクォータが残っているか確認
3. モデル名が正しいか確認（`claude-sonnet-4-6`）

### プロンプトが生成されない

1. workspace/sales_md/ と workspace/admin_md/ にmdファイルが配置されているか確認
2. `python3 build_prompts.py` を手動実行してエラーを確認
3. Bot起動時に自動生成されるため、エラーログを確認

## 開発メモ

### モデル情報

- 使用モデル: `claude-sonnet-4-6` （Claude Sonnet 4.6 最新版）
- 最大トークン: 4096
- システムプロンプト: 各Botごとに設定

### ループ防止ロジック

- Bot間のラリーカウンターをチャンネルごとに管理
- 人間からのメッセージでカウンターリセット
- 3往復目で強制的にまとめモードに移行

## ライセンス

Tokyo307inc 内部使用
