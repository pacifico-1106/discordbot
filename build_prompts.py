"""
システムプロンプト生成スクリプト
workspace内のmdファイルを結合してシステムプロンプトを生成
"""
import os
from pathlib import Path

# 結合するファイルの順序（指示書に基づく）
SALES_FILES_ORDER = [
    "IDENTITY.md",
    "SOUL.md",
    "USER.md",
    "MEMORY.md",
    "CONFIDENTIAL.md",
    "PRODUCTS.md",
    "TASTE.md",
    "TOOLS.md",
    "WORKFLOW_RULES.md"
]

ADMIN_FILES_ORDER = [
    "IDENTITY.md",
    "SOUL.md",
    "USER.md",
    "MEMORY.md",
    "TOOLS.md",
    "運用ルール_307-Admin.md",
    "セキュリティ防御マトリクス.md",
    "法改正監視ルール.md"
]


def read_md_file(filepath: Path) -> str:
    """mdファイルを読み込む"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        return content
    except FileNotFoundError:
        print(f"⚠️  ファイルが見つかりません: {filepath}")
        return None
    except Exception as e:
        print(f"❌ ファイル読み込みエラー ({filepath}): {e}")
        return None


def build_system_prompt(
    workspace_dir: Path,
    file_order: list,
    bot_name: str,
    bot_id: int,
    partner_bot_name: str,
    partner_bot_id: int
) -> str:
    """
    システムプロンプトを構築

    Args:
        workspace_dir: workspace/sales_md または workspace/admin_md のパス
        file_order: 結合するファイルの順序リスト
        bot_name: Botの名前（例：307-Sales）
        bot_id: BotのID
        partner_bot_name: 相手Botの名前
        partner_bot_id: 相手BotのID

    Returns:
        結合されたシステムプロンプト
    """
    prompt_parts = []

    # ヘッダー
    prompt_parts.append(f"# {bot_name} システムプロンプト")
    prompt_parts.append("")

    # 各ファイルを順に結合
    for filename in file_order:
        filepath = workspace_dir / filename
        content = read_md_file(filepath)

        if content:
            prompt_parts.append(f"\n{'='*80}")
            prompt_parts.append(f"## {filename.replace('.md', '')}")
            prompt_parts.append(f"{'='*80}\n")
            prompt_parts.append(content)
            print(f"✓ 結合: {filename}")
        else:
            print(f"⊘ スキップ: {filename}")

    # Bot間連携ルールを追加
    collaboration_rules = f"""

{'='*80}
## Discord Bot間連携ルール
{'='*80}

- あなたはDiscord上で動作するAI Botです
- 他のBotからメンションされた場合も通常通り応答してください
- 応答は具体的・実務的な内容のみ。「了解」「ありがとう」等の形式的返答は禁止
- 他のBotに作業を依頼する場合は <@{partner_bot_id}> でメンションしてください
- 同じ話題で3往復以上のラリーは禁止。3往復目では必ず「まとめ」を出して終了すること
- まとめは「📋 まとめ」で始めること

### 自分の情報
- Bot名: {bot_name}
- 自分のID: {bot_id}
- 相手Bot名: {partner_bot_name}
- 相手BotのメンションID: <@{partner_bot_id}>
"""
    prompt_parts.append(collaboration_rules)

    return "\n".join(prompt_parts)


def main():
    """メイン処理"""
    print("\n" + "="*80)
    print("システムプロンプト生成スクリプト")
    print("="*80 + "\n")

    # パス設定
    base_dir = Path(__file__).parent
    workspace_dir = base_dir / "workspace"
    prompts_dir = base_dir / "prompts"

    # Sales Bot プロンプト生成
    print("\n📝 Sales Bot プロンプトを生成中...")
    print("-" * 80)
    sales_workspace = workspace_dir / "sales_md"
    if sales_workspace.exists():
        sales_prompt = build_system_prompt(
            workspace_dir=sales_workspace,
            file_order=SALES_FILES_ORDER,
            bot_name="307-Sales",
            bot_id=1475846620967993424,
            partner_bot_name="307-Admin",
            partner_bot_id=1475848238425964666
        )

        output_path = prompts_dir / "sales_system.md"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(sales_prompt)
        print(f"\n✅ Sales Bot プロンプトを保存: {output_path}")
    else:
        print(f"❌ {sales_workspace} が存在しません")

    # Admin Bot プロンプト生成
    print("\n📝 Admin Bot プロンプトを生成中...")
    print("-" * 80)
    admin_workspace = workspace_dir / "admin_md"
    if admin_workspace.exists():
        admin_prompt = build_system_prompt(
            workspace_dir=admin_workspace,
            file_order=ADMIN_FILES_ORDER,
            bot_name="307-Admin",
            bot_id=1475848238425964666,
            partner_bot_name="307-Sales",
            partner_bot_id=1475846620967993424
        )

        output_path = prompts_dir / "admin_system.md"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(admin_prompt)
        print(f"\n✅ Admin Bot プロンプトを保存: {output_path}")
    else:
        print(f"❌ {admin_workspace} が存在しません")

    print("\n" + "="*80)
    print("✅ プロンプト生成完了")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
