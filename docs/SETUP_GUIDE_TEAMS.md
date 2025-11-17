# Microsoft Teams 統合セットアップガイド

**対象**: DiagnoLeads Phase 1 - Teams統合機能
**想定時間**: 60-90分
**難易度**: 中級

このガイドでは、DiagnoLeadsとMicrosoft Teamsを統合するための手順を説明します。

---

## 📋 前提条件

### 必要なアカウント・権限
- **Microsoft 365アカウント** (管理者権限)
- **Azure サブスクリプション** (無料アカウント可)
- **DiagnoLeads テナント管理者アカウント**

### 技術要件
- Node.js 18+ または Python 3.11+ (Bot開発用)
- ngrok または Azure Tunnel (ローカル開発時)
- Git

---

## 🚀 Step 1: Azure ADアプリケーション登録

### 1.1 Azure Portalにサインイン

1. [Azure Portal](https://portal.azure.com) にアクセス
2. Microsoft 365アカウントでサインイン

### 1.2 アプリケーション登録

1. **Azure Active Directory** > **App registrations** を開く
2. **New registration** をクリック
3. 以下の情報を入力：
   - **Name**: `DiagnoLeads Teams Integration`
   - **Supported account types**: `Accounts in any organizational directory (Any Azure AD directory - Multitenant)`
   - **Redirect URI**:
     - Platform: `Web`
     - URI: `https://your-domain.com/api/v1/integrations/teams/oauth/callback`
4. **Register** をクリック

### 1.3 クライアントシークレット作成

1. 作成したアプリの **Certificates & secrets** を開く
2. **New client secret** をクリック
3. Description: `DiagnoLeads Teams Secret`
4. Expires: `24 months` (推奨)
5. **Add** をクリック
6. **Value（シークレット値）を必ずコピー** - 二度と表示されません！

### 1.4 API権限の追加

1. **API permissions** を開く
2. **Add a permission** をクリック
3. 以下の権限を追加：

**Microsoft Graph**:
- `User.Read` (Delegated)
- `Team.ReadBasic.All` (Delegated)
- `Channel.ReadBasic.All` (Delegated)
- `ChannelMessage.Send` (Application) ⭐ 重要

**注意**: Application権限は管理者の承認が必要です。

4. **Grant admin consent for [Your Organization]** をクリック

### 1.5 必要な情報をメモ

以下の情報を `.env` ファイルに保存します：

```bash
# Azure AD
AZURE_AD_CLIENT_ID=<Application (client) ID>
AZURE_AD_CLIENT_SECRET=<Client Secret Value>
AZURE_AD_TENANT_ID=<Directory (tenant) ID>
```

---

## 🤖 Step 2: Teams Bot作成

### 2.1 Azure Bot Serviceの作成

1. Azure Portalで **Create a resource** を開く
2. 「Bot」で検索し、**Azure Bot** を選択
3. **Create** をクリック
4. 以下の情報を入力：
   - **Bot handle**: `diagnoleads-bot` (一意の名前)
   - **Subscription**: 使用するサブスクリプション
   - **Resource group**: 新規作成 or 既存選択
   - **Pricing tier**: `F0 (Free)` (開発時)
   - **Microsoft App ID**: `Use existing app registration`
   - **App ID**: Step 1で作成した Application ID を入力
5. **Review + create** > **Create**

### 2.2 Messaging Endpointの設定

1. 作成したBotの **Configuration** を開く
2. **Messaging endpoint** に以下を入力：
   ```
   https://your-domain.com/api/v1/integrations/teams/bot/messages
   ```

   **ローカル開発時**:
   ```bash
   # ngrokを起動
   ngrok http 8000

   # 表示されたURLを使用
   https://abc123.ngrok.io/api/v1/integrations/teams/bot/messages
   ```

3. **Apply** をクリック

### 2.3 Teams Channelの有効化

1. Botの **Channels** を開く
2. **Microsoft Teams** アイコンをクリック
3. 利用規約に同意して **Agree**
4. **Save** をクリック

---

## 📦 Step 3: Teams App Manifest作成

### 3.1 Manifestファイルの準備

`teams-app/manifest.json` を作成：

```json
{
  "$schema": "https://developer.microsoft.com/en-us/json-schemas/teams/v1.16/MicrosoftTeams.schema.json",
  "manifestVersion": "1.16",
  "version": "1.0.0",
  "id": "<YOUR_AZURE_AD_CLIENT_ID>",
  "packageName": "com.diagnoleads.teamsapp",
  "developer": {
    "name": "DiagnoLeads",
    "websiteUrl": "https://diagnoleads.com",
    "privacyUrl": "https://diagnoleads.com/privacy",
    "termsOfUseUrl": "https://diagnoleads.com/terms"
  },
  "name": {
    "short": "DiagnoLeads",
    "full": "DiagnoLeads - B2B Assessment Platform"
  },
  "description": {
    "short": "Create and distribute assessments to capture quality leads",
    "full": "DiagnoLeads helps B2B companies create diagnostic assessments to identify customer needs and capture high-quality leads. Receive real-time notifications when hot leads are captured."
  },
  "icons": {
    "color": "color-icon.png",
    "outline": "outline-icon.png"
  },
  "accentColor": "#4F46E5",
  "bots": [
    {
      "botId": "<YOUR_AZURE_AD_CLIENT_ID>",
      "scopes": ["team", "personal", "groupchat"],
      "supportsFiles": false,
      "isNotificationOnly": false,
      "commandLists": [
        {
          "scopes": ["team", "personal", "groupchat"],
          "commands": [
            {
              "title": "help",
              "description": "Show help information"
            },
            {
              "title": "list assessments",
              "description": "List available assessments"
            },
            {
              "title": "start [assessment-id]",
              "description": "Start an assessment"
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
    "your-domain.com"
  ],
  "webApplicationInfo": {
    "id": "<YOUR_AZURE_AD_CLIENT_ID>",
    "resource": "api://botid-<YOUR_AZURE_AD_CLIENT_ID>"
  }
}
```

### 3.2 アイコン画像の準備

- **color-icon.png**: 192x192px (カラー)
- **outline-icon.png**: 32x32px (透過PNG、白色アウトライン)

### 3.3 ZIPファイルの作成

```bash
cd teams-app
zip -r DiagnoLeads.zip manifest.json color-icon.png outline-icon.png
```

---

## 🔧 Step 4: DiagnoLeadsバックエンド設定

### 4.1 環境変数の設定

`.env` ファイルに以下を追加：

```bash
# Teams Integration
TEAMS_ENABLED=true
TEAMS_APP_ID=<YOUR_AZURE_AD_CLIENT_ID>
TEAMS_APP_PASSWORD=<YOUR_AZURE_AD_CLIENT_SECRET>
TEAMS_BOT_ENDPOINT=https://your-domain.com/api/v1/integrations/teams/bot/messages

# Bot Framework
BOT_FRAMEWORK_APP_ID=<YOUR_AZURE_AD_CLIENT_ID>
BOT_FRAMEWORK_APP_PASSWORD=<YOUR_AZURE_AD_CLIENT_SECRET>
```

### 4.2 依存パッケージのインストール

**Python (FastAPI)**:
```bash
cd backend
pip install botbuilder-core botbuilder-schema aiohttp
```

**Node.js (オプション)**:
```bash
npm install botbuilder botframework-connector
```

### 4.3 Botエンドポイントの実装

実装例は `backend/app/integrations/teams/` を参照してください。

---

## 📲 Step 5: Teams Appのインストール

### 5.1 サイドローディング（開発・テスト用）

1. Microsoft Teams を開く
2. 左サイドバーの **Apps** をクリック
3. 左下の **Upload a custom app** をクリック
4. Step 3で作成した `DiagnoLeads.zip` を選択
5. **Add** をクリック

### 5.2 チームへの追加

1. 追加したいチームを選択
2. チーム名の横の **…** > **Manage team** をクリック
3. **Apps** タブを開く
4. DiagnoLeads を検索して **Add** をクリック

### 5.3 動作確認

1. Teamsのチャットで `@DiagnoLeads help` と入力
2. Botから応答があれば成功！

---

## 🧪 Step 6: Webhook通知のテスト

### 6.1 Incoming Webhookの設定

1. Teamsでチャネルを開く
2. チャネル名の横の **…** > **Connectors** をクリック
3. **Incoming Webhook** を検索して **Configure**
4. 名前: `DiagnoLeads Notifications`
5. **Create** をクリック
6. **Webhook URL をコピー**

### 6.2 DiagnoLeads管理画面で設定

1. DiagnoLeads管理画面にログイン
2. **設定** > **外部連携** > **Microsoft Teams**
3. Webhook URLを貼り付け
4. **保存**

### 6.3 テスト通知の送信

```bash
curl -X POST https://your-domain.com/api/v1/integrations/teams/test-notification \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json"
```

Teamsチャネルに通知が届けば成功！

---

## 🎨 Step 7: Adaptive Cards設定

Adaptive Cardsのテンプレートは `backend/app/integrations/teams/cards/` にあります。

### サンプル: リード通知カード

```json
{
  "type": "AdaptiveCard",
  "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
  "version": "1.5",
  "body": [
    {
      "type": "TextBlock",
      "text": "🔥 New Hot Lead Captured!",
      "weight": "Bolder",
      "size": "Large",
      "color": "Attention"
    },
    {
      "type": "FactSet",
      "facts": [
        {
          "title": "Company:",
          "value": "${company_name}"
        },
        {
          "title": "Contact:",
          "value": "${contact_name}"
        },
        {
          "title": "Email:",
          "value": "${email}"
        },
        {
          "title": "Score:",
          "value": "${lead_score}/100"
        }
      ]
    }
  ],
  "actions": [
    {
      "type": "Action.OpenUrl",
      "title": "View in DiagnoLeads",
      "url": "${lead_url}"
    }
  ]
}
```

---

## ⚠️ トラブルシューティング

### Bot が応答しない

**原因**: Messaging Endpoint が正しく設定されていない

**解決方法**:
1. Azure Bot の Configuration で Messaging endpoint を確認
2. ngrokを使っている場合、ngrokが起動しているか確認
3. バックエンドサーバーが起動しているか確認
4. ログでエラーを確認: `tail -f backend/logs/teams.log`

### 通知が届かない

**原因**: Webhook URL が間違っている、または権限不足

**解決方法**:
1. Webhook URLを再度コピー＆ペースト
2. Teamsで Incoming Webhook が有効か確認
3. テスト送信を実行: `curl -X POST <WEBHOOK_URL> -H "Content-Type: application/json" -d '{"text": "Test"}'`

### 権限エラー

**原因**: Azure ADで管理者承認がされていない

**解決方法**:
1. Azure Portal > App registrations > API permissions を開く
2. 「Grant admin consent」をクリック
3. 承認されるまで数分待つ

---

## 📚 参考リンク

- [Microsoft Teams 開発者ドキュメント](https://docs.microsoft.com/en-us/microsoftteams/platform/)
- [Bot Framework SDK](https://docs.microsoft.com/en-us/azure/bot-service/)
- [Adaptive Cards Designer](https://adaptivecards.io/designer/)
- [Teams App Manifest スキーマ](https://docs.microsoft.com/en-us/microsoftteams/platform/resources/schema/manifest-schema)

---

## 🎯 次のステップ

Teams統合が完了したら、以下の機能を追加できます：

1. **会議内診断**: Teams会議中に診断を共有
2. **SharePoint統合**: 診断結果を自動保存
3. **タスク自動作成**: Planner/To Doに自動でタスク追加

詳細: [IMPLEMENTATION_PLAN_PHASE1.md](./IMPLEMENTATION_PLAN_PHASE1.md)

---

**Built with ❤️ using OpenSpec Spec-Driven Development**
