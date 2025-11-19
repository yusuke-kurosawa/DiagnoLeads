# Microsoft Teams Native Integration

**Status**: Approved (Phase 1 実装済み)
**Priority**: Critical
**Phase**: Phase 1 完了 / Phase 2-3 計画中
**Estimated Effort**: Phase 1 完了 (6週間) / Phase 2-3 (8-12週間)
**Dependencies**: Microsoft Graph API, Bot Framework SDK

## Implementation Status

### ✅ Phase 1: 基本Webhook統合（完了）
- ✅ Incoming Webhook経由でのリード通知
- ✅ Adaptive Cardsでのリッチな通知UI
- ✅ リトライロジック（最大3回、指数バックオフ）
- ✅ テスト送信機能
- ✅ 暗号化されたWebhook URL保存
- ⚠️ テストカバレッジの充実化が必要

### 🔄 Phase 2: Bot統合（次期スプリント）
- Teams Bot経由での診断配信
- チャット内での対話型診断
- メンション通知機能
- Bot Commands実装
- **推定工数**: 3-4週間

### 📋 Phase 3: 高度な統合（中長期）
- Teams会議内での診断実施
- SharePoint統合
- Microsoft Graph API完全統合
- Teams Appストア配信
- **推定工数**: 8-12週間

## Overview

Microsoft Teamsとのネイティブ統合により、企業ユーザーが最も使用するコミュニケーションツール内で診断を配信・管理できるようにします。Slack統合より優先度が高く、エンタープライズ市場での競争優位性を確立します。

## Business Value

- **エンタープライズ獲得率**: +300%（Fortune 500の85%がTeamsを使用）
- **リード対応速度**: 平均2時間 → 5分（即座にTeams通知）
- **営業チーム生産性**: +50%（Teamsから離れずに完結）
- **競合優位性**: 主要競合にはない機能

## User Stories

### 1. Teams Bot経由での診断配信

**As a** マーケティング担当者  
**I want to** Teamsチャネルに診断を投稿  
**So that** チームメンバーが簡単に診断を共有・回答できる

**Acceptance Criteria**:

**Given**: テナントがTeams連携を有効化している  
**When**: ダッシュボードから「Teamsで共有」をクリック  
**Then**: 
- Teams Bot選択ダイアログが表示される
- 対象チャネルを選択
- Adaptive Card形式で診断リンクが投稿される
- カード内に診断タイトル、説明、推定所要時間、開始ボタンが含まれる

### 2. リアルタイムホットリード通知

**As a** 営業担当者  
**I want to** ホットリードがTeamsに即座に通知される  
**So that** すぐにフォローアップできる

**Acceptance Criteria**:

**Given**: リードスコアが80以上のホットリードが獲得される  
**When**: 診断回答が完了する  
**Then**:
- 指定されたTeamsチャネルに通知が投稿される
- Adaptive Card形式で以下を表示：
  - 🔥 ホットリードアイコン
  - 会社名、担当者名、役職
  - リードスコア（数値とビジュアル）
  - 診断名と回答サマリー
  - 「リードを見る」ボタン（DiagnoLeadsダッシュボードへのリンク）
  - 「カレンダーに追加」ボタン（フォローアップ予定を自動作成）
- 担当営業にメンション（@山田太郎）

### 3. Teams会議内での診断実施

**As a** ウェビナー主催者  
**I want to** Teams会議中に参加者に診断を実施  
**So that** その場でリードを獲得できる

**Acceptance Criteria**:

**Given**: Teams会議が進行中  
**When**: 主催者がTeams Appから診断を起動  
**Then**:
- 参加者全員に診断が表示される（Meeting Stage拡張機能）
- 参加者は会議を離れずに回答可能
- リアルタイム完了状況が主催者に表示される
- 会議終了後、自動的にリード情報がダッシュボードに同期

### 4. Teams Bot対話型診断

**As a** 診断回答者  
**I want to** Teamsチャット内で診断に回答  
**So that** 外部リンクに移動せずに完結できる

**Acceptance Criteria**:

**Given**: Teams BotにDM（ダイレクトメッセージ）を送信  
**When**: 「診断を開始」とメッセージ送信  
**Then**:
- Bot が質問を1つずつ送信
- ユーザーが回答（ボタンまたはテキスト入力）
- 進捗状況表示（3/8問完了）
- 完了後、結果カードを表示
- オプションで詳細レポートへのリンク

## Technical Architecture

### Microsoft Graph API統合

```python
# backend/app/integrations/microsoft/teams_client.py
from msgraph import GraphServiceClient
from azure.identity import ClientSecretCredential

class TeamsClient:
    def __init__(self, tenant_id: str, client_id: str, client_secret: str):
        credential = ClientSecretCredential(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret
        )
        self.client = GraphServiceClient(credential)
    
    async def send_adaptive_card(
        self, 
        team_id: str, 
        channel_id: str, 
        card: dict
    ) -> dict:
        """Adaptive Cardをチャネルに投稿"""
        message = {
            "body": {
                "contentType": "html",
                "content": "<attachment id='card'></attachment>"
            },
            "attachments": [{
                "id": "card",
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": json.dumps(card)
            }]
        }
        
        result = await self.client.teams.by_team_id(team_id)\
            .channels.by_channel_id(channel_id)\
            .messages.post(message)
        
        return result
    
    async def send_hot_lead_notification(
        self,
        channel_id: str,
        lead: Lead,
        mention_user_id: str = None
    ):
        """ホットリード通知"""
        card = self._build_hot_lead_card(lead, mention_user_id)
        await self.send_adaptive_card(
            team_id=lead.tenant.teams_team_id,
            channel_id=channel_id,
            card=card
        )
```

### Adaptive Card Template

```python
def _build_hot_lead_card(self, lead: Lead, mention_user_id: str = None) -> dict:
    """ホットリード通知用Adaptive Card"""
    return {
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
                                        "text": f"スコア: {lead.score}/100",
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
                    {"title": "会社名", "value": lead.company_name},
                    {"title": "担当者", "value": f"{lead.contact_name} ({lead.job_title})"},
                    {"title": "メール", "value": lead.email},
                    {"title": "電話", "value": lead.phone or "未提供"},
                    {"title": "診断", "value": lead.assessment.title},
                    {"title": "完了時刻", "value": lead.created_at.strftime("%Y-%m-%d %H:%M")}
                ]
            },
            {
                "type": "TextBlock",
                "text": "**主な課題**",
                "weight": "bolder",
                "separator": True
            },
            {
                "type": "TextBlock",
                "text": lead.ai_insights.get("pain_points", "分析中..."),
                "wrap": True
            }
        ],
        "actions": [
            {
                "type": "Action.OpenUrl",
                "title": "リードを見る",
                "url": f"{settings.FRONTEND_URL}/leads/{lead.id}"
            },
            {
                "type": "Action.OpenUrl",
                "title": "カレンダーに追加",
                "url": self._generate_calendar_link(lead)
            }
        ],
        "msteams": {
            "entities": [
                {
                    "type": "mention",
                    "text": f"<at>{mention_user_id}</at>",
                    "mentioned": {
                        "id": mention_user_id,
                        "name": "営業担当"
                    }
                }
            ] if mention_user_id else []
        }
    }
```

### Bot Framework統合

```python
# backend/app/integrations/microsoft/teams_bot.py
from botbuilder.core import BotFrameworkAdapter, TurnContext
from botbuilder.schema import Activity, ActivityTypes

class DiagnoLeadsTeamsBot:
    def __init__(self, app_id: str, app_password: str):
        self.adapter = BotFrameworkAdapter(
            app_id=app_id,
            app_password=app_password
        )
    
    async def on_message_activity(self, turn_context: TurnContext):
        """メッセージ受信時の処理"""
        text = turn_context.activity.text.lower()
        
        if "診断" in text or "start" in text:
            await self._start_assessment(turn_context)
        elif text.isdigit():
            await self._process_answer(turn_context, int(text))
        else:
            await turn_context.send_activity(
                "診断を開始するには「診断を開始」と送信してください。"
            )
    
    async def _start_assessment(self, turn_context: TurnContext):
        """診断開始"""
        user_id = turn_context.activity.from_property.id
        
        # セッション作成
        session = await self._create_assessment_session(user_id)
        
        # 最初の質問を送信
        card = self._build_question_card(session.current_question)
        await turn_context.send_activity(Activity(
            type=ActivityTypes.message,
            attachments=[card]
        ))
```

## API Endpoints

### Teams連携管理

```
POST   /api/v1/integrations/teams/install
       - Teams App をテナントにインストール
       - Request Body: { tenant_id, team_id, channel_id, auth_code }
       - Response: { integration_id, status, webhook_url }

GET    /api/v1/integrations/teams
       - テナントのTeams連携一覧を取得
       - Response: [{ id, team_name, channel_name, status }]

DELETE /api/v1/integrations/teams/{integration_id}
       - Teams連携を削除

GET    /api/v1/integrations/teams/channels
       - 利用可能なTeamsチャネル一覧
       - Response: [{ team_id, team_name, channels: [...] }]
```

### 診断配信

```
POST   /api/v1/integrations/teams/send-assessment
       - Teamsチャネルに診断を投稿
       - Request Body: { 
           assessment_id, 
           team_id, 
           channel_id,
           message: "optional custom message"
         }
       - Response: { message_id, posted_at }

POST   /api/v1/integrations/teams/send-dm
       - Teams DMで診断を送信
       - Request Body: { assessment_id, user_id }
```

### リード通知

```
POST   /api/v1/integrations/teams/notify-lead
       - ホットリード通知を送信
       - Request Body: { 
           lead_id, 
           channel_id,
           mention_user_id: "optional"
         }
       - Response: { notification_id, sent_at }

POST   /api/v1/integrations/teams/notify-bulk
       - 複数リードをまとめて通知（日次サマリー）
       - Request Body: { lead_ids[], channel_id }
```

### Bot対話

```
POST   /api/v1/integrations/teams/bot/webhook
       - Teams Botからのwebhook受信
       - Bot Framework SDKが自動的にルーティング

GET    /api/v1/integrations/teams/bot/sessions/{user_id}
       - ユーザーの診断セッション状態を取得
```

## Database Schema

```sql
-- Teams連携設定
CREATE TABLE teams_integrations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    team_id VARCHAR(255) NOT NULL,
    team_name VARCHAR(255) NOT NULL,
    channel_id VARCHAR(255),
    channel_name VARCHAR(255),
    
    -- Microsoft Graph API認証
    client_id VARCHAR(255) NOT NULL,
    client_secret_encrypted TEXT NOT NULL,
    tenant_id_ms VARCHAR(255) NOT NULL,  -- Microsoft Tenant ID
    
    -- Bot設定
    bot_app_id VARCHAR(255),
    bot_app_password_encrypted TEXT,
    
    -- 通知設定
    notify_hot_leads BOOLEAN DEFAULT TRUE,
    hot_lead_threshold INTEGER DEFAULT 80,
    notify_channel_id VARCHAR(255),  -- 通知先チャネル
    mention_user_ids TEXT[],  -- メンション対象ユーザー
    
    status VARCHAR(50) DEFAULT 'active',
    last_sync_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(tenant_id, team_id, channel_id)
);

-- Bot診断セッション
CREATE TABLE teams_bot_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    integration_id UUID REFERENCES teams_integrations(id) ON DELETE CASCADE,
    assessment_id UUID REFERENCES assessments(id) ON DELETE CASCADE,
    
    user_id VARCHAR(255) NOT NULL,  -- Teams User ID
    conversation_id VARCHAR(255) NOT NULL,
    
    current_question_index INTEGER DEFAULT 0,
    responses JSONB DEFAULT '[]',
    
    status VARCHAR(50) DEFAULT 'active',  -- active, completed, abandoned
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    
    UNIQUE(conversation_id, assessment_id)
);

CREATE INDEX idx_teams_integrations_tenant ON teams_integrations(tenant_id);
CREATE INDEX idx_teams_bot_sessions_conversation ON teams_bot_sessions(conversation_id);
```

## Events

```javascript
// Webhook通知用イベント
teams.integration.installed
teams.integration.removed
teams.assessment.shared
teams.lead.notified
teams.bot.session_started
teams.bot.session_completed
```

## Configuration

### 環境変数

```bash
# Microsoft Teams / Azure AD
MICROSOFT_CLIENT_ID=your-client-id
MICROSOFT_CLIENT_SECRET=your-client-secret
MICROSOFT_TENANT_ID=your-tenant-id

# Bot Framework
BOT_APP_ID=your-bot-app-id
BOT_APP_PASSWORD=your-bot-password

# Teams App設定
TEAMS_APP_ID=your-teams-app-id
TEAMS_APP_MANIFEST_URL=https://diagno-leads.com/teams-manifest.json
```

### Azure AD App登録

1. Azure Portalで新しいApp登録を作成
2. 必要な権限:
   - `Channel.ReadBasic.All`
   - `ChannelMessage.Send`
   - `Team.ReadBasic.All`
   - `User.Read.All`
3. Redirect URI: `https://api.diagnoleads.com/auth/microsoft/callback`

## Security Considerations

- **認証情報の暗号化**: Client SecretとBot Passwordは必ず暗号化して保存
- **テナント分離**: Teams連携は必ずテナントIDでフィルタリング
- **レート制限**: Microsoft Graph APIのレート制限を遵守（1分あたり600リクエスト）
- **Bot検証**: Botからのリクエストは必ず署名検証
- **OAuth 2.0**: 管理者同意フローを実装

## Testing Strategy

### 単体テスト
- Adaptive Card生成ロジック
- Bot応答ロジック
- 通知トリガー条件

### 統合テスト
- Microsoft Graph API呼び出し（モック使用）
- Bot Framework Adapter
- Webhook受信処理

### E2Eテスト
- テスト用Teamsテナントで実際に連携
- 診断投稿 → 回答 → 通知の全フロー
- Bot対話フロー

## Performance Requirements

- **通知遅延**: ホットリード獲得から5秒以内にTeams通知
- **Bot応答**: ユーザーメッセージから3秒以内に返答
- **カード表示**: Adaptive Card読み込み1秒以内

## Rollout Plan

### Week 1-2: 基礎実装
- Azure AD App登録
- Microsoft Graph API統合
- Adaptive Card生成

### Week 3-4: 通知機能
- ホットリード通知
- 診断共有機能
- カレンダー連携

### Week 5-6: Bot実装
- Bot Framework統合
- 対話型診断
- セッション管理

### Week 7: テスト & ドキュメント
- E2Eテスト
- ユーザードキュメント作成
- デモ動画作成

## Success Metrics

- **利用率**: 3ヶ月以内に50%のエンタープライズテナントがTeams連携を有効化
- **通知到達率**: 99%以上
- **Bot完了率**: 70%以上（従来のWeb版と同等以上）
- **リード対応時間**: 平均5分以内（従来の2時間から改善）

## Related Specifications

- [Integrations Overview](./integrations.md)
- [Lead Management](./lead-management.md)
- [Multi-Channel Distribution](./multi-channel-distribution.md)

## References

- [Microsoft Graph API Documentation](https://learn.microsoft.com/graph/)
- [Adaptive Cards Designer](https://adaptivecards.io/designer/)
- [Bot Framework SDK](https://dev.botframework.com/)
- [Teams App Development](https://learn.microsoft.com/microsoftteams/platform/)
