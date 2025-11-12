# Microsoft Teams メッセージ送信機能ガイド

## 概要

DiagnoLeadsのMicrosoft Teams統合では、ホットリード獲得時に自動的にTeamsチャネルへ通知を送信できます。

---

## 🎯 実装済み機能

### 1. Adaptive Card送信
- リッチなフォーマットでリード情報を表示
- 会社名、担当者、スコア、連絡先などを含む
- DiagnoLeadsダッシュボードへの直接リンク

### 2. エラーハンドリング
- 権限不足の検出と分かりやすいエラーメッセージ
- HTTPステータスコード別の処理
- 詳細なログ出力

### 3. リトライロジック
- **Exponential Backoff**: 指数バックオフで自動リトライ
- **Rate Limit対応**: 429エラー時にRetry-Afterヘッダーを参照
- **一時的エラー対応**: 5xx, 408, ネットワークエラーを自動リトライ
- **デフォルト設定**: 最大3回リトライ、初回1秒待機

---

## 📋 必要な権限

メッセージ送信機能を使用するには、以下の追加権限が必要です：

### Azure Portal での設定

1. **Azure Portal** → **Azure Active Directory** → **App registrations**
2. **DiagnoLeads Teams Integration localhost** を選択
3. **API permissions** → **Add a permission**
4. **Microsoft Graph** → **Application permissions**
5. 以下の権限を追加:
   - ✅ `ChannelMessage.Send` - チャネルへのメッセージ送信
6. **Grant admin consent for [Your Organization]** をクリック

### 権限一覧

| 権限名 | 用途 | ステータス |
|---|---|---|
| `Group.Read.All` | チーム情報の取得 | ✅ 設定済み |
| `Team.ReadBasic.All` | チーム詳細の取得 | ✅ 設定済み |
| `Channel.ReadBasic.All` | チャネル情報の取得 | ✅ 設定済み |
| `User.Read.All` | ユーザー情報の取得 | ✅ 設定済み |
| `ChannelMessage.Send` | メッセージ送信 | ⚠️ 追加が必要 |

---

## 🧪 テスト方法

### 1. 権限設定の確認

```bash
cd /home/kurosawa/DiagnoLeads/backend
./venv/bin/python test_teams_permissions.py
```

すべてのテストが成功することを確認してください。

### 2. メッセージ送信テスト

```bash
cd /home/kurosawa/DiagnoLeads/backend
./venv/bin/python test_teams_send_message.py
```

**動作:**
1. 認証
2. チーム一覧取得
3. チャネル一覧取得
4. 送信先の確認プロンプト
5. テストメッセージ送信

**注意:** 
- 実際のTeamsチャネルにメッセージが送信されます
- 送信前に確認プロンプトが表示されます
- `yes` と入力しない限り送信されません

### 3. 期待される結果

#### 成功時:
```
============================================================
✅ MESSAGE SENT SUCCESSFULLY!
============================================================
Message ID: 1735123456789
Created at: 2025-11-11T07:30:00.000Z
Web URL: https://teams.microsoft.com/...

Please check the Teams channel to verify the message.
```

#### 権限不足時:
```
============================================================
❌ PERMISSION REQUIRED
============================================================

The 'ChannelMessage.Send' permission is not granted.

To fix this:
1. Go to Azure Portal → App registrations
2. Select your app → API permissions
3. Add 'ChannelMessage.Send' under Microsoft Graph → Application permissions
4. Click 'Grant admin consent for [Your Organization]'
5. Wait 5-10 minutes and try again
```

---

## 📊 送信されるAdaptive Card

### サンプル

```json
{
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
              "items": [{"type": "TextBlock", "text": "🔥", "size": "extraLarge"}]
            },
            {
              "type": "Column",
              "width": "stretch",
              "items": [
                {"type": "TextBlock", "text": "ホットリード獲得！", "weight": "bolder", "size": "large"},
                {"type": "TextBlock", "text": "スコア: 95/100", "color": "attention", "weight": "bolder"}
              ]
            }
          ]
        }
      ]
    },
    {
      "type": "FactSet",
      "facts": [
        {"title": "会社名", "value": "株式会社サンプル"},
        {"title": "担当者", "value": "山田太郎 (営業部長)"},
        {"title": "メール", "value": "yamada@example.com"},
        {"title": "電話", "value": "03-1234-5678"},
        {"title": "診断", "value": "営業課題診断"}
      ]
    }
  ],
  "actions": [
    {
      "type": "Action.OpenUrl",
      "title": "リードを見る",
      "url": "https://app.diagnoleads.com/leads/lead_12345"
    }
  ]
}
```

### プレビュー

Teamsチャネルでは以下のように表示されます：

```
┌──────────────────────────────────────────┐
│ 🔥 ホットリード獲得！                    │
│    スコア: 95/100                        │
├──────────────────────────────────────────┤
│ 会社名:   株式会社サンプル               │
│ 担当者:   山田太郎 (営業部長)           │
│ メール:   yamada@example.com            │
│ 電話:     03-1234-5678                   │
│ 診断:     営業課題診断                   │
├──────────────────────────────────────────┤
│ [リードを見る] ボタン                    │
└──────────────────────────────────────────┘
```

---

## 🔧 実装詳細

### TeamsClient.send_adaptive_card()

```python
@with_retry(max_retries=3, initial_delay=2.0)
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
        {
            "id": "message_id",
            "created_at": "2025-11-11T07:30:00.000Z",
            "web_url": "https://teams.microsoft.com/...",
            "status": "sent"
        }
    """
```

### リトライロジック

```python
# retry_policy.py

class RetryPolicy:
    """
    Exponential Backoffでリトライを実行
    """
    
    def should_retry(self, exception: Exception) -> bool:
        """
        リトライすべきエラー:
        - 429 Too Many Requests (Rate Limit)
        - 5xx Server Errors
        - 408 Request Timeout
        - Network Errors (ConnectError, TimeoutException)
        """
        
    def get_retry_after(self, exception: Exception, attempt: int) -> float:
        """
        次のリトライまでの待機時間:
        - Rate Limit: Retry-Afterヘッダーを参照
        - その他: Exponential Backoff (1s, 2s, 4s...)
        """
```

### 使用方法

```python
from app.integrations.microsoft.teams_client import TeamsClient

# クライアント初期化
client = TeamsClient(
    tenant_id=os.getenv("MICROSOFT_TENANT_ID"),
    client_id=os.getenv("MICROSOFT_CLIENT_ID"),
    client_secret=os.getenv("MICROSOFT_CLIENT_SECRET")
)

# ホットリード通知送信
lead_data = {
    "lead_id": "lead_12345",
    "company_name": "株式会社サンプル",
    "contact_name": "山田太郎",
    "job_title": "営業部長",
    "email": "yamada@example.com",
    "phone": "03-1234-5678",
    "score": 95,
    "assessment_title": "営業課題診断"
}

result = await client.send_hot_lead_notification(
    team_id="team_id_here",
    channel_id="channel_id_here",
    lead_data=lead_data
)

print(f"Message sent: {result['id']}")
```

---

## 🔒 セキュリティ考慮事項

### 1. 権限の最小化
- 必要最小限の権限のみを付与
- Delegatedではなく、Applicationを使用（ユーザーログイン不要）

### 2. 認証情報の保護
- Client Secretは環境変数で管理
- `.env`ファイルは`.gitignore`に追加済み
- 本番環境ではAzure Key Vault使用を推奨

### 3. レート制限対策
- リトライロジックでRetry-Afterヘッダーを尊重
- Microsoft Graph APIの制限: 1分あたり600リクエスト

### 4. エラー情報の取り扱い
- 本番環境ではエラーメッセージを適切にフィルタリング
- センシティブな情報をログに出力しない

---

## 📈 今後の拡張

### Phase 2: 高度な機能
- [ ] ユーザーメンション機能（担当者を自動タグ付け）
- [ ] 通知条件のカスタマイズ（スコア閾値、診断タイプ）
- [ ] バッチ通知（複数リードをまとめて送信）
- [ ] 通知テンプレートの管理

### Phase 3: Bot Framework統合
- [ ] 対話型Bot（診断開始、結果確認）
- [ ] Adaptive Card Actions（承認/却下ボタン）
- [ ] 双方向コミュニケーション

### Phase 4: 分析・監視
- [ ] 通知送信ログの記録
- [ ] 送信成功率の監視
- [ ] エラーアラート

---

## 🐛 トラブルシューティング

### Q1: "ChannelMessage.Send permission required" エラー

**原因**: 権限が未設定または管理者の同意が未実施

**解決策**:
1. Azure Portal → App registrations → API permissions
2. `ChannelMessage.Send`を追加
3. 管理者の同意を付与
4. 5-10分待機

---

### Q2: "The request timed out" エラー

**原因**: ネットワーク遅延またはMicrosoft Graph API側の問題

**解決策**:
- リトライロジックが自動的に再試行します
- 最大3回リトライしても失敗する場合は、時間をおいて再試行

---

### Q3: "Rate limit exceeded" エラー

**原因**: 1分あたり600リクエストの制限を超過

**解決策**:
- リトライロジックが自動的にRetry-Afterヘッダーに従って待機します
- 送信頻度を下げる、またはバッチ処理を実装

---

## 📞 サポート

問題が解決しない場合:
1. `docs/TEAMS_PERMISSION_CHECKLIST.md` を確認
2. `docs/TEAMS_SETUP_TROUBLESHOOTING.md` を確認
3. エラーメッセージ全文とログを記録
4. IT部門/管理者に連絡

---

**Document Version**: 1.0  
**Last Updated**: 2025-11-11  
**Status**: Ready for Testing
