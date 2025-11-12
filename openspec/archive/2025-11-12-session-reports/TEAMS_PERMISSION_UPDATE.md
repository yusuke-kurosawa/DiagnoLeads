# Microsoft Teams メッセージ送信権限 - 重要な更新

## 🔍 新しい発見

テスト実行の結果、チャネルへのメッセージ送信には `ChannelMessage.Send` ではなく、別の権限が必要であることが判明しました。

### エラーメッセージ:
```
Missing role permissions on the request. 
API requires one of 'Teamwork.Migrate.All'.
```

---

## ✅ 正しい権限設定

### 必要な権限

| 権限名 | 用途 | 優先度 |
|---|---|---|
| `Group.Read.All` | チーム情報の取得 | ✅ 設定済み |
| `Team.ReadBasic.All` | チーム詳細の取得 | ✅ 設定済み |
| `Channel.ReadBasic.All` | チャネル情報の取得 | ✅ 設定済み |
| `User.Read.All` | ユーザー情報の取得 | ✅ 設定済み |
| `ChannelMessage.Read.All` | メッセージ読み取り | ✅ 設定済み |
| **`Teamwork.Migrate.All`** | **チャネルへのメッセージ送信** | ⚠️ **追加が必要** |

### 代替オプション

Microsoft Graph APIでチャネルにメッセージを送信するには、いくつかのアプローチがあります：

#### オプション1: Teamwork.Migrate.All（現在推奨）
- **用途**: メッセージの作成・送信
- **制限**: 移行シナリオ用の権限だが、通常のメッセージ送信にも使用可能
- **セキュリティレベル**: 高（管理者権限必須）

#### オプション2: Bot Framework経由
- **用途**: Botとしてメッセージを送信
- **制限**: Bot Frameworkの設定が必要
- **メリット**: よりTeamsネイティブな統合

#### オプション3: Incoming Webhooks
- **用途**: Webhookを使用したメッセージ送信
- **制限**: チャネルごとにWebhookの設定が必要
- **メリット**: 権限管理が不要、シンプル

---

## 📋 推奨アプローチ: Incoming Webhooks

現在の要件（ホットリード通知）には、**Incoming Webhooks**が最も適しています。

### メリット
- ✅ Azure AD権限が不要
- ✅ シンプルな実装
- ✅ セキュリティリスクが低い
- ✅ チャネルごとに個別設定可能
- ✅ 管理者の承認が不要

### デメリット
- ❌ チャネルごとにWebhook URLの設定が必要
- ❌ 双方向通信（返信の受信）ができない
- ❌ @メンションが制限される

---

## 🔧 実装方法

### A. Incoming Webhooks アプローチ（推奨）

#### 1. TeamsでWebhook URLを取得

1. Microsoft Teams でチャネルを開く
2. チャネル名の横の **...** をクリック
3. **コネクタ** を選択
4. **Incoming Webhook** を検索して **構成** をクリック
5. 名前を入力: `DiagnoLeads`
6. （オプション）画像をアップロード
7. **作成** をクリック
8. **Webhook URL をコピー** して保存

#### 2. 実装例

```python
import httpx

class TeamsWebhookClient:
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
    
    async def send_adaptive_card(self, card: dict):
        """Webhook経由でAdaptive Cardを送信"""
        message = {
            "type": "message",
            "attachments": [{
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": card
            }]
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(self.webhook_url, json=message)
            response.raise_for_status()
            return {"status": "sent"}

# 使用例
webhook_client = TeamsWebhookClient(
    webhook_url="https://your-tenant.webhook.office.com/webhookb2/..."
)

await webhook_client.send_adaptive_card(card)
```

#### 3. 環境変数設定

```bash
# backend/.env に追加
TEAMS_WEBHOOK_URL=https://your-tenant.webhook.office.com/webhookb2/...
```

### B. Teamwork.Migrate.All アプローチ（代替）

現在のGraph API実装を維持する場合:

#### Azure Portal での設定

1. [Azure Portal](https://portal.azure.com) にアクセス
2. **Azure Active Directory** → **App registrations**
3. **DiagnoLeads Teams Integration localhost** を選択
4. **API permissions** → **Add a permission**
5. **Microsoft Graph** → **Application permissions**
6. `Teamwork.Migrate.All` を検索して追加
7. **Grant admin consent for [Your Organization]** をクリック
8. 5-10分待機

⚠️ **注意**: この権限は非常に強力で、すべてのチームのメッセージを操作できます。

---

## 🎯 推奨実装プラン

### Phase 1: Incoming Webhooks（即座に実装可能）

1. ✅ TeamsWebhookClientクラスを作成
2. ✅ Webhook URL設定をテナントモデルに追加
3. ✅ Adaptive Card送信機能を実装
4. ✅ テスト実施

**メリット**: 管理者権限不要、即座に使用開始可能

### Phase 2: Bot Framework（将来の拡張）

1. Azure Bot Service登録
2. Bot Framework SDK統合
3. 双方向通信機能
4. @メンション機能

**メリット**: よりリッチな機能、Teams App Storeへの公開可能

---

## 🚀 次のステップ

### 推奨: Incoming Webhooks実装

1. **Webhook Client実装**
   ```bash
   backend/app/integrations/microsoft/teams_webhook_client.py
   ```

2. **テストスクリプト作成**
   ```bash
   backend/test_teams_webhook.py
   ```

3. **ドキュメント更新**
   ```bash
   docs/TEAMS_WEBHOOK_GUIDE.md
   ```

### 代替: Teamwork.Migrate.All権限追加

Azure Portal で権限を追加し、`check_message_permission.py`を再実行

---

## 📊 アプローチ比較

| 項目 | Incoming Webhook | Graph API + Teamwork.Migrate.All | Bot Framework |
|---|---|---|---|
| 実装難易度 | ⭐ 簡単 | ⭐⭐ 中 | ⭐⭐⭐ 難 |
| 権限管理 | 不要 | 管理者権限必須 | 管理者権限必須 |
| 即座に使用可能 | ✅ Yes | ❌ No（承認待ち） | ❌ No（設定多い） |
| セキュリティ | ✅ 高い | ⚠️ 中（広範な権限） | ✅ 高い |
| 双方向通信 | ❌ No | ❌ No | ✅ Yes |
| @メンション | ❌ 制限あり | ❌ 制限あり | ✅ Full |
| Teams App Store公開 | ❌ No | ❌ No | ✅ Yes |
| **推奨度** | **⭐⭐⭐** | ⭐ | ⭐⭐（将来用） |

---

## ✅ 結論

**現在の要件（ホットリード通知）には Incoming Webhooks が最適です。**

理由:
- 即座に実装・使用可能
- 管理者の承認不要
- セキュリティリスクが低い
- 実装がシンプル

次のアクションとして、**Incoming Webhooks の実装**を推奨します。

---

**Document Version**: 1.0  
**Created**: 2025-11-11  
**Status**: Critical Update - Action Required
