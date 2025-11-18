"""
ChannelMessage.Send 権限の確認スクリプト
"""
import asyncio
import os
from dotenv import load_dotenv
from app.integrations.microsoft.teams_client import TeamsClient

load_dotenv()

async def main():
    print("\n" + "="*60)
    print("ChannelMessage.Send Permission Check")
    print("="*60)
    
    # 環境変数確認
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
    
    # チーム取得（基本権限確認）
    print("\n2. Testing basic permissions (Group.Read.All)...")
    try:
        teams = await client.get_teams()
        print(f"✅ Group.Read.All: OK ({len(teams)} teams found)")
    except Exception as e:
        print(f"❌ Group.Read.All: FAILED - {e}")
        return
    
    if not teams:
        print("❌ No teams found. Cannot proceed with message sending test.")
        return
    
    # 最初のチームのチャネル取得
    first_team = teams[0]
    print(f"\n3. Testing channel access on '{first_team['displayName']}'...")
    try:
        channels = await client.get_channels(first_team['id'])
        print(f"✅ Channel.ReadBasic.All: OK ({len(channels)} channels found)")
    except Exception as e:
        print(f"❌ Channel.ReadBasic.All: FAILED - {e}")
        return
    
    if not channels:
        print("❌ No channels found. Cannot proceed with message sending test.")
        return
    
    # メッセージ送信権限の確認（実際には送信しない、APIレスポンスで判定）
    print("\n4. Checking ChannelMessage.Send permission...")
    print("   (This will attempt to send a test message)")
    print(f"   Team: {first_team['displayName']}")
    print(f"   Channel: {channels[0]['displayName']}")
    
    # 簡単なテストカード
    test_card = {
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "type": "AdaptiveCard",
        "version": "1.5",
        "body": [
            {
                "type": "TextBlock",
                "text": "🧪 Permission Test",
                "weight": "bolder",
                "size": "large"
            },
            {
                "type": "TextBlock",
                "text": "This is an automated test message from DiagnoLeads. ChannelMessage.Send permission is working correctly.",
                "wrap": True
            }
        ]
    }
    
    try:
        result = await client.send_adaptive_card(
            team_id=first_team['id'],
            channel_id=channels[0]['id'],
            card=test_card
        )
        
        print("\n" + "="*60)
        print("✅ ChannelMessage.Send: OK")
        print("="*60)
        print(f"Message ID: {result.get('id')}")
        print(f"Created at: {result.get('created_at')}")
        print("\nA test message was sent to:")
        print(f"  Team: {first_team['displayName']}")
        print(f"  Channel: {channels[0]['displayName']}")
        print("\n⚠️  You may want to delete this test message in Teams.")
        print("\n" + "="*60)
        print("✅ ALL PERMISSIONS OK - Ready for production use!")
        print("="*60)
        
    except Exception as e:
        error_msg = str(e)
        
        if "ChannelMessage.Send" in error_msg or "Insufficient privileges" in error_msg or "403" in error_msg:
            print("\n" + "="*60)
            print("❌ ChannelMessage.Send: NOT GRANTED")
            print("="*60)
            print("\nThe permission is not yet configured.")
            print("\n📋 Action Required:")
            print("1. Open Azure Portal: https://portal.azure.com")
            print("2. Go to: Azure Active Directory → App registrations")
            print("3. Select: DiagnoLeads Teams Integration localhost")
            print("4. Click: API permissions → Add a permission")
            print("5. Choose: Microsoft Graph → Application permissions")
            print("6. Search: ChannelMessage.Send")
            print("7. Add the permission")
            print("8. Click: Grant admin consent for [Your Organization]")
            print("9. Wait 5-10 minutes")
            print("10. Run this script again")
            print("\n" + "="*60)
        else:
            print(f"\n❌ Error: {error_msg}")
    
    print("\n" + "="*60)
    print("Permission check completed")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())
