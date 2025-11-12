# Microsoft Teams Incoming Webhook セットアップガイド

## 📋 概要

このガイドでは、DiagnoLeadsからMicrosoft Teamsにメッセージを送信するためのIncoming Webhook URLを取得・設定する手順を説明します。

**所要時間**: 5分

---

## ⚠️ 重要な注意事項

### テスト用チャネルの使用を強く推奨

- ❌ **本番のビジネスチャネルは避けてください**
- ❌ 全社チャネル、営業チーム、役員チャネルなど
- ✅ **テスト専用のチャネルを作成してください**
- ✅ 'test', 'テスト', 'sandbox', 'dev' などの名前推奨

---

## 🎯 ステップ1: テスト用チャネルの作成（推奨）

### 1.1 Microsoft Teams を開く

デスクトップアプリまたはブラウザで Microsoft Teams にアクセス

### 1.2 適切なチームを選択

- 既存のチームを選択、または
- 新しいチームを作成（プライベート推奨）

### 1.3 テストチャネルを作成

1. チーム名の横の **...** をクリック
2. **チャネルを追加** を選択
3. 以下の情報を入力:
   - **チャネル名**: `DiagnoLeads Test` （推奨）
   - **説明**: `DiagnoLeads 通知テスト用チャネル`
   - **プライバシー**: `プライベート` （推奨）
4. **追加** をクリック
5. メンバーとして自分のみを追加

---

## 🔧 ステップ2: Incoming Webhook URL の取得

### 2.1 チャネルでコネクタを開く

1. 作成した **DiagnoLeads Test** チャネルを開く
2. チャネル名の横の **...（その他のオプション）** をクリック
3. **コネクタ** を選択

### 2.2 Incoming Webhook を構成

1. 検索ボックスで **Incoming Webhook** を検索
2. **Incoming Webhook** の **構成** ボタンをクリック

### 2.3 Webhook を設定

1. 以下の情報を入力:
   - **名前**: `DiagnoLeads`
   - **画像のアップロード**:（オプション）DiagnoLeadsのロゴ
2. **作成** をクリック

### 2.4 Webhook URL をコピー

1. 表示された **Webhook URL をコピー**
2. 安全な場所に保存（後で使用）

**URL の形式例:**
```
https://your-tenant.webhook.office.com/webhookb2/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx@xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx/IncomingWebhook/yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy/zzzzzzzz-zzzz-zzzz-zzzz-zzzzzzzzzzzz
```

⚠️ **重要**: この URL は秘密情報です。他者と共有しないでください。

---

## 💾 ステップ3: DiagnoLeads への設定

### 3.1 .env ファイルを編集

```bash
cd /home/kurosawa/DiagnoLeads/backend
```

`.env` ファイルを開き、以下の行を追加:

```bash
# Microsoft Teams Incoming Webhook
TEAMS_WEBHOOK_URL=<コピーしたWebhook URL>
```

**実際の例:**
```bash
TEAMS_WEBHOOK_URL=https://your-tenant.webhook.office.com/webhookb2/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx@xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx/IncomingWebhook/yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy/zzzzzzzz-zzzz-zzzz-zzzz-zzzzzzzzzzzz
```

### 3.2 保存して確認

```bash
# 設定が正しいか確認（URLの一部のみ表示）
grep "TEAMS_WEBHOOK_URL" .env | head -c 50
```

---

## 🧪 ステップ4: テスト実行

### 4.1 Webhook Client のテストを実行

```bash
cd /home/kurosawa/DiagnoLeads/backend
./venv/bin/python app/integrations/microsoft/teams_webhook_client.py
```

### 4.2 期待される出力

```
============================================================
Teams Webhook Client Test
============================================================

1. Testing simple message...
✅ Adaptive Card sent successfully via Webhook
✅ Simple message sent

2. Testing Adaptive Card...
✅ Adaptive Card sent successfully via Webhook
✅ Adaptive Card sent

============================================================
Test completed. Check your Teams channel!
============================================================
```

### 4.3 Teams で確認

1. **DiagnoLeads Test** チャネルを開く
2. 2つのテストメッセージが表示されていることを確認:
   - シンプルなテストメッセージ
   - ホットリード通知（Adaptive Card）

---

## 📊 テストメッセージの例

### メッセージ1: シンプルメッセージ

```
┌──────────────────────────────────────┐
│ DiagnoLeads                          │
│ テスト通知                            │
│                                      │
│ これはDiagnoLeadsからの              │
│ テストメッセージです。                │
└──────────────────────────────────────┘
```

### メッセージ2: Adaptive Card（ホットリード通知）

```
┌──────────────────────────────────────────────┐
│ DiagnoLeads                                  │
│                                              │
│ 🔥 ホットリード獲得！                        │
│    スコア: 98/100                            │
│                                              │
│ 会社名:   Webhook株式会社                    │
│ 担当者:   Webhook太郎 (Webhook部長)         │
│ メール:   webhook@example.com               │
│ 電話:     03-XXXX-XXXX                       │
│ 診断:     【Webhookテスト】診断              │
│                                              │
│ [リードを見る] ボタン                        │
└──────────────────────────────────────────────┘
```

---

## ✅ 成功の確認

以下がすべて完了していれば成功です：

- [ ] テスト用チャネル「DiagnoLeads Test」を作成
- [ ] Incoming Webhook URL を取得
- [ ] `.env` ファイルに URL を設定
- [ ] テストスクリプトを実行
- [ ] Teams チャネルに2つのメッセージが表示された

---

## 🔄 次のステップ

### DiagnoLeads アプリへの統合

リード獲得時の自動通知を実装:

```python
# backend/app/services/lead_service.py

from app.integrations.microsoft.teams_webhook_client import TeamsWebhookClient
import os

async def create_lead(lead_data: dict, tenant):
    # リード作成処理
    lead = await save_lead(lead_data)
    
    # ホットリードの場合、Teams通知
    if lead.score >= 80:  # スコア閾値
        webhook_url = tenant.teams_webhook_url or os.getenv("TEAMS_WEBHOOK_URL")
        
        if webhook_url:
            teams_client = TeamsWebhookClient(webhook_url)
            await teams_client.send_hot_lead_notification(
                lead_data={
                    "lead_id": lead.id,
                    "company_name": lead.company_name,
                    "contact_name": lead.contact_name,
                    "job_title": lead.job_title,
                    "email": lead.email,
                    "phone": lead.phone,
                    "score": lead.score,
                    "assessment_title": lead.assessment.title
                },
                dashboard_url=f"https://app.diagnoleads.com/leads/{lead.id}"
            )
    
    return lead
```

---

## 🐛 トラブルシューティング

### Q1: "TEAMS_WEBHOOK_URL environment variable not set" エラー

**原因**: Webhook URL が設定されていない

**解決策**:
1. ステップ2で取得したURLを確認
2. `.env` ファイルに正しく追加されているか確認
3. スペルミス、余計なスペースがないか確認

### Q2: "Invalid card format or webhook URL" エラー (400)

**原因**: 
- Webhook URL が間違っている
- Adaptive Card の JSON フォーマットエラー

**解決策**:
1. Webhook URL を再確認
2. Teams でWebhookを削除して再作成
3. 新しいURLで再テスト

### Q3: "Webhook URL not found" エラー (404)

**原因**: 
- Webhook が削除された
- URL の一部が欠けている

**解決策**:
1. Teams でWebhook設定を確認
2. 必要に応じて再作成
3. URL全体がコピーされているか確認（改行などがないか）

### Q4: テストは成功したが、Teams にメッセージが表示されない

**原因**: 
- 別のチャネルに送信されている
- Teams の同期遅延

**解決策**:
1. 正しいチャネルを開いているか確認
2. Teams をリフレッシュ（F5）
3. 数分待ってから再確認
4. Teams アプリを再起動

### Q5: メッセージは表示されるが、文字化けしている

**原因**: 文字エンコーディングの問題

**解決策**:
- 通常は自動的に正しく処理されます
- 問題が続く場合はサポートに連絡

---

## 🔒 セキュリティのベストプラクティス

### Webhook URL の管理

1. **秘密として扱う**
   - Webhook URL は秘密情報です
   - Git にコミットしない（.env は .gitignore 済み）
   - チーム内で共有する場合は安全な方法で

2. **定期的なローテーション**
   - 定期的に Webhook を再作成
   - 古い URL を無効化

3. **最小権限の原則**
   - テスト用チャネルはプライベートに設定
   - 必要なメンバーのみを招待

4. **本番環境の分離**
   - 開発/テスト用と本番用で別の Webhook を使用
   - 環境変数で管理

---

## 📚 参考資料

### Microsoft 公式ドキュメント

- [Incoming Webhooks in Teams](https://learn.microsoft.com/microsoftteams/platform/webhooks-and-connectors/how-to/add-incoming-webhook)
- [Adaptive Cards Designer](https://adaptivecards.io/designer/)
- [Teams Connectors](https://learn.microsoft.com/microsoftteams/platform/webhooks-and-connectors/what-are-webhooks-and-connectors)

### DiagnoLeads ドキュメント

- `TEAMS_PERMISSION_UPDATE.md` - 権限とアプローチの比較
- `TEAMS_TESTING_GUIDE.md` - テスト実施手順
- `TEAMS_MESSAGE_SENDING.md` - メッセージ送信ガイド

---

## 📞 サポート

問題が解決しない場合:

1. エラーメッセージの全文を記録
2. 実行したコマンドを記録
3. `.env` ファイルの設定を確認（URL以外の部分）
4. IT部門/管理者に連絡

---

**Document Version**: 1.0  
**Created**: 2025-11-11  
**Status**: Ready to Use

**重要リマインダー**: 必ずテスト用チャネルで実施してください！
