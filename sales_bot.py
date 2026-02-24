"""
307-Sales Bot
Discord上で動作するSales担当AIボット
"""
import discord
from discord import Intents
from collections import defaultdict
from typing import Dict, List
from shared.config import BOT_INFO, MAX_RALLY_COUNT, MAX_HISTORY_LENGTH
from shared.claude_client import ClaudeClient, load_system_prompt


class SalesBot:
    """Sales Bot クラス"""

    def __init__(self):
        # Bot情報
        self.bot_info = BOT_INFO["sales"]
        self.bot_name = self.bot_info["name"]
        self.bot_id = self.bot_info["bot_id"]
        self.partner_bot_id = self.bot_info["partner_bot_id"]
        self.partner_bot_name = self.bot_info["partner_bot_name"]
        self.partner_mention = self.bot_info["partner_mention"]

        # Discord クライアント
        intents = Intents.default()
        intents.message_content = True  # メッセージ内容を取得するために必須
        intents.members = True  # メンバー情報を取得
        self.client = discord.Client(intents=intents)

        # Claude クライアント
        self.claude_client = ClaudeClient()

        # システムプロンプト
        self.system_prompt = self._build_system_prompt()

        # 会話履歴管理（チャンネルごと）
        self.conversation_history: Dict[int, List[Dict]] = defaultdict(list)

        # Bot間ラリーカウンター
        self.rally_counter: Dict[int, Dict] = defaultdict(
            lambda: {"count": 0, "last_bot_id": None}
        )

        # イベントハンドラーを登録
        self._setup_events()

    def _build_system_prompt(self) -> str:
        """システムプロンプトを構築"""
        # Phase 1: 基本的なプロンプト（Phase 2でファイルから読み込む）
        base_prompt = load_system_prompt(self.bot_info["system_prompt_path"])

        # Bot間連携ルールを追加
        collaboration_rules = f"""

## Discord Bot間連携ルール
- あなたはDiscord上で動作するAI Botです
- 他のBotからメンションされた場合も通常通り応答してください
- 応答は具体的・実務的な内容のみ。「了解」「ありがとう」等の形式的返答は禁止
- 他のBotに作業を依頼する場合は {self.partner_mention} でメンションしてください
- 同じ話題で3往復以上のラリーは禁止。3往復目では必ず「まとめ」を出して終了すること
- まとめは「📋 まとめ」で始めること

## 自分の情報
- Bot名: {self.bot_name}
- 自分のID: {self.bot_id}
- 相手Bot名: {self.partner_bot_name}
- 相手BotのメンションID: {self.partner_mention}
"""
        return base_prompt + collaboration_rules

    def _setup_events(self):
        """Discord イベントハンドラーを設定"""

        @self.client.event
        async def on_ready():
            print(f'{self.bot_name} がログインしました: {self.client.user}')
            print(f'Bot ID: {self.client.user.id}')

        @self.client.event
        async def on_message(message):
            await self._handle_message(message)

    async def _handle_message(self, message: discord.Message):
        """メッセージ処理のメインロジック"""

        # 自分自身のメッセージは無視
        if message.author.id == self.client.user.id:
            return

        channel_id = message.channel.id

        # 人間からのメッセージの場合、ラリーカウンターをリセット
        if not message.author.bot:
            self.rally_counter[channel_id] = {"count": 0, "last_bot_id": None}

        # 自分宛のメンションがあるかチェック
        if not self.client.user.mentioned_in(message):
            return

        # Bot間ラリーの回数をチェック
        rally_info = self.rally_counter[channel_id]
        current_rally_count = rally_info["count"]

        # 相手Botからのメッセージの場合、ラリーカウントを増加
        if message.author.bot and message.author.id == self.partner_bot_id:
            if rally_info["last_bot_id"] == self.bot_id:
                # 前回自分が送信していた場合はカウント増加
                rally_info["count"] += 1
                current_rally_count = rally_info["count"]

        # 最大ラリー数に達した場合
        is_final_rally = current_rally_count >= MAX_RALLY_COUNT

        # 会話履歴を構築
        await self._add_to_history(channel_id, message)

        # Claudeに送信するメッセージを作成
        claude_messages = self._build_claude_messages(channel_id, is_final_rally)

        # Typing indicatorを表示
        async with message.channel.typing():
            # Claude APIから応答を取得
            response = await self.claude_client.get_response(
                system_prompt=self.system_prompt,
                messages=claude_messages
            )

        # 応答を送信
        await message.channel.send(response)

        # 自分が送信したことを記録
        self.rally_counter[channel_id]["last_bot_id"] = self.bot_id

        print(f"[{self.bot_name}] 応答送信 (Rally: {current_rally_count}/{MAX_RALLY_COUNT})")

    async def _add_to_history(self, channel_id: int, message: discord.Message):
        """会話履歴にメッセージを追加"""
        # メンションを除去したクリーンなコンテンツ
        content = message.content

        # ユーザー情報
        author_name = message.author.display_name
        is_bot = message.author.bot

        # 履歴に追加
        self.conversation_history[channel_id].append({
            "role": "user",
            "content": f"[{author_name}{'(Bot)' if is_bot else ''}]: {content}"
        })

        # 履歴が長すぎる場合は古いものを削除
        if len(self.conversation_history[channel_id]) > MAX_HISTORY_LENGTH:
            self.conversation_history[channel_id] = \
                self.conversation_history[channel_id][-MAX_HISTORY_LENGTH:]

    def _build_claude_messages(
        self,
        channel_id: int,
        is_final_rally: bool
    ) -> List[Dict[str, str]]:
        """Claude APIに送信するメッセージリストを構築"""
        messages = []

        # 会話履歴を追加
        for msg in self.conversation_history[channel_id]:
            messages.append(msg)

        # 最終ラリーの場合は追加指示
        if is_final_rally:
            if messages and messages[-1]["role"] == "user":
                messages[-1]["content"] += (
                    "\n\n[システム注意] これが最後のラリーです。"
                    "必ず「📋 まとめ」で始まるまとめを出力して会話を終了してください。"
                )

        return messages

    def run(self):
        """Botを起動"""
        token = self.bot_info["token"]
        print(f"{self.bot_name} を起動中...")
        self.client.run(token)


if __name__ == "__main__":
    bot = SalesBot()
    bot.run()
