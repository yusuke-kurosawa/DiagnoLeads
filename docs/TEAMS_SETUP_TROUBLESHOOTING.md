# Microsoft Teams Integration - Troubleshooting Guide

## 現在の状況

### ✅ 完了した設定
1. Azure AD App Registration完了
   - Client ID: `08ac2808-5c23-4f76-a5c1-69b6317d0f68`
   - Tenant ID: `afa5f8a9-ec65-4590-a8b5-f375824a68e7`
   - Client Secret設定済み

2. Azure Bot登録完了
   - Bot App ID: `7aeaa6d8-fe25-4b61-91fc-4b4fa522b14b`
   - Bot App Password設定済み

3. 環境変数設定完了
   - backend/.env に認証情報設定済み

4. 認証テスト成功
   - Azure ADでのトークン取得成功 ✅

### ❌ 発生しているエラー

```
Error: 403 Forbidden
Message: "Authorization_RequestDenied - Insufficient privileges to complete the operation."
```

**原因**: Azure AD Appに必要なAPI権限が設定されていないか、管理者同意が未実施

---

## 解決手順

### Step 1: Azure Portalでのワリ限設定

1. [Azure Portal](https://portal.azure.com/) にアクセス
2. **Azure Active Directory** → **App registrations** を開く
3. **DiagnoLeads Teams Integration localhost** アプリを選択
4. 左メニューから **API permissions** を選択

### Step 2: 必要な権限を追加

**Microsoft Graph** の **Application permissions** として以下を追加:

| 権限名 | 説明 | 必須 |
|---|---|---|
| `Group.Read.All` | すべてのグループ情報の読み取り | ✅ |
| `Team.ReadBasic.All` | すべてのチーム情報の読み取り | ✅ |
| `Channel.ReadBasic.All` | すべてのチャネル情報の読み取り | ✅ |
| `ChannelMessage.Send` | チャネルへのメッセージ送信 | ⚠️ (メッセージ送信時) |
| `User.Read.All` | ユーザー情報の読み取り (メンション用) | ⚠️ (メンション時) |

**⚠️ 重要**: 必ず **Application permissions** を選択してください（Delegated permissionsではありません）

#### 追加手順:
1. **Add a permission** をクリック
2. **Microsoft Graph** を選択
3. **Application permissions** を選択
4. 上記の権限を検索して追加
5. **Add permissions** をクリック

### Step 3: 管理者同意を付与

**これが最も重要なステップです！**

1. API permissions画面で **Grant admin consent for {Your Organization}** をクリック
2. 確認ダイアログで **Yes** をクリック
3. すべての権限の **Status** 列に緑のチェックマーク ✅ が表示されることを確認

**⚠️ 注意**: このステップには **Azure AD管理者権限** が必要です

### Step 4: 権限が正しく設定されたか確認

API permissions画面で以下を確認:
- すべての権限に **Admin consent granted** と表示されている
- Status列にすべて緑のチェックマーク ✅ がある

---

## 再テスト手順

権限設定完了後、以下のコマンドでテストを再実行:

```bash
cd /home/kurosawa/DiagnoLeads/backend
./venv/bin/python app/integrations/microsoft/teams_client.py
```

### 期待される成功結果:

```
============================================================
Microsoft Teams Integration - Live Test
============================================================

1. Authentication Test
✅ Authentication successful for tenant: afa5f8a9-ec65-4590-a8b5-f375824a68e7
✅ Authentication successful

2. Get Teams Test
✅ Found X teams
  1. チーム名A (ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)
  2. チーム名B (ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)

3. Get Channels Test (Team: チーム名A)
✅ Found Y channels
  1. General (ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)
  2. Channel Name (ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)

4. Hot Lead Notification Test (Dry Run)
Sample notification data:
  Company: 株式会社サンプル
  Contact: 山田太郎 (営業部長)
  Score: 92/100

⚠️  Note: Actual message sending is not implemented in this test.
    To send messages, you need 'ChannelMessage.Send' permission.

============================================================
Prototype Test Completed Successfully! 🎉
============================================================
```

---

## よくあるエラーと解決策

### Error: 403 Forbidden (現在のエラー)
**原因**: API権限が設定されていない、または管理者同意が未実施
**解決**: 上記のStep 1-3を実行

### Error: 401 Unauthorized
**原因**: Client IDまたはClient Secretが正しくない
**解決**: 
1. backend/.envファイルの認証情報を確認
2. Azure Portalで新しいClient Secretを生成して再設定

### Error: 400 Bad Request (no body)
**原因1**: API権限の設定ミス（Delegated permissionsを選択している）
**解決**: **Application permissions** を選択し直す

**原因2**: テナントIDが正しくない
**解決**: Azure PortalでDirectory (tenant) IDを確認

### Error: Invalid redirect URI
**原因**: Redirect URIがAzure AD Appに登録されていない
**解決**: 
1. Azure Portal → App registrations → Authentication
2. Redirect URIsに `http://localhost:8000/auth/microsoft/callback` を追加

---

## セキュリティ上の注意

### Client Secretの管理
- ✅ `.env`ファイルは`.gitignore`に追加済み
- ⚠️ Client Secretは絶対にGitにコミットしない
- ⚠️ 本番環境ではAzure Key VaultまたはAWS Secrets Managerを使用

### 最小権限の原則
- 現在のテストに必要な最小限の権限のみ設定
- `ChannelMessage.Send`は実際に送信機能を実装する時のみ追加
- 定期的に権限を見直し、不要な権限は削除

---

## 次のステップ

### 1. 権限設定完了後 (現在)
- [ ] Azure AD Appに必要な権限を追加
- [ ] 管理者同意を付与
- [ ] テストスクリプトを再実行
- [ ] チーム・チャネル一覧取得が成功することを確認

### 2. メッセージ送信機能の実装
- [ ] `ChannelMessage.Send`権限を追加
- [ ] `send_adaptive_card()`メソッドを実装
- [ ] Adaptive Cardのテスト送信

### 3. Bot Framework統合
- [ ] Bot Messaging Endpointの実装
- [ ] Webhook署名検証
- [ ] Bot対話ロジックの実装

### 4. Teams App Manifest作成
- [ ] manifest.jsonファイル作成
- [ ] アイコン準備
- [ ] Teamsへのサイドローディング

---

## リファレンス

- [Microsoft Graph API - Teams](https://learn.microsoft.com/graph/api/resources/teams-api-overview)
- [Application vs Delegated Permissions](https://learn.microsoft.com/azure/active-directory/develop/v2-permissions-and-consent)
- [Admin Consent](https://learn.microsoft.com/azure/active-directory/manage-apps/grant-admin-consent)

---

**Document Version**: 1.0  
**Created**: 2025-11-11  
**Status**: 権限設定待ち (Action Required)
