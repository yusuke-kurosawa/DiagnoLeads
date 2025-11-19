"""
Microsoft Teams Incoming Webhook Client
シンプルで安全なメッセージ送信方法
"""

from typing import Dict, Optional
import httpx
from datetime import datetime


class TeamsWebhookClient:
    """
    Incoming Webhookを使用したTeams通知クライアント

    メリット:
    - Azure AD権限不要
    - シンプルな実装
    - チャネルごとに個別設定可能

    制限:
    - チャネルごとにWebhook URLが必要
    - 双方向通信不可
    - @メンションは制限あり
    """

    def __init__(self, webhook_url: str):
        """
        Teams Webhook Client初期化

        Args:
            webhook_url: Teams Incoming Webhook URL
                        (例: https://your-tenant.webhook.office.com/webhookb2/...)
        """
        self.webhook_url = webhook_url

        if not webhook_url or not webhook_url.startswith("https://"):
            raise ValueError("Valid webhook URL is required")

    async def send_adaptive_card(self, card: Dict) -> Dict:
        """
        Adaptive Cardを送信

        Args:
            card: Adaptive Card JSON

        Returns:
            送信結果
        """
        # Webhook APIのメッセージフォーマット
        message = {
            "type": "message",
            "attachments": [
                {
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "contentUrl": None,
                    "content": card,
                }
            ],
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(self.webhook_url, json=message)
                response.raise_for_status()

                print("✅ Adaptive Card sent successfully via Webhook")
                return {
                    "status": "sent",
                    "sent_at": datetime.now().isoformat(),
                    "method": "webhook",
                }

        except httpx.HTTPStatusError as e:
            print(f"❌ Failed to send message: {e.response.status_code}")
            print(f"Response: {e.response.text}")

            if e.response.status_code == 400:
                raise Exception("Invalid card format or webhook URL")
            elif e.response.status_code == 404:
                raise Exception(
                    "Webhook URL not found. Please check the URL or recreate the webhook in Teams."
                )
            else:
                raise

        except Exception as e:
            print(f"❌ Error sending message: {str(e)}")
            raise

    async def send_simple_message(self, text: str, title: Optional[str] = None) -> Dict:
        """
        シンプルなテキストメッセージを送信

        Args:
            text: メッセージ本文
            title: タイトル（オプション）

        Returns:
            送信結果
        """
        # MessageCard形式（シンプルなメッセージ用）
        message = {
            "@type": "MessageCard",
            "@context": "https://schema.org/extensions",
            "summary": title or text[:50],
            "title": title,
            "text": text,
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(self.webhook_url, json=message)
                response.raise_for_status()

                print("✅ Message sent successfully via Webhook")
                return {
                    "status": "sent",
                    "sent_at": datetime.now().isoformat(),
                    "method": "webhook",
                }

        except Exception as e:
            print(f"❌ Error sending message: {str(e)}")
            raise

    async def send_hot_lead_notification(
        self, lead_data: Dict, dashboard_url: Optional[str] = None
    ) -> Dict:
        """
        ホットリード通知を送信

        Args:
            lead_data: リードデータ（会社名、担当者、スコアなど）
            dashboard_url: DiagnoLeadsダッシュボードURL

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
                                    "items": [
                                        {
                                            "type": "TextBlock",
                                            "text": "🔥",
                                            "size": "extraLarge",
                                        }
                                    ],
                                },
                                {
                                    "type": "Column",
                                    "width": "stretch",
                                    "items": [
                                        {
                                            "type": "TextBlock",
                                            "text": "ホットリード獲得！",
                                            "weight": "bolder",
                                            "size": "large",
                                        },
                                        {
                                            "type": "TextBlock",
                                            "text": f"スコア: {lead_data.get('score', 0)}/100",
                                            "color": "attention",
                                            "weight": "bolder",
                                        },
                                    ],
                                },
                            ],
                        }
                    ],
                },
                {
                    "type": "FactSet",
                    "facts": [
                        {
                            "title": "会社名",
                            "value": lead_data.get("company_name", "N/A"),
                        },
                        {
                            "title": "担当者",
                            "value": f"{lead_data.get('contact_name', 'N/A')} ({lead_data.get('job_title', 'N/A')})",
                        },
                        {"title": "メール", "value": lead_data.get("email", "N/A")},
                        {"title": "電話", "value": lead_data.get("phone", "未提供")},
                        {
                            "title": "診断",
                            "value": lead_data.get("assessment_title", "N/A"),
                        },
                    ],
                },
            ],
        }

        # ダッシュボードリンクがある場合はアクションボタンを追加
        if dashboard_url:
            card["actions"] = [
                {
                    "type": "Action.OpenUrl",
                    "title": "リードを見る",
                    "url": dashboard_url,
                }
            ]

        return await self.send_adaptive_card(card)


# テスト用
async def main():
    """動作テスト"""
    import os
    from dotenv import load_dotenv

    load_dotenv()

    webhook_url = os.getenv("TEAMS_WEBHOOK_URL")

    if not webhook_url:
        print("❌ TEAMS_WEBHOOK_URL environment variable not set")
        print("\nTo set up:")
        print("1. Go to Teams channel → ... → Connectors")
        print("2. Configure 'Incoming Webhook'")
        print("3. Copy the webhook URL")
        print("4. Add to backend/.env: TEAMS_WEBHOOK_URL=<your-url>")
        return

    print("=" * 60)
    print("Teams Webhook Client Test")
    print("=" * 60)

    client = TeamsWebhookClient(webhook_url)

    # テスト1: シンプルメッセージ
    print("\n1. Testing simple message...")
    try:
        await client.send_simple_message(
            title="テスト通知", text="これはDiagnoLeadsからのテストメッセージです。"
        )
        print("✅ Simple message sent")
    except Exception as e:
        print(f"❌ Failed: {e}")

    # テスト2: Adaptive Card
    print("\n2. Testing Adaptive Card...")
    lead_data = {
        "lead_id": "lead_webhook_test_001",
        "company_name": "Webhook株式会社",
        "contact_name": "Webhook太郎",
        "job_title": "Webhook部長",
        "email": "webhook@example.com",
        "phone": "03-XXXX-XXXX",
        "score": 98,
        "assessment_title": "【Webhookテスト】診断",
    }

    try:
        await client.send_hot_lead_notification(
            lead_data=lead_data,
            dashboard_url="https://app.diagnoleads.com/leads/webhook_test_001",
        )
        print("✅ Adaptive Card sent")
    except Exception as e:
        print(f"❌ Failed: {e}")

    print("\n" + "=" * 60)
    print("Test completed. Check your Teams channel!")
    print("=" * 60)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
