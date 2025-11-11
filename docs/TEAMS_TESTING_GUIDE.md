# Microsoft Teams メッセージ送信テストガイド

## ⚠️ 重要な注意事項

このテストでは**実際のMicrosoft Teamsチャネルにメッセージが送信されます**。

### 安全なテスト実施のために

1. **テスト用チャネルを使用してください**
   - 'test' や 'テスト' を含むチャネル名
   - 'sandbox' や 'dev' を含むチャネル名
   - 自分だけがいるプライベートチャネル

2. **避けるべきチャネル**
   - 全社チャネル
   - 営業・マーケティングなどの重要な業務チャネル
   - 役員や経営陣がいるチャネル
   - 顧客とのやり取りがあるチャネル

3. **推奨: テスト用チャネルの作成**
   - Teams で新しいチャネルを作成
   - 名前: "DiagnoLeads Test" や "テスト用"
   - プライベート設定で自分だけを招待

---

## 事前準備

### 1. ChannelMessage.Send 権限の追加

メッセージ送信には追加の権限が必要です。

**Azure Portal での設定:**

1. [Azure Portal](https://portal.azure.com) にアクセス
2. **Azure Active Directory** → **App registrations**
3. **DiagnoLeads Teams Integration localhost** を選択
4. **API permissions** → **Add a permission**
5. **Microsoft Graph** → **Application permissions**
6. `ChannelMessage.Send` を検索して追加
7. **Grant admin consent for [Your Organization]** をクリック
8. 5-10分待機（権限の反映に時間がかかる場合があります）

### 2. テスト用チャネルの準備（推奨）

**Microsoft Teams での設定:**

1. Microsoft Teams を開く
2. 任意のチームを選択（または新しいチーム作成）
3. **チャネルの追加** をクリック
4. 以下の情報を入力:
   - チャネル名: `DiagnoLeads Test`
   - プライバシー: `プライベート` （推奨）
   - メンバー: 自分のみを追加
5. チャネル作成完了

---

## テスト実行手順

### ステップ1: テストスクリプトの実行

```bash
cd /home/kurosawa/DiagnoLeads/backend
./venv/bin/python test_teams_send_safe.py
```

### ステップ2: チームの選択

表示されるチームリストから選択します：

```
Available teams (showing first 20):
   1. プラットフォームサービス部
   2. システムFAQサイト
   3. DXサービス部
   ...

Select team number (1-20), or 'q' to quit: 
```

**推奨:** テスト用チャネルを作成したチームの番号を入力

### ステップ3: チャネルの選択

選択したチームのチャネルリストが表示されます：

```
📗 RECOMMENDED: Safe test channels detected:
  ✅ 1. DiagnoLeads Test

All available channels:
  ✅  1. DiagnoLeads Test
  ⚠️   2. General
  ⚠️   3. 営業チーム

Select channel number (1-3), or 'q' to quit:
```

**推奨:** ✅マークが付いたチャネルを選択

### ステップ4: 安全性確認

テスト用チャネルでない場合、追加の確認が表示されます：

```
⚠️  WARNING: This does not appear to be a test channel!
⚠️  Channel: 営業チーム

Are you ABSOLUTELY SURE you want to send to this channel? (type 'YES' to confirm):
```

**注意:** この警告が表示された場合は `q` を入力して終了し、安全なチャネルを選択し直してください。

### ステップ5: 最終確認

送信内容の最終確認が表示されます：

```
FINAL CONFIRMATION
============================================================
Team:    プラットフォームサービス部
Channel: DiagnoLeads Test

A test message will be sent with:
  - Title: 🔥 ホットリード獲得！
  - Company: テスト株式会社
  - Contact: テスト太郎 (テスト部長)
  - Score: 95/100

Type 'SEND' to proceed:
```

**確認:** 送信先が正しいことを確認し、`SEND` と入力（大文字）

---

## 期待される結果

### 成功時

```
============================================================
✅ MESSAGE SENT SUCCESSFULLY!
============================================================
Message ID: 1735123456789
Created at: 2025-11-11T08:00:00.000Z
Web URL: https://teams.microsoft.com/l/message/...

Team: プラットフォームサービス部
Channel: DiagnoLeads Test

✅ Please check the Teams channel to verify the message.
```

**Teams チャネルでの表示例:**

```
┌──────────────────────────────────────────────────────────┐
│ DiagnoLeads Bot  8:00                                    │
├──────────────────────────────────────────────────────────┤
│                                                          │
│ 🔥 ホットリード獲得！                                    │
│    スコア: 95/100                                        │
│                                                          │
│ 会社名:   テスト株式会社                                 │
│ 担当者:   テスト太郎 (テスト部長)                       │
│ メール:   test@example.com                              │
│ 電話:     03-0000-0000                                   │
│ 診断:     【テスト送信】営業課題診断                     │
│                                                          │
│ [リードを見る] ボタン                                    │
└──────────────────────────────────────────────────────────┘
```

### 権限不足エラー

```
============================================================
❌ PERMISSION REQUIRED: ChannelMessage.Send
============================================================

The 'ChannelMessage.Send' permission is not granted.

To add this permission:
1. Go to Azure Portal (https://portal.azure.com)
2. Navigate to: Azure Active Directory → App registrations
3. Select: DiagnoLeads Teams Integration localhost
4. Click: API permissions → Add a permission
5. Select: Microsoft Graph → Application permissions
6. Search and add: ChannelMessage.Send
7. Click: Grant admin consent for [Your Organization]
8. Wait 5-10 minutes for changes to propagate

Then run this script again.
```

**対処:** 「事前準備」セクションの手順1を実行してください。

---

## トラブルシューティング

### Q1: "Team/Channel not found" エラー

**原因:** チーム/チャネルIDが無効、または権限がない

**解決策:**
1. 別のチーム/チャネルを選択
2. 自分がメンバーとして参加しているチームを選択
3. チャネルのプライバシー設定を確認

---

### Q2: メッセージが送信されたが、Teamsで表示されない

**原因:** 
- ブラウザ/アプリのキャッシュ
- Teams の同期遅延

**解決策:**
1. Teams をリフレッシュ（F5）
2. Teams アプリを再起動
3. 数分待ってから再確認

---

### Q3: "The request timed out" エラー

**原因:** ネットワーク遅延またはAPI側の問題

**解決策:**
- リトライロジックが自動的に再試行します（最大3回）
- それでも失敗する場合は、時間をおいて再実行

---

### Q4: チャネルリストが空

**原因:** チームにチャネルがない、または権限不足

**解決策:**
1. Teams アプリでチャネルを作成
2. 別のチームを選択
3. `Channel.ReadBasic.All` 権限を確認

---

## 次のステップ

テスト送信が成功したら：

### 1. DiagnoLeads アプリへの統合

リード獲得時の自動通知を実装:

```python
# backend/app/services/lead_service.py

from app.integrations.microsoft.teams_client import TeamsClient

async def create_lead(lead_data: dict):
    # リード作成処理
    lead = await save_lead(lead_data)
    
    # ホットリードの場合、Teams通知
    if lead.score >= 80:  # スコア閾値
        teams_client = TeamsClient(...)
        await teams_client.send_hot_lead_notification(
            team_id=tenant.teams_team_id,
            channel_id=tenant.teams_channel_id,
            lead_data=lead_data
        )
    
    return lead
```

### 2. 設定UIの実装

テナント管理画面で通知設定を管理:

- 通知先チーム/チャネルの選択
- スコア閾値の設定
- 通知テンプレートのカスタマイズ
- 通知ON/OFFの切り替え

### 3. 高度な機能

- ユーザーメンション（担当者を自動タグ付け）
- 通知条件の細かいカスタマイズ
- バッチ通知（複数リードをまとめて送信）

---

## セキュリティチェックリスト

テスト実施前に確認:

- [ ] テスト用チャネルを準備した
- [ ] 送信先チャネルが重要なビジネスチャネルでないことを確認
- [ ] ChannelMessage.Send 権限が付与されている
- [ ] 環境変数（.env）にClient Secretが設定されている
- [ ] .envファイルが.gitignoreに含まれている

---

## 付録: テストデータ

テストメッセージで送信されるデータ:

```python
lead_data = {
    "lead_id": "lead_test_001",
    "company_name": "テスト株式会社",
    "contact_name": "テスト太郎",
    "job_title": "テスト部長",
    "email": "test@example.com",
    "phone": "03-0000-0000",
    "score": 95,
    "assessment_title": "【テスト送信】営業課題診断"
}
```

このデータは完全にダミーです。実際の顧客情報は含まれていません。

---

**Document Version**: 1.0  
**Created**: 2025-11-11  
**Status**: Ready for Safe Testing

**重要:** 必ず安全なテスト環境でテストを実施してください。
