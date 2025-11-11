"""
Microsoft Teams メッセージ送信テストスクリプト
ChannelMessage.Send権限が必要
"""
import asyncio
import os
import sys
from dotenv import load_dotenv

# Import the TeamsClient
sys.path.insert(0, os.path.dirname(__file__))
from app.integrations.microsoft.teams_client import TeamsClient

load_dotenv()

async def main():
    print("\n" + "="*60)
    print("Microsoft Teams - Message Sending Test")
    print("="*60)
    
    # 環境変数から認証情報を読み込み
    tenant_id = os.getenv("MICROSOFT_TENANT_ID")
    client_id = os.getenv("MICROSOFT_CLIENT_ID")
    client_secret = os.getenv("MICROSOFT_CLIENT_SECRET")
    
    if not all([tenant_id, client_id, client_secret]):
        print("❌ Error: Missing environment variables")
        return
    
    # Teams Client初期化
    client = TeamsClient(
        tenant_id=tenant_id,
        client_id=client_id,
        client_secret=client_secret
    )
    
    # 認証
    print("\n1. Authenticating...")
    try:
        await client.authenticate()
        print("✅ Authentication successful")
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return
    
    # チーム取得
    print("\n2. Getting teams...")
    try:
        teams = await client.get_teams()
        if not teams:
            print("❌ No teams found")
            return
        print(f"✅ Found {len(teams)} teams")
        print("\nAvailable teams:")
        for i, team in enumerate(teams[:10]):
            print(f"  {i+1}. {team['displayName']} (ID: {team['id']})")
    except Exception as e:
        print(f"❌ Failed to get teams: {e}")
        return
    
    # 最初のチームを選択
    selected_team = teams[0]
    print(f"\n3. Selected team: {selected_team['displayName']}")
    
    # チャネル取得
    print("\n4. Getting channels...")
    try:
        channels = await client.get_channels(selected_team['id'])
        if not channels:
            print("❌ No channels found")
            return
        print(f"✅ Found {len(channels)} channels")
        print("\nAvailable channels:")
        for i, channel in enumerate(channels[:10]):
            print(f"  {i+1}. {channel['displayName']} (ID: {channel['id']})")
    except Exception as e:
        print(f"❌ Failed to get channels: {e}")
        return
    
    # 最初のチャネルを選択
    selected_channel = channels[0]
    print(f"\n5. Selected channel: {selected_channel['displayName']}")
    
    # 確認
    print("\n" + "="*60)
    print("⚠️  WARNING: This will send a test message to Teams!")
    print(f"Team: {selected_team['displayName']}")
    print(f"Channel: {selected_channel['displayName']}")
    print("="*60)
    
    user_input = input("\nDo you want to proceed? (yes/no): ")
    if user_input.lower() != 'yes':
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
        "assessment_title": "テスト診断"
    }
    
    try:
        result = await client.send_hot_lead_notification(
            team_id=selected_team['id'],
            channel_id=selected_channel['id'],
            lead_data=lead_data
        )
        
        print("\n" + "="*60)
        print("✅ MESSAGE SENT SUCCESSFULLY!")
        print("="*60)
        print(f"Message ID: {result.get('id')}")
        print(f"Created at: {result.get('created_at')}")
        if result.get('web_url'):
            print(f"Web URL: {result.get('web_url')}")
        print("\nPlease check the Teams channel to verify the message.")
        
    except Exception as e:
        error_message = str(e)
        
        if "ChannelMessage.Send" in error_message:
            print("\n" + "="*60)
            print("❌ PERMISSION REQUIRED")
            print("="*60)
            print("\nThe 'ChannelMessage.Send' permission is not granted.")
            print("\nTo fix this:")
            print("1. Go to Azure Portal → App registrations")
            print("2. Select your app → API permissions")
            print("3. Add 'ChannelMessage.Send' under Microsoft Graph → Application permissions")
            print("4. Click 'Grant admin consent for [Your Organization]'")
            print("5. Wait 5-10 minutes and try again")
            print("\n" + "="*60)
        else:
            print(f"\n❌ Error: {error_message}")
    
    print("\n" + "="*60)
    print("Test completed")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())
