# Microsoft Teams 通知機能 - クイックスタート

**所要時間: 5分**

---

## 🎯 この機能について

DiagnoLeadsでホットリードを獲得したとき、Microsoft Teamsチャネルに自動通知を送信できます。

**通知例:**
```
🔥 ホットリード獲得！
スコア: 95/100

会社名: 株式会社サンプル
担当者: 山田太郎 (営業部長)
メール: yamada@example.com
```

---

## ⚠️ 重要: テスト用チャネルを使用してください

- ❌ 本番のビジネスチャネルは絶対に使わないでください
- ✅ テスト専用チャネルを作成してください（推奨名: 'DiagnoLeads Test'）

---

## 📋 セットアップ手順

### ステップ1: Teams でテストチャネルを作成

1. Microsoft Teams を開く
2. チーム名の横の **...** → **チャネルを追加**
3. チャネル名: `DiagnoLeads Test`
4. プライバシー: **プライベート**（推奨）
5. メンバー: 自分のみを追加

### ステップ2: Incoming Webhook URL を取得

1. **DiagnoLeads Test** チャネルを開く
2. チャネル名の横の **...** → **コネクタ**
3. **Incoming Webhook** を検索 → **構成**
4. 名前: `DiagnoLeads` → **作成**
5. **Webhook URL をコピー**

### ステップ3: DiagnoLeads に設定

```bash
cd /home/kurosawa/DiagnoLeads/backend
./venv/bin/python setup_teams_webhook.py
```

プロンプトに従ってWebhook URLを貼り付けてください。

### ステップ4: テスト実行

```bash
./venv/bin/python app/integrations/microsoft/teams_webhook_client.py
```

### ステップ5: Teams で確認

**DiagnoLeads Test** チャネルに2つのテストメッセージが表示されていれば成功！

---

## 🐛 うまくいかない場合

### エラー: "TEAMS_WEBHOOK_URL not found"

**解決策:** ステップ3を再実行してください

### エラー: "Invalid card format or webhook URL" (400)

**解決策:** 
1. Webhook URLが正しいか確認
2. URL全体がコピーされているか確認（改行がないか）
3. Teamsでwebhookを削除して再作成

### メッセージが表示されない

**解決策:**
1. 正しいチャネルを開いているか確認
2. Teams をリフレッシュ（F5）
3. 数分待ってから再確認

---

## 📖 詳細ドキュメント

- **詳しい手順**: `docs/TEAMS_WEBHOOK_SETUP.md`
- **トラブルシューティング**: `docs/TEAMS_TESTING_GUIDE.md`
- **セキュリティ**: `docs/TEAMS_PERMISSION_UPDATE.md`

---

## ✅ セットアップ完了後

DiagnoLeads アプリで、リード獲得時に自動的にTeamsへ通知されます。

通知設定（スコア閾値、通知先チャネルなど）は管理画面で変更できます。

---

**重要リマインダー**: 必ずテスト用チャネルでセットアップしてください！
