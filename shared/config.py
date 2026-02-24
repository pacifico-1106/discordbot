"""
Discord Bot System Configuration
環境変数から設定値を読み込む
"""
import os
from typing import Optional
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

# 環境変数から取得（.envファイルを使う場合はpython-dotenvを使用）
def get_env(key: str, default: Optional[str] = None) -> str:
    value = os.getenv(key, default)
    if value is None:
        raise ValueError(f"環境変数 {key} が設定されていません")
    return value

# Anthropic API
ANTHROPIC_API_KEY = get_env("ANTHROPIC_API_KEY")
CLAUDE_MODEL = "claude-sonnet-4-6"  # Claude Sonnet 4.6（最新モデル）

# Discord Bot トークン
DISCORD_SALES_TOKEN = get_env("DISCORD_SALES_TOKEN")
DISCORD_ADMIN_TOKEN = get_env("DISCORD_ADMIN_TOKEN")

# Bot IDs
SALES_BOT_ID = 1475846620967993424
ADMIN_BOT_ID = 1475848238425964666

# Channel IDs
SALES_WORK_CHANNEL_ID = 1475845642432811070
ADMIN_WORK_CHANNEL_ID = 1475845713106829398
COLLAB_CHANNEL_ID = 1475845750939320523

# Server ID
SERVER_ID = 1475845134242283613

# Bot間連携設定
MAX_RALLY_COUNT = 3  # Bot間の最大ラリー回数
MAX_HISTORY_LENGTH = 20  # 保持する会話履歴の最大件数

# Bot情報マッピング
BOT_INFO = {
    "sales": {
        "name": "307-Sales",
        "bot_id": SALES_BOT_ID,
        "token": DISCORD_SALES_TOKEN,
        "partner_bot_id": ADMIN_BOT_ID,
        "partner_bot_name": "307-Admin",
        "partner_mention": f"<@{ADMIN_BOT_ID}>",
        "system_prompt_path": "prompts/sales_system.md"
    },
    "admin": {
        "name": "307-Admin",
        "bot_id": ADMIN_BOT_ID,
        "token": DISCORD_ADMIN_TOKEN,
        "partner_bot_id": SALES_BOT_ID,
        "partner_bot_name": "307-Sales",
        "partner_mention": f"<@{SALES_BOT_ID}>",
        "system_prompt_path": "prompts/admin_system.md"
    }
}
