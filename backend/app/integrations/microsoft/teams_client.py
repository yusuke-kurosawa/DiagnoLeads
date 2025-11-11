"""
Microsoft Teams Client - Technical Spike Prototype
最小限のTeams統合プロトタイプ
"""
from typing import Dict, Optional, List
import json
import os
from datetime import datetime
import httpx


class TeamsClient:
    """
    Microsoft Teams API クライアント（プロトタイプ版）
    
    本実装では以下を使用：
    - msal: Azure AD認証
    - msgraph: Microsoft Graph API
    
    このプロトタイプでは基本構造のみを定義
    """
    
    def __init__(
        self, 
        tenant_id: str, 
        client_id: str, 
        client_secret: str
    ):
        """
        Teams Client初期化
        
        Args:
            tenant_id: Azure AD Tenant ID
            client_id: Application (client) ID
            client_secret: Client Secret Value
        """
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self._access_token: Optional[str] = None
        
        # 本実装では以下を追加:
        # from msal import ConfidentialClientApplication
        # self.msal_app = ConfidentialClientApplication(
        #     client_id=client_id,
        #     client_credential=client_secret,
        #     authority=f"https://login.microsoftonline.com/{tenant_id}"
        # )
    
    async def authenticate(self) -> str:
        """
        Azure ADで認証してアクセストークンを取得
        
        Returns:
            Access token
        """
        # OAuth 2.0 Client Credentials Flow
        token_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": "https://graph.microsoft.com/.default",
            "grant_type": "client_credentials"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(token_url, data=data)
                response.raise_for_status()
                result = response.json()
                self._access_token = result["access_token"]
                print(f"✅ Authentication successful for tenant: {self.tenant_id}")
                return self._access_token
        except httpx.HTTPStatusError as e:
            print(f"❌ Authentication failed: {e.response.status_code}")
            print(f"Response: {e.response.text}")
            raise
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            raise
    
    async def send_adaptive_card(
        self,
        team_id: str,
        channel_id: str,
        card: Dict
    ) -> Dict:
        """
        Teams チャネルにAdaptive Cardを送信
        
        Args:
            team_id: Teams ID
            channel_id: Channel ID
            card: Adaptive Card JSON
            
        Returns:
            送信結果
        """
        # プロトタイプ: ログ出力のみ
        # 本実装:
        # from msgraph import GraphServiceClient
        # message = {
        #     "body": {
        #         "contentType": "html",
        #         "content": "<attachment id='card'></attachment>"
        #     },
        #     "attachments": [{
        #         "id": "card",
        #         "contentType": "application/vnd.microsoft.card.adaptive",
        #         "content": json.dumps(card)
        #     }]
        # }
        # result = await self.graph_client.teams.by_team_id(team_id)\
        #     .channels.by_channel_id(channel_id)\
        #     .messages.post(message)
        
        print(f"[PROTOTYPE] Sending Adaptive Card to team={team_id}, channel={channel_id}")
        print(f"Card content: {json.dumps(card, indent=2, ensure_ascii=False)}")
        
        return {
            "id": "msg_prototype_123",
            "created_at": datetime.now().isoformat(),
            "status": "sent"
        }
    
    async def send_hot_lead_notification(
        self,
        team_id: str,
        channel_id: str,
        lead_data: Dict,
        mention_user_id: Optional[str] = None
    ) -> Dict:
        """
        ホットリード通知をTeamsに送信
        
        Args:
            team_id: Teams ID
            channel_id: Channel ID
            lead_data: リードデータ（会社名、担当者、スコアなど）
            mention_user_id: メンション対象ユーザーID
            
        Returns:
            送信結果
        """
        # Adaptive Card作成
        card = {
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "type": "AdaptiveCard",
            "version": "1.5",
            "body": [
                {
                    "type": "Container",
                    "style": "attention",
                    "items": [
                        {
                            "type": "ColumnSet",
                            "columns": [
                                {
                                    "type": "Column",
                                    "width": "auto",
                                    "items": [{
                                        "type": "TextBlock",
                                        "text": "🔥",
                                        "size": "extraLarge"
                                    }]
                                },
                                {
                                    "type": "Column",
                                    "width": "stretch",
                                    "items": [
                                        {
                                            "type": "TextBlock",
                                            "text": "ホットリード獲得！",
                                            "weight": "bolder",
                                            "size": "large"
                                        },
                                        {
                                            "type": "TextBlock",
                                            "text": f"スコア: {lead_data.get('score', 0)}/100",
                                            "color": "attention",
                                            "weight": "bolder"
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                },
                {
                    "type": "FactSet",
                    "facts": [
                        {"title": "会社名", "value": lead_data.get("company_name", "N/A")},
                        {"title": "担当者", "value": f"{lead_data.get('contact_name', 'N/A')} ({lead_data.get('job_title', 'N/A')})"},
                        {"title": "メール", "value": lead_data.get("email", "N/A")},
                        {"title": "電話", "value": lead_data.get("phone", "未提供")},
                        {"title": "診断", "value": lead_data.get("assessment_title", "N/A")},
                    ]
                }
            ],
            "actions": [
                {
                    "type": "Action.OpenUrl",
                    "title": "リードを見る",
                    "url": f"https://app.diagnoleads.com/leads/{lead_data.get('lead_id', '')}"
                }
            ]
        }
        
        # メンション追加（本実装で対応）
        if mention_user_id:
            card["msteams"] = {
                "entities": [{
                    "type": "mention",
                    "text": f"<at>{mention_user_id}</at>",
                    "mentioned": {
                        "id": mention_user_id,
                        "name": "営業担当"
                    }
                }]
            }
        
        return await self.send_adaptive_card(team_id, channel_id, card)
    
    async def get_teams(self) -> List[Dict]:
        """
        組織内のチーム一覧を取得
        
        Returns:
            チームリスト
        """
        if not self._access_token:
            await self.authenticate()
        
        graph_url = "https://graph.microsoft.com/v1.0/groups?$filter=resourceProvisioningOptions/Any(x:x eq 'Team')"
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(graph_url, headers=headers)
                response.raise_for_status()
                result = response.json()
                teams = result.get("value", [])
                print(f"✅ Found {len(teams)} teams")
                return teams
        except httpx.HTTPStatusError as e:
            print(f"❌ Failed to get teams: {e.response.status_code}")
            print(f"Response: {e.response.text}")
            raise
        except Exception as e:
            print(f"❌ Error getting teams: {str(e)}")
            raise
    
    async def get_channels(self, team_id: str) -> List[Dict]:
        """
        チームのチャネル一覧を取得
        
        Args:
            team_id: Team ID
            
        Returns:
            チャネルリスト
        """
        if not self._access_token:
            await self.authenticate()
        
        graph_url = f"https://graph.microsoft.com/v1.0/teams/{team_id}/channels"
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(graph_url, headers=headers)
                response.raise_for_status()
                result = response.json()
                channels = result.get("value", [])
                print(f"✅ Found {len(channels)} channels in team {team_id}")
                return channels
        except httpx.HTTPStatusError as e:
            print(f"❌ Failed to get channels: {e.response.status_code}")
            print(f"Response: {e.response.text}")
            raise
        except Exception as e:
            print(f"❌ Error getting channels: {str(e)}")
            raise


# プロトタイプテスト用
async def main():
    """プロトタイプテスト"""
    print("=" * 60)
    print("Microsoft Teams Integration - Live Test")
    print("=" * 60)
    
    # .envファイルから環境変数を読み込み
    from dotenv import load_dotenv
    load_dotenv()
    
    # 環境変数から認証情報を読み込み
    tenant_id = os.getenv("MICROSOFT_TENANT_ID")
    client_id = os.getenv("MICROSOFT_CLIENT_ID")
    client_secret = os.getenv("MICROSOFT_CLIENT_SECRET")
    
    if not all([tenant_id, client_id, client_secret]):
        print("❌ Error: Missing environment variables")
        print("Required: MICROSOFT_TENANT_ID, MICROSOFT_CLIENT_ID, MICROSOFT_CLIENT_SECRET")
        return
    
    # Teams Client初期化
    client = TeamsClient(
        tenant_id=tenant_id,
        client_id=client_id,
        client_secret=client_secret
    )
    
    # 認証
    print("\n1. Authentication Test")
    await client.authenticate()
    print("✅ Authentication successful")
    
    # チーム取得
    print("\n2. Get Teams Test")
    teams = await client.get_teams()
    print(f"✅ Found {len(teams)} teams")
    for i, team in enumerate(teams[:5]):  # 最初の5チームのみ表示
        print(f"  {i+1}. {team['displayName']} (ID: {team['id']})")
    
    if not teams:
        print("⚠️  No teams found. Cannot continue with channel test.")
        return
    
    # 最初のチームでチャネル取得をテスト
    first_team = teams[0]
    print(f"\n3. Get Channels Test (Team: {first_team['displayName']})")
    channels = await client.get_channels(first_team['id'])
    print(f"✅ Found {len(channels)} channels")
    for i, channel in enumerate(channels[:5]):  # 最初の5チャネルのみ表示
        print(f"  {i+1}. {channel['displayName']} (ID: {channel['id']})")
    
    # ホットリード通知送信テスト（実際の送信はスキップ）
    print("\n4. Hot Lead Notification Test (Dry Run)")
    lead_data = {
        "lead_id": "lead_12345",
        "company_name": "株式会社サンプル",
        "contact_name": "山田太郎",
        "job_title": "営業部長",
        "email": "yamada@example.com",
        "phone": "03-1234-5678",
        "score": 92,
        "assessment_title": "営業課題診断"
    }
    
    print("Sample notification data:")
    print(f"  Company: {lead_data['company_name']}")
    print(f"  Contact: {lead_data['contact_name']} ({lead_data['job_title']})")
    print(f"  Score: {lead_data['score']}/100")
    print("\n⚠️  Note: Actual message sending is not implemented in this test.")
    print("    To send messages, you need 'ChannelMessage.Send' permission.")
    
    print("\n" + "=" * 60)
    print("Test Completed Successfully! 🎉")
    print("=" * 60)
    print("\n✅ Teams integration is working correctly!")
    print("Next steps:")
    print("1. Add 'ChannelMessage.Send' permission for actual message sending")
    print("2. Implement Bot Framework webhook endpoint")
    print("3. Create Teams App Manifest")
    print("4. Sideload app to Microsoft Teams")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
