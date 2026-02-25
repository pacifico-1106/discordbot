# Discord Bot間自律会話システム構築指示書

## 背景
Tokyo307inc（307）では、2台のMac mini（#1 Sales / #2 Admin）でOpenClawを運用中。
しかしOpenClawのDiscord Bot間通信にはバグ（Issue #11199）があり、Bot同士が自動でやり取りできない。
2/27のAIセミナーデモに向けて、**Bot同士が自律的に会話できる自作Discord Botシステム**を構築する。

## ゴール
Discord上で2つのAI Bot（Sales Bot / Admin Bot）が以下のように動作すること：
1. 人間が `@307-Sales 〇〇を調べて、終わったら@307-Adminにレビューを依頼して` と指示
2. Sales Botが調査を実行し、結果をチャンネルに投稿
3. Sales Botが `@307-Admin この内容をレビューして` とメンション
4. Admin Botがそれを検知し、自動でレビューを返信
5. 必要に応じてさらにラリー（最大3往復でまとめて終了）

## 技術スタック
- **Python 3** + **discord.py**
- **Anthropic Claude API**（モデル: `claude-sonnet-4-6-20250514`）
- 既存のDiscord Bot トークンを再利用
- 各Mac miniで1プロセスずつ稼働（Sales Bot → #1, Admin Bot → #2）

## Discord情報（既存）
- サーバー: 307 AI Team（ID: 1475845134242283613）
- Bot A（307-Sales）Token: [REGENERATED - SEE .env FILE]
  - Application ID: 1475846620967993424
- Bot B（307-Admin）Token: [REGENERATED - SEE .env FILE]
  - Application ID: 1475848238425964666
- チャンネル: 
  - #sales-work: 1475845642432811070
  - #admin-work: 1475845713106829398
  - #collaboration: 1475845750939320523

## ファイル構成
```
~/discord-bot-system/
├── sales_bot.py          # Sales Bot メインスクリプト
├── admin_bot.py          # Admin Bot メインスクリプト
├── shared/
│   ├── claude_client.py  # Claude API共通ラッパー
│   └── config.py         # 設定値（トークン、チャンネルID等）
├── prompts/
│   ├── sales_system.md   # Sales Botのシステムプロンプト（IDENTITY等を結合）
│   └── admin_system.md   # Admin Botのシステムプロンプト（IDENTITY等を結合）
├── workspace/
│   ├── sales_md/         # ← Mac mini #1から取得したmdファイル群
│   └── admin_md/         # ← Mac mini #2から取得したmdファイル群
├── requirements.txt
└── README.md
```

## システムプロンプト構成
各Botのシステムプロンプトは以下のmdファイルを結合して生成する：

### Sales Bot（prompts/sales_system.md）
以下の順序で `workspace/sales_md/` 内のファイルを結合：
1. IDENTITY.md（人格・役割定義）
2. SOUL.md（行動原則）
3. USER.md（ユーザー情報）
4. MEMORY.md（過去の記憶）
5. CONFIDENTIAL.md（機密情報）
6. PRODUCTS.md（製品情報）
7. TASTE.md（好み・スタイル）
8. TOOLS.md（利用可能ツール ※参考用。実ツール連携は後述）
9. WORKFLOW_RULES.md（ワークフロールール）

### Admin Bot（prompts/admin_system.md）
以下の順序で `workspace/admin_md/` 内のファイルを結合：
1. IDENTITY.md
2. SOUL.md
3. USER.md
4. MEMORY.md
5. TOOLS.md
6. 運用ルール_307-Admin.md
7. セキュリティ防御マトリクス.md
8. 法改正監視ルール.md

## コア実装要件

### 1. メッセージ監視ロジック（discord.py）
```python
@client.event
async def on_message(message):
    # 自分自身のメッセージは無視
    if message.author.id == client.user.id:
        return
    
    # 自分宛のメンションを検知（人間からもBotからも受け取る）
    if client.user.mentioned_in(message):
        # Claude APIにメッセージを送信して返信
        response = await get_claude_response(message)
        await message.channel.send(response)
```

### 2. 会話履歴管理
- チャンネルごとに直近のメッセージ履歴を保持（最大20件）
- Bot同士のラリーもClaude APIに渡すことでコンテキストを維持
- 会話履歴はメモリ内で管理（永続化不要）

### 3. ループ防止（重要）
```python
# チャンネルごとのBot間ラリーカウンター
rally_counter = {}  # {channel_id: {"count": 0, "last_bot": None}}

# ルール：
# - Bot間ラリーは最大3往復
# - 3往復目で「まとめ」を生成して終了
# - 「了解」「ありがとう」等の形式的返答はしない（プロンプトで制御）
# - 人間の新規メッセージでカウンターリセット
```

### 4. Bot間連携プロンプトルール（システムプロンプトに追記）
```
## Discord Bot間連携ルール
- あなたはDiscord上で動作するAI Botです
- 他のBotからメンションされた場合も通常通り応答してください
- 応答は具体的・実務的な内容のみ。「了解」「ありがとう」等の形式的返答は禁止
- 他のBotに作業を依頼する場合は <@{相手のBot ID}> でメンションしてください
- 同じ話題で3往復以上のラリーは禁止。3往復目では必ず「まとめ」を出して終了すること
- まとめは「📋 まとめ」で始めること

## 自分の情報
- Bot名: 307-Sales（または307-Admin）
- 自分のID: {自分のBot ID}
- 相手Bot名: 307-Admin（または307-Sales）
- 相手BotのメンションID: <@{相手のBot ID}>
```

### 5. Claude API呼び出し
```python
import anthropic

client = anthropic.Anthropic(api_key="YOUR_API_KEY")

async def get_claude_response(system_prompt, messages):
    response = client.messages.create(
        model="claude-sonnet-4-6-20250514",
        max_tokens=4096,
        system=system_prompt,
        messages=messages
    )
    return response.content[0].text
```

### 6. 環境変数
```
ANTHROPIC_API_KEY=sk-ant-xxxxx
DISCORD_SALES_TOKEN=MTQ3NTg0NjYyMDk2Nzk5MzQyNA.GjfjRG.tMYhO5QPy6QhV_rTPil0plQDg4r_s5uxoLQLN0
DISCORD_ADMIN_TOKEN=MTQ3NTg0ODIzODQyNTk2NDY2Ng.Gql2Ma.NYukFP9W3K9Pwdt3eGsdfkMhEyNP7YI_IQNBfo
SALES_BOT_ID=1475846620967993424
ADMIN_BOT_ID=1475848238425964666
COLLAB_CHANNEL_ID=1475845750939320523
```

## デモシナリオ（2/27セミナー用）
1. 人間:「@307-Sales 長崎県のコワーキングスペース業界を調査して。完了したら @307-Admin に法務・コンプライアンス観点でレビューを依頼して」
2. Sales Bot → 調査結果を投稿 → Admin Botにメンション
3. Admin Bot → 法務レビューを返信
4. （必要なら1-2往復のやり取り）
5. 最後のBotが「📋 まとめ」で締めくくり

## 実装の優先順位
1. **Phase 1: 最小動作版**（まずこれを完成させる）
   - discord.py + Claude API で2Bot起動
   - メンション検知 → Claude応答 → 返信
   - Bot間メンションでの自動応答
   - ループ防止カウンター
   
2. **Phase 2: プロンプト最適化**
   - workspace/のmdファイルからシステムプロンプト生成
   - Bot間連携ルール調整
   
3. **Phase 3: ツール連携（余裕があれば）**
   - Google Drive連携（gogコマンド実行）
   - Web検索（Brave API）

## 注意事項
- Anthropic API Keyは `~/.bashrc` か `.env` で管理
- discord.pyのIntentsで `message_content=True` を有効にすること
- 各Botは別プロセスで起動（Sales → Mac mini #1、Admin → Mac mini #2）
- デモ当日は両方を #collaboration チャンネルで動作させる
- Sonnet 4.6のモデル文字列: `claude-sonnet-4-6-20250514` ←要確認、最新のモデル名をAnthropic公式で確認のこと

## 実行コマンド
```bash
# Mac mini #1（Sales）
cd ~/discord-bot-system
python sales_bot.py

# Mac mini #2（Admin）
cd ~/discord-bot-system
python admin_bot.py
```

以上の仕様で実装してください。まずPhase 1の最小動作版から始めて、動作確認ができたらPhase 2に進んでください。
