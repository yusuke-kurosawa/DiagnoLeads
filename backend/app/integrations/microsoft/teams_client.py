"""
Microsoft Teams Client - Technical Spike Prototype
最小限のTeams統合プロトタイプ
"""
from typing import Dict, Optional
import json
from datetime import datetime


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
        # プロトタイプ: ダミートークン返却
        # 本実装:
        # result = self.msal_app.acquire_token_for_client(
        #     scopes=["https://graph.microsoft.com/.default"]
        # )
        # self._access_token = result["access_token"]
        # return self._access_token
        
        print(f"[PROTOTYPE] Authenticating with tenant: {self.tenant_id}")
        self._access_token = "dummy_access_token_for_prototype"
        return self._access_token
    
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
    
    async def get_teams(self) -> list:
        """
        ユーザーが所属するチーム一覧を取得
        
        Returns:
            チームリスト
        """
        print("[PROTOTYPE] Getting teams list")
        # プロトタイプ: ダミーデータ
        return [
            {"id": "team_001", "displayName": "営業チーム"},
            {"id": "team_002", "displayName": "マーケティングチーム"},
        ]
    
    async def get_channels(self, team_id: str) -> list:
        """
        チームのチャネル一覧を取得
        
        Args:
            team_id: Team ID
            
        Returns:
            チャネルリスト
        """
        print(f"[PROTOTYPE] Getting channels for team: {team_id}")
        # プロトタイプ: ダミーデータ
        return [
            {"id": "channel_001", "displayName": "一般"},
            {"id": "channel_002", "displayName": "リード通知"},
        ]


# プロトタイプテスト用
async def main():
    """プロトタイプテスト"""
    print("=" * 60)
    print("Microsoft Teams Integration - Technical Spike Prototype")
    print("=" * 60)
    
    # Teams Client初期化
    client = TeamsClient(
        tenant_id="your-tenant-id",
        client_id="your-client-id",
        client_secret="your-client-secret"
    )
    
    # 認証
    print("\n1. Authentication Test")
    await client.authenticate()
    print("✅ Authentication successful")
    
    # チーム取得
    print("\n2. Get Teams Test")
    teams = await client.get_teams()
    print(f"✅ Found {len(teams)} teams")
    for team in teams:
        print(f"  - {team['displayName']} (ID: {team['id']})")
    
    # チャネル取得
    print("\n3. Get Channels Test")
    channels = await client.get_channels("team_001")
    print(f"✅ Found {len(channels)} channels")
    for channel in channels:
        print(f"  - {channel['displayName']} (ID: {channel['id']})")
    
    # ホットリード通知送信
    print("\n4. Send Hot Lead Notification Test")
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
    
    result = await client.send_hot_lead_notification(
        team_id="team_001",
        channel_id="channel_002",
        lead_data=lead_data,
        mention_user_id="user_12345"
    )
    print(f"✅ Notification sent: {result['id']}")
    
    print("\n" + "=" * 60)
    print("Prototype Test Completed Successfully! 🎉")
    print("=" * 60)
    print("\n次のステップ:")
    print("1. Azure AD App登録")
    print("2. msal、msgraph-sdkライブラリのインストール")
    print("3. 本実装のコメント解除")
    print("4. 実際のTeamsアカウントでテスト")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
