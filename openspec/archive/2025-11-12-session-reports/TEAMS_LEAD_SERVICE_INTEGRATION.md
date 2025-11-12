# Lead Service Teams Integration - 実装完了

**Date**: 2025-11-11  
**Status**: ✅ Implementation Complete

---

## 🎉 実装内容

DiagnoLeadsのLead ServiceにMicrosoft Teams自動通知機能を統合しました。

### 機能概要

ホットリード（スコア ≥ 80）が作成またはスコア更新された際、自動的にMicrosoft Teamsチャネルに通知を送信します。

---

## 📊 実装詳細

### 1. Lead Service への統合

**ファイル**: `backend/app/services/lead_service.py`

#### 追加された機能

**a) Teams通知メソッド**
```python
async def _send_teams_notification(self, lead: Lead, tenant: Tenant) -> None:
    """
    ホットリード通知を非同期で送信
    - スコア >= 80 のリードのみ通知
    - Webhook URLはテナント設定またはグローバル環境変数から取得
    - エラーはログ出力のみ（リード作成を失敗させない）
    """
```

**b) リード作成時の通知**
```python
def create(self, data: LeadCreate, tenant_id: UUID, created_by: UUID) -> Lead:
    # リード作成処理
    lead = Lead(...)
    self.db.add(lead)
    self.db.commit()
    
    # スコア >= 80 の場合、Teams通知を送信
    if lead.score >= 80:
        asyncio.create_task(self._send_teams_notification(lead, tenant))
```

**c) スコア更新時の通知**
```python
def update_score(self, lead_id: UUID, data: LeadScoreUpdate, tenant_id: UUID) -> Lead:
    old_score = lead.score
    lead.score = new_score
    
    # スコアが80を超えた場合のみ通知（閾値超え検出）
    if old_score < 80 and new_score >= 80:
        asyncio.create_task(self._send_teams_notification(lead, tenant))
```

---

### 2. 設定管理

**a) グローバル設定（デフォルト）**
```bash
# backend/.env
TEAMS_WEBHOOK_URL=https://sasbusiness.webhook.office.com/webhookb2/...
```

**b) テナント別設定（優先）**
```python
# Tenant.settings JSON
{
    "teams_webhook_url": "https://custom-webhook-url...",
    "teams_notification_enabled": true,
    "teams_score_threshold": 80
}
```

優先順位: テナント設定 > グローバル設定

---

### 3. 通知内容

#### Adaptive Card フォーマット

```
┌──────────────────────────────────────────────┐
│ 🔥 ホットリード獲得！                        │
│    スコア: 95/100                            │
├──────────────────────────────────────────────┤
│ 会社名:   テスト株式会社                     │
│ 担当者:   テスト太郎 (テスト部長)           │
│ メール:   test@example.com                  │
│ 電話:     03-1234-5678                       │
│ 診断:     営業課題診断                       │
├──────────────────────────────────────────────┤
│ [リードを見る] ボタン                        │
└──────────────────────────────────────────────┘
```

---

## 🔧 技術仕様

### 通知トリガー

| イベント | 条件 | 動作 |
|---|---|---|
| リード作成 | `score >= 80` | 即座に通知 |
| スコア更新 | `old_score < 80 AND new_score >= 80` | 閾値超え時のみ通知 |
| スコア更新 | `old_score >= 80 AND new_score >= 80` | 通知しない（重複防止） |

### エラーハンドリング

```python
try:
    await teams_client.send_hot_lead_notification(...)
    print(f"✅ Teams notification sent for lead {lead.id}")
except Exception as e:
    # エラーはログ出力のみ（リード作成を失敗させない）
    print(f"⚠️  Failed to send Teams notification: {str(e)}")
```

**設計思想**: 通知失敗はリード作成の失敗にしない

### 非同期処理

```python
# バックグラウンドタスクとして実行
asyncio.create_task(self._send_teams_notification(lead, tenant))
```

- メインのリード作成処理をブロックしない
- レスポンスタイムへの影響を最小化

---

## 📋 設定例

### テナントごとに異なる通知先

```python
# Tenant 1: 営業チーム
tenant_1.settings = {
    "teams_webhook_url": "https://...webhook1...",
    "teams_score_threshold": 80
}

# Tenant 2: マーケティングチーム
tenant_2.settings = {
    "teams_webhook_url": "https://...webhook2...",
    "teams_score_threshold": 90  # より高いスコアのみ
}

# Tenant 3: 通知無効
tenant_3.settings = {
    "teams_webhook_url": "",  # 空文字列で無効化
}
```

---

## 🧪 テスト方法

### 手動テスト

#### 1. ホットリード作成テスト

**API リクエスト:**
```bash
POST /api/v1/leads
{
  "name": "テスト太郎",
  "email": "test@example.com",
  "company": "テスト株式会社",
  "job_title": "部長",
  "phone": "03-1234-5678",
  "score": 95
}
```

**期待される動作:**
1. リードが作成される
2. Teams チャネルに通知が送信される
3. APIレスポンスは正常に返る（通知失敗でもエラーにならない）

#### 2. スコア更新テスト

**API リクエスト:**
```bash
# 1. 通常リード作成（score = 70）
POST /api/v1/leads
{
  "name": "更新テスト太郎",
  "email": "update-test@example.com",
  "score": 70
}

# 2. スコア更新（70 → 90）
PATCH /api/v1/leads/{lead_id}/score
{
  "score": 90
}
```

**期待される動作:**
1. リード作成時は通知なし（score < 80）
2. スコア更新時に通知が送信される（閾値超え）

---

## 🎯 使用シナリオ

### シナリオ1: 診断完了時の自動通知

```python
# 診断結果からリード作成
assessment_result = {
    "score": 92,  # AI により算出
    "user_info": {...}
}

lead = lead_service.create(
    data=LeadCreate(**assessment_result),
    tenant_id=tenant.id,
    created_by=system_user.id
)
# → Teams に自動通知が送信される
```

### シナリオ2: AIスコアリング更新

```python
# AIによるリードスコアの再評価
new_score = ai_service.calculate_lead_score(lead, additional_data)

if new_score != lead.score:
    lead_service.update_score(
        lead_id=lead.id,
        data=LeadScoreUpdate(score=new_score),
        tenant_id=tenant.id
    )
    # → スコアが80を超えた場合のみ通知
```

### シナリオ3: 営業担当への即座な通知

```
ユーザーが診断完了
    ↓
スコア算出（95点）
    ↓
リード作成
    ↓
Teams 通知送信（営業チャネル）
    ↓
営業担当が即座に確認
    ↓
迅速なフォローアップ
```

---

## 📈 今後の拡張

### Phase 1: 設定UI（推奨）

**管理画面で設定可能に:**
- ✅ Webhook URL設定
- ✅ 通知ON/OFF切り替え
- ✅ スコア閾値カスタマイズ
- ✅ 通知テンプレート選択

### Phase 2: 高度な通知条件

```python
# テナント設定例
{
    "teams_notification": {
        "enabled": true,
        "score_threshold": 80,
        "filters": {
            "company_size": ["mid", "large"],  # 中小企業のみ
            "job_titles": ["部長", "役員"],     # 決裁者のみ
            "industries": ["IT", "金融"]        # 業界フィルタ
        },
        "schedule": {
            "business_hours_only": true,        # 営業時間のみ
            "timezone": "Asia/Tokyo"
        }
    }
}
```

### Phase 3: 通知履歴とログ

```python
class TeamsNotificationLog(Base):
    __tablename__ = "teams_notification_logs"
    
    id = Column(UUID, primary_key=True)
    tenant_id = Column(UUID, ForeignKey("tenants.id"))
    lead_id = Column(UUID, ForeignKey("leads.id"))
    sent_at = Column(DateTime)
    status = Column(String)  # success, failed
    error_message = Column(Text, nullable=True)
```

### Phase 4: A/Bテストと最適化

- 通知タイミングの最適化
- メッセージフォーマットのA/Bテスト
- 営業担当の反応時間分析

---

## ✅ 完了チェックリスト

### 実装

- [x] Lead Service に Teams通知機能を統合
- [x] リード作成時の通知
- [x] スコア更新時の通知（閾値超え検出）
- [x] テナント別設定サポート
- [x] エラーハンドリング
- [x] 非同期処理実装

### 設定

- [x] Config.pyに環境変数追加
- [x] Webhook URL設定（グローバル）
- [x] テナント設定の準備（settings JSON）

### ドキュメント

- [x] 統合ガイド作成
- [x] 技術仕様書作成
- [x] テスト手順書作成
- [x] 使用シナリオ例

### テスト

- [ ] 手動テスト（データベース必要）
- [ ] 統合テスト
- [ ] E2Eテスト

---

## 🚀 本番運用の準備

### 1. 環境変数設定

**本番環境:**
```bash
TEAMS_WEBHOOK_URL=<本番用Webhook URL>
```

### 2. テナント設定（推奨）

各テナントのWebhook URLを個別に設定:

```sql
UPDATE tenants 
SET settings = jsonb_set(
    settings, 
    '{teams_webhook_url}', 
    '"https://..."'
)
WHERE id = 'tenant_id_here';
```

### 3. 監視とログ

```python
# ログ出力を確認
# ✅ Teams notification sent for lead {lead.id} (score: {score})
# ⚠️  No Teams webhook URL configured for tenant {tenant.name}
# ⚠️  Failed to send Teams notification: {error}
```

---

## 📞 サポート

### トラブルシューティング

**Q1: 通知が送信されない**
- Webhook URLが設定されているか確認
- スコアが80以上か確認
- ログで`⚠️`を確認

**Q2: 通知が重複する**
- スコア更新時の閾値超え検出ロジックを確認
- `old_score < 80 AND new_score >= 80` の条件

**Q3: リード作成が失敗する**
- 通知エラーはリード作成を失敗させません
- 別の原因を調査してください

---

## 📚 関連ドキュメント

- `TEAMS_WEBHOOK_SETUP.md` - Webhook URL取得手順
- `TEAMS_INTEGRATION_SUCCESS.md` - 統合テスト結果
- `SESSION_SUMMARY_TEAMS_INTEGRATION.md` - 実装セッションサマリー

---

**Document Version**: 1.0  
**Created**: 2025-11-11  
**Status**: ✅ Implementation Complete - Ready for Manual Testing
