# Microsoft Teams Integration Setup Guide

このガイドでは、DiagnoLeadsとMicrosoft Teamsを連携するための技術的な準備手順を説明します。

---

## Prerequisites

- **Microsoft 365アカウント**: 管理者権限があるアカウント
- **Azure Subscription**: 無料アカウント可 ([Azure Portal](https://portal.azure.com/))
- **開発環境**: Python 3.11+、Node.js 20+

---

## Part 1: Azure AD App Registration

### Step 1: Azure Portalにログイン

1. [Azure Portal](https://portal.azure.com/) にアクセス
2. Microsoft 365管理者アカウントでログイン

### Step 2: App Registrationを作成

1. **Azure Active Directory** → **App registrations** → **New registration**
2. 以下を入力:
   - **Name**: `DiagnoLeads Teams Integration`
   - **Supported account types**: `Accounts in this organizational directory only`
   - **Redirect URI**: 
     - Type: `Web`
     - URI: `https://api.diagnoleads.com/auth/microsoft/callback`
     - ローカル開発用: `http://localhost:8000/auth/microsoft/callback`

3. **Register** をクリック

### Step 3: Client Secretを生成

1. 作成したAppの詳細画面で **Certificates & secrets** を選択
2. **New client secret** をクリック
3. Description: `DiagnoLeads Production`
4. Expires: `24 months` (推奨)
5. **Add** をクリック
6. **Value** をコピーして安全な場所に保存 ⚠️ この値は二度と表示されません

### Step 4: 必要な権限を追加

1. **API permissions** を選択
2. **Add a permission** → **Microsoft Graph** → **Application permissions**
3. 以下の権限を追加:
   - `Channel.ReadBasic.All` - チャネル情報の読み取り
   - `ChannelMessage.Send` - チャネルへのメッセージ送信
   - `Team.ReadBasic.All` - チーム情報の読み取り
   - `User.Read.All` - ユーザー情報の読み取り (メンション用)

4. **Grant admin consent for {Your Organization}** をクリック
   - ⚠️ これには管理者権限が必要です

### Step 5: 認証情報をメモ

以下の情報をコピー:
- **Application (client) ID**: Overview画面に表示
- **Directory (tenant) ID**: Overview画面に表示
- **Client Secret**: Step 3で保存した値

---

## Part 2: Bot Framework App Registration

Microsoft Teams BotにはBot Frameworkの登録が必要です。

### Step 1: Azure Bot Service作成

1. Azure Portal → **Create a resource**
2. "Bot" で検索 → **Azure Bot** を選択
3. **Create** をクリック
4. 以下を入力:
   - **Bot handle**: `diagno-leads-bot` (ユニークな名前)
   - **Subscription**: あなたのサブスクリプション
   - **Resource group**: 新規作成または既存を選択
   - **Pricing tier**: `Free (F0)` (開発用)
   - **Microsoft App ID**: `Create new Microsoft App ID`

5. **Review + create** → **Create**

### Step 2: Bot App ID & Passwordを取得

1. 作成したBotの **Configuration** を開く
2. **Microsoft App ID** をコピー
3. **Manage** リンクをクリック
4. **Certificates & secrets** → **New client secret**
5. Secret valueをコピー (Bot App Password)

### Step 3: Messaging Endpointを設定

1. Bot Configurationに戻る
2. **Messaging endpoint** に以下を設定:
   ```
   https://api.diagnoleads.com/api/v1/integrations/teams/bot/webhook
   ```
   - ローカル開発用: `https://your-ngrok-url.ngrok.io/api/v1/integrations/teams/bot/webhook`

3. **Apply** をクリック

### Step 4: Teams Channelを有効化

1. Bot リソースの **Channels** を選択
2. **Microsoft Teams** アイコンをクリック
3. Terms of Service に同意
4. **Apply** をクリック

---

## Part 3: 環境変数設定

### Backend (.env)

```bash
# Microsoft Teams Integration
MICROSOFT_CLIENT_ID=<Application (client) ID>
MICROSOFT_CLIENT_SECRET=<Client Secret Value>
MICROSOFT_TENANT_ID=<Directory (tenant) ID>

# Bot Framework
BOT_APP_ID=<Bot Microsoft App ID>
BOT_APP_PASSWORD=<Bot App Password>

# Teams App
TEAMS_APP_ID=<後で設定>
TEAMS_APP_MANIFEST_URL=https://api.diagnoleads.com/teams-manifest.json
```

### 環境変数の安全な管理

**Production**:
- AWS Secrets Manager / Azure Key Vault 使用を推奨
- 環境変数は暗号化して保存

**Development**:
- `.env.local` に保存 (`.gitignore` に追加済み)
- チーム内での共有は1Passwordなど使用

---

## Part 4: ローカル開発環境セットアップ

### ngrokのインストール (Webhook受信用)

Teams Botはインターネット経由でWebhookを送信するため、ローカル開発にはngrokが必要です。

```bash
# macOS (Homebrew)
brew install ngrok

# Windows (Chocolatey)
choco install ngrok

# Linux (Snap)
snap install ngrok

# ngrok認証
ngrok authtoken YOUR_AUTHTOKEN  # ngrok.com で取得
```

### バックエンド起動

```bash
cd backend

# 依存関係インストール
pip install msal msgraph-sdk botbuilder-core botbuilder-schema

# 開発サーバー起動
uvicorn app.main:app --reload --port 8000
```

### ngrok起動

```bash
# 別のターミナルで
ngrok http 8000
```

ngrokが表示するHTTPS URL (例: `https://abc123.ngrok.io`) をBot Messaging Endpointに設定。

---

## Part 5: Teams App Manifestの作成

Teams AppとしてパッケージングするにはManifestファイルが必要です。

### manifest.json

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/teams/v1.16/MicrosoftTeams.schema.json",
  "manifestVersion": "1.16",
  "version": "1.0.0",
  "id": "{{BOT_APP_ID}}",
  "packageName": "com.diagnoleads.teamsapp",
  "developer": {
    "name": "DiagnoLeads",
    "websiteUrl": "https://diagnoleads.com",
    "privacyUrl": "https://diagnoleads.com/privacy",
    "termsOfUseUrl": "https://diagnoleads.com/terms"
  },
  "icons": {
    "color": "color.png",
    "outline": "outline.png"
  },
  "name": {
    "short": "DiagnoLeads",
    "full": "DiagnoLeads Assessment Platform"
  },
  "description": {
    "short": "B2B診断サービスプラットフォーム",
    "full": "DiagnoLeadsは、B2B企業向けの診断サービスプラットフォームです。Teams内で診断を配信・実施し、リアルタイムでホットリードを検出します。"
  },
  "accentColor": "#FFFFFF",
  "bots": [
    {
      "botId": "{{BOT_APP_ID}}",
      "scopes": [
        "personal",
        "team"
      ],
      "commandLists": [
        {
          "scopes": [
            "personal",
            "team"
          ],
          "commands": [
            {
              "title": "診断を開始",
              "description": "利用可能な診断を表示します"
            },
            {
              "title": "ヘルプ",
              "description": "使い方を表示します"
            }
          ]
        }
      ]
    }
  ],
  "permissions": [
    "identity",
    "messageTeamMembers"
  ],
  "validDomains": [
    "diagnoleads.com",
    "*.diagnoleads.com"
  ]
}
```

### アイコン準備

- **color.png**: 192x192px、フルカラー
- **outline.png**: 32x32px、白い輪郭のみ (透過背景)

### Appパッケージ作成

```bash
# manifest.json, color.png, outline.pngを含むZIPを作成
zip diagno-leads-teams-app.zip manifest.json color.png outline.png
```

---

## Part 6: Teams AppをTeamsにインストール

### サイドローディング (開発用)

1. Microsoft Teams を開く
2. 左サイドバー **Apps** → **Manage your apps** → **Upload an app**
3. **Upload a custom app** を選択
4. `diagno-leads-teams-app.zip` をアップロード
5. チーム/チャットに追加

⚠️ サイドローディングには管理者による許可が必要な場合があります:
- Teams Admin Center → **Teams apps** → **Setup policies** → Custom app uploading を有効化

### 本番環境への公開

1. [Partner Center](https://partner.microsoft.com/) でアカウント作成
2. Teams Appを提出
3. Microsoft審査 (通常2-4週間)
4. 承認後、Teams App Storeに掲載

---

## Part 7: テスト

### 1. Graph API接続テスト

```python
# test_teams_integration.py
import asyncio
from app.integrations.microsoft.teams_client import TeamsClient

async def test_connection():
    client = TeamsClient(
        tenant_id="YOUR_TENANT_ID",
        client_id="YOUR_CLIENT_ID",
        client_secret="YOUR_CLIENT_SECRET"
    )
    
    # チャネル一覧取得
    channels = await client.get_channels("YOUR_TEAM_ID")
    print(f"Found {len(channels)} channels")
    
    # テストメッセージ送信
    await client.send_message(
        team_id="YOUR_TEAM_ID",
        channel_id="YOUR_CHANNEL_ID",
        message="Hello from DiagnoLeads!"
    )

asyncio.run(test_connection())
```

### 2. Adaptive Card送信テスト

```python
async def test_adaptive_card():
    client = TeamsClient(...)
    
    card = {
        "type": "AdaptiveCard",
        "body": [
            {
                "type": "TextBlock",
                "text": "テスト通知",
                "weight": "bolder",
                "size": "large"
            }
        ],
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "version": "1.5"
    }
    
    await client.send_adaptive_card(
        team_id="YOUR_TEAM_ID",
        channel_id="YOUR_CHANNEL_ID",
        card=card
    )

asyncio.run(test_adaptive_card())
```

### 3. Bot対話テスト

1. Teams でBot にDM送信: `診断を開始`
2. Bot からの返信を確認
3. 診断選択 → 質問受信を確認

---

## Troubleshooting

### エラー: "Forbidden: Insufficient privileges"
→ Azure ADで管理者同意が必要。API permissions → Grant admin consent

### Bot がWebhookを受信しない
→ Messaging Endpointが正しいか確認。ngrokが起動しているか確認。

### Adaptive Cardが表示されない
→ JSONスキーマが正しいか [Adaptive Cards Designer](https://adaptivecards.io/designer/) で検証

### レート制限エラー
→ Microsoft Graph APIは1分あたり600リクエスト制限。Exponential backoff実装。

---

## Security Checklist

- [ ] Client SecretをGitにコミットしていない
- [ ] 本番環境の認証情報は暗号化されている
- [ ] Webhook署名検証を実装 (Bot Framework)
- [ ] Teams App Manifestに不要な権限がない
- [ ] Azure ADのRedirect URIが本番URLのみ (開発終了後)

---

## Next Steps

1. ✅ Azure AD & Bot Framework登録完了
2. → [Implementation Plan](./IMPLEMENTATION_PLAN_PHASE1.md) のWeek 2へ
3. → Microsoft Graph API統合実装開始

---

## References

- [Microsoft Teams Developer Docs](https://learn.microsoft.com/microsoftteams/platform/)
- [Microsoft Graph API](https://learn.microsoft.com/graph/)
- [Bot Framework SDK](https://dev.botframework.com/)
- [Adaptive Cards](https://adaptivecards.io/)

**Document Version**: 1.0  
**Last Updated**: 2025-11-10
