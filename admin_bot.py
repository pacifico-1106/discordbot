"""
307-Admin Bot
Discord上で動作するAdmin担当AIボット
"""
import discord
from discord import Intents
from collections import defaultdict
from typing import Dict, List
from shared.config import BOT_INFO, MAX_RALLY_COUNT, MAX_HISTORY_LENGTH
from shared.claude_client import ClaudeClient, load_system_prompt
from shared.file_processor import FileProcessor
import datetime


class AdminBot:
    """Admin Bot クラス"""

    def __init__(self):
        # Bot情報
        self.bot_info = BOT_INFO["admin"]
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

        # 古いメッセージ（5秒以上前）は無視
        import datetime
        now = datetime.datetime.now(datetime.timezone.utc)
        if (now - message.created_at).total_seconds() > 5:
            return

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

        # 応答を送信（2000文字制限対応：自動分割）
        await self._send_response(message.channel, response)

        # 自分が送信したことを記録
        self.rally_counter[channel_id]["last_bot_id"] = self.bot_id

        print(f"[{self.bot_name}] 応答送信 (Rally: {current_rally_count}/{MAX_RALLY_COUNT})")

    async def _send_response(self, channel, response: str):
        """
        応答を送信（Discord 2000文字制限対応：自動分割）
        """
        MAX_LENGTH = 1900  # 余裕を持たせる

        if len(response) <= MAX_LENGTH:
            # 2000文字以内ならそのまま送信
            await channel.send(response)
        else:
            # 2000文字超える場合は分割送信
            chunks = []
            current_chunk = ""

            # 段落単位で分割（\n\nで分ける）
            paragraphs = response.split('\n\n')

            for paragraph in paragraphs:
                # 段落を追加しても制限内なら追加
                if len(current_chunk) + len(paragraph) + 2 <= MAX_LENGTH:
                    if current_chunk:
                        current_chunk += '\n\n'
                    current_chunk += paragraph
                else:
                    # 制限を超える場合は現在のchunkを保存
                    if current_chunk:
                        chunks.append(current_chunk)
                    current_chunk = paragraph

            # 最後のchunkを追加
            if current_chunk:
                chunks.append(current_chunk)

            # 分割して送信
            for i, chunk in enumerate(chunks, 1):
                if i == 1:
                    await channel.send(chunk)
                else:
                    await channel.send(f"**(続き {i}/{len(chunks)})**\n\n{chunk}")

    async def _add_to_history(self, channel_id: int, message: discord.Message):
        """会話履歴にメッセージを追加（添付ファイル対応）"""
        # ユーザー情報
        author_name = message.author.display_name
        is_bot = message.author.bot

        # メッセージコンテンツを構築
        content_parts = []

        # テキスト部分
        if message.content:
            content_parts.append({
                "type": "text",
                "text": f"[{author_name}{'(Bot)' if is_bot else ''}]: {message.content}"
            })

        # 添付ファイルの処理
        if message.attachments:
            for attachment in message.attachments:
                print(f"📎 添付ファイル検出: {attachment.filename}")

                result = await FileProcessor.process_attachment(attachment)

                if result['error']:
                    # エラーの場合はテキストで追加
                    content_parts.append({
                        "type": "text",
                        "text": f"\n[添付ファイル: {result['filename']}] {result['error']}"
                    })
                elif result['type'] == 'image':
                    # 画像の場合
                    content_parts.append({
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": result['content']['media_type'],
                            "data": result['content']['data']
                        }
                    })
                    content_parts.append({
                        "type": "text",
                        "text": f"\n[添付画像: {result['filename']}]"
                    })
                elif result['type'] == 'text':
                    # ドキュメントの場合（抽出したテキスト）
                    content_parts.append({
                        "type": "text",
                        "text": f"\n\n--- 添付ファイル: {result['filename']} ---\n{result['content']}"
                    })

        # URLリンクの抽出と通知
        if message.content:
            urls = FileProcessor.extract_urls(message.content)
            if urls:
                url_text = "\n\n[検出されたURL]:\n" + "\n".join(f"- {url}" for url in urls)
                content_parts.append({
                    "type": "text",
                    "text": url_text
                })

                # Google Drive リンクの場合は注意喚起
                for url in urls:
                    if FileProcessor.is_google_drive_url(url):
                        content_parts.append({
                            "type": "text",
                            "text": "\n⚠️ Google Driveリンクが含まれています。共有設定を確認してください。"
                        })
                        break

        # コンテンツが1つの場合は文字列に、複数の場合はリストに
        if len(content_parts) == 1 and content_parts[0]["type"] == "text":
            message_content = content_parts[0]["text"]
        else:
            message_content = content_parts

        # 履歴に追加
        self.conversation_history[channel_id].append({
            "role": "user",
            "content": message_content
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
    bot = AdminBot()
    bot.run()
