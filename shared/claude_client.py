"""
Claude API Client
Anthropic APIとの通信を管理する共通クライアント
"""
import anthropic
from typing import List, Dict
from shared.config import ANTHROPIC_API_KEY, CLAUDE_MODEL, MAX_RESPONSE_LENGTH


class ClaudeClient:
    """Claude API クライアント"""

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        self.model = CLAUDE_MODEL

    async def get_response(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
        max_tokens: int = 1500
    ) -> str:
        """
        Claude APIからレスポンスを取得

        Args:
            system_prompt: システムプロンプト
            messages: 会話履歴 [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
            max_tokens: 最大トークン数（デフォルト1500でDiscord制限に収まる）

        Returns:
            Claudeからの返答テキスト（Discord制限2000文字に収まるよう調整）
        """
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=messages
            )
            text = response.content[0].text

            # Discord の文字数制限（2000文字）対策
            if len(text) > MAX_RESPONSE_LENGTH:
                text = text[:MAX_RESPONSE_LENGTH-50] + "\n\n...(続きは省略されました)"

            return text
        except Exception as e:
            error_msg = f"Claude API エラー: {str(e)}"
            print(error_msg)
            return f"申し訳ございません。処理中にエラーが発生しました。\n{error_msg}"


def load_system_prompt(prompt_path: str) -> str:
    """
    システムプロンプトをファイルから読み込む
    ファイルが存在しない場合は build_prompts.py を実行してから再度読み込む

    Args:
        prompt_path: プロンプトファイルのパス

    Returns:
        システムプロンプト文字列
    """
    import os
    import subprocess
    from pathlib import Path

    try:
        with open(prompt_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # ファイルが存在するがほぼ空の場合（Phase 1のデフォルト）、再生成を試みる
            if len(content.strip()) < 500:
                print(f"⚠️  {prompt_path} が小さすぎます。プロンプトを再生成します...")
                raise FileNotFoundError("再生成が必要")
            return content
    except FileNotFoundError:
        # build_prompts.py を実行してプロンプトを生成
        print(f"📝 {prompt_path} が見つかりません。自動生成を試みます...")

        script_dir = Path(__file__).parent.parent
        build_script = script_dir / "build_prompts.py"

        if build_script.exists():
            try:
                result = subprocess.run(
                    ["python3", str(build_script)],
                    cwd=str(script_dir),
                    capture_output=True,
                    text=True
                )
                print(result.stdout)
                if result.returncode != 0:
                    print(f"⚠️  プロンプト生成でエラー: {result.stderr}")
            except Exception as e:
                print(f"⚠️  build_prompts.py の実行エラー: {e}")

        # 再度読み込みを試みる
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            # それでも失敗したらデフォルトプロンプトを使用
            print(f"⚠️  プロンプト生成に失敗。デフォルトプロンプトを使用します。")
            return """あなたは Discord 上で動作する AI Bot です。
ユーザーや他の Bot からのメンションに対して、的確に応答してください。"""
