"""
Microsoft Teams 安全なメッセージ送信テストスクリプト
テスト用チャネルのみに送信することを推奨
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Import the TeamsClient
sys.path.insert(0, os.path.dirname(__file__))
from app.integrations.microsoft.teams_client import TeamsClient

load_dotenv()

# 安全なキーワードリスト（テスト用チャネルと思われるもの）
SAFE_CHANNEL_KEYWORDS = [
    "test",
    "テスト",
    "sandbox",
    "サンドボックス",
    "dev",
    "開発",
    "試験",
    "demo",
    "デモ",
]


def is_safe_channel(channel_name: str) -> bool:
    """チャネル名が安全かどうかを判定"""
    channel_lower = channel_name.lower()
    return any(keyword in channel_lower for keyword in SAFE_CHANNEL_KEYWORDS)


def print_warning():
    """警告メッセージを表示"""
    print("\n" + "⚠️ " * 20)
    print("⚠️  WARNING: MESSAGE SENDING TEST")
    print("⚠️ " * 20)
    print("\n実際のTeamsチャネルにメッセージが送信されます。")
    print("以下のような安全なテスト用チャネルを選択してください：")
    print("  - 'test' や 'テスト' を含むチャネル名")
    print("  - 'sandbox' や 'dev' を含むチャネル名")
    print("  - 自分だけがいるプライベートチャネル")
    print("\n⚠️  重要なチャネル（全社、営業など）への送信は避けてください！")
    print("\n" + "=" * 60 + "\n")


async def main():
    print("\n" + "=" * 60)
    print("Microsoft Teams - Safe Message Sending Test")
    print("=" * 60)

    # 警告表示
    print_warning()

    # 環境変数から認証情報を読み込み
    tenant_id = os.getenv("MICROSOFT_TENANT_ID")
    client_id = os.getenv("MICROSOFT_CLIENT_ID")
    client_secret = os.getenv("MICROSOFT_CLIENT_SECRET")

    if not all([tenant_id, client_id, client_secret]):
        print("❌ Error: Missing environment variables")
        return

    # Teams Client初期化
    client = TeamsClient(
        tenant_id=tenant_id, client_id=client_id, client_secret=client_secret
    )

    # 認証
    print("1. Authenticating...")
    try:
        await client.authenticate()
        print("✅ Authentication successful\n")
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return

    # チーム取得
    print("2. Getting teams...")
    try:
        teams = await client.get_teams()
        if not teams:
            print("❌ No teams found")
            return
        print(f"✅ Found {len(teams)} teams\n")
    except Exception as e:
        print(f"❌ Failed to get teams: {e}")
        return

    # チーム選択
    print("Available teams (showing first 20):")
    for i, team in enumerate(teams[:20]):
        print(f"  {i + 1:2}. {team['displayName']}")

    while True:
        try:
            team_choice = input(
                f"\nSelect team number (1-{min(20, len(teams))}), or 'q' to quit: "
            )
            if team_choice.lower() == "q":
                print("❌ Test cancelled by user")
                return

            team_idx = int(team_choice) - 1
            if 0 <= team_idx < min(20, len(teams)):
                selected_team = teams[team_idx]
                break
            else:
                print(f"❌ Invalid number. Please enter 1-{min(20, len(teams))}")
        except ValueError:
            print("❌ Invalid input. Please enter a number or 'q'")

    print(f"\n3. Selected team: {selected_team['displayName']}")

    # チャネル取得
    print("\n4. Getting channels...")
    try:
        channels = await client.get_channels(selected_team["id"])
        if not channels:
            print("❌ No channels found")
            return
        print(f"✅ Found {len(channels)} channels\n")
    except Exception as e:
        print(f"❌ Failed to get channels: {e}")
        return

    # 安全なチャネルをフィルタリング
    safe_channels = [ch for ch in channels if is_safe_channel(ch["displayName"])]

    if safe_channels:
        print("📗 RECOMMENDED: Safe test channels detected:")
        for i, channel in enumerate(safe_channels):
            print(f"  ✅ {i + 1}. {channel['displayName']}")
        print()

    print("All available channels:")
    for i, channel in enumerate(channels):
        safety_marker = "✅" if is_safe_channel(channel["displayName"]) else "⚠️ "
        print(f"  {safety_marker} {i + 1:2}. {channel['displayName']}")

    # チャネル選択
    while True:
        try:
            channel_choice = input(
                f"\nSelect channel number (1-{len(channels)}), or 'q' to quit: "
            )
            if channel_choice.lower() == "q":
                print("❌ Test cancelled by user")
                return

            channel_idx = int(channel_choice) - 1
            if 0 <= channel_idx < len(channels):
                selected_channel = channels[channel_idx]
                break
            else:
                print(f"❌ Invalid number. Please enter 1-{len(channels)}")
        except ValueError:
            print("❌ Invalid input. Please enter a number or 'q'")

    print(f"\n5. Selected channel: {selected_channel['displayName']}")

    # 安全性確認
    if not is_safe_channel(selected_channel["displayName"]):
        print("\n" + "⚠️ " * 20)
        print("⚠️  WARNING: This does not appear to be a test channel!")
        print(f"⚠️  Channel: {selected_channel['displayName']}")
        print("⚠️ " * 20)

        confirm = input(
            "\nAre you ABSOLUTELY SURE you want to send to this channel? (type 'YES' to confirm): "
        )
        if confirm != "YES":
            print("❌ Test cancelled for safety")
            return

    # 最終確認
    print("\n" + "=" * 60)
    print("FINAL CONFIRMATION")
    print("=" * 60)
    print(f"Team:    {selected_team['displayName']}")
    print(f"Channel: {selected_channel['displayName']}")
    print("\nA test message will be sent with:")
    print("  - Title: 🔥 ホットリード獲得！")
    print("  - Company: テスト株式会社")
    print("  - Contact: テスト太郎 (テスト部長)")
    print("  - Score: 95/100")
    print("=" * 60)

    final_confirm = input("\nType 'SEND' to proceed: ")
    if final_confirm != "SEND":
        print("❌ Test cancelled by user")
        return

    # テストメッセージを送信
    print("\n6. Sending test message...")

    # サンプルリードデータ
    lead_data = {
        "lead_id": "lead_test_001",
        "company_name": "テスト株式会社",
        "contact_name": "テスト太郎",
        "job_title": "テスト部長",
        "email": "test@example.com",
        "phone": "03-0000-0000",
        "score": 95,
        "assessment_title": "【テスト送信】営業課題診断",
    }

    try:
        result = await client.send_hot_lead_notification(
            team_id=selected_team["id"],
            channel_id=selected_channel["id"],
            lead_data=lead_data,
        )

        print("\n" + "=" * 60)
        print("✅ MESSAGE SENT SUCCESSFULLY!")
        print("=" * 60)
        print(f"Message ID: {result.get('id')}")
        print(f"Created at: {result.get('created_at')}")
        if result.get("web_url"):
            print(f"Web URL: {result.get('web_url')}")
        print(f"\nTeam: {selected_team['displayName']}")
        print(f"Channel: {selected_channel['displayName']}")
        print("\n✅ Please check the Teams channel to verify the message.")

    except Exception as e:
        error_message = str(e)

        if (
            "ChannelMessage.Send" in error_message
            or "permission" in error_message.lower()
        ):
            print("\n" + "=" * 60)
            print("❌ PERMISSION REQUIRED: ChannelMessage.Send")
            print("=" * 60)
            print("\nThe 'ChannelMessage.Send' permission is not granted.")
            print("\nTo add this permission:")
            print("1. Go to Azure Portal (https://portal.azure.com)")
            print("2. Navigate to: Azure Active Directory → App registrations")
            print("3. Select: DiagnoLeads Teams Integration localhost")
            print("4. Click: API permissions → Add a permission")
            print("5. Select: Microsoft Graph → Application permissions")
            print("6. Search and add: ChannelMessage.Send")
            print("7. Click: Grant admin consent for [Your Organization]")
            print("8. Wait 5-10 minutes for changes to propagate")
            print("\nThen run this script again.")
            print("=" * 60)
        else:
            print(f"\n❌ Error: {error_message}")

    print("\n" + "=" * 60)
    print("Test completed")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
