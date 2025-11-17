# Phase 1機能 API仕様書

DiagnoLeads Phase 1で追加された新機能のREST API仕様です。

## 📋 目次

1. [A/Bテスト API](#abテスト-api)
2. [SMSキャンペーン API](#smsキャンペーン-api)
3. [QRコード画像ダウンロード API](#qrコード画像ダウンロード-api)
4. [認証・権限](#認証権限)

---

## A/Bテスト API

Thompson Samplingを使用した自動最適化A/Bテストの管理。

### エンドポイント一覧

#### 1. A/Bテスト作成

```http
POST /api/v1/tenants/{tenant_id}/ab-tests
```

**リクエストボディ**:
```json
{
  "assessment_id": "uuid",
  "name": "CTA文言テスト",
  "description": "診断開始ボタンの文言をA/Bテスト",
  "test_type": "cta_text",
  "variants": [
    {
      "name": "A",
      "description": "現行版",
      "is_control": true,
      "config": {
        "cta_text": "今すぐ診断を開始"
      }
    },
    {
      "name": "B",
      "description": "新パターン",
      "is_control": false,
      "config": {
        "cta_text": "無料で診断する"
      }
    }
  ],
  "min_sample_size": 100,
  "confidence_threshold": 0.95,
  "exploration_rate": 0.1
}
```

**レスポンス**: `201 Created`
```json
{
  "id": "uuid",
  "tenant_id": "uuid",
  "assessment_id": "uuid",
  "name": "CTA文言テスト",
  "status": "draft",
  "variants": [...],
  "created_at": "2025-11-17T12:00:00Z"
}
```

#### 2. A/Bテスト開始

```http
POST /api/v1/tenants/{tenant_id}/ab-tests/{test_id}/start
```

**レスポンス**: `200 OK`
```json
{
  "id": "uuid",
  "status": "running",
  "started_at": "2025-11-17T12:00:00Z"
}
```

#### 3. バリアント選択（Thompson Sampling）

```http
GET /api/v1/tenants/{tenant_id}/ab-tests/{test_id}/select-variant
```

**説明**: Thompson Samplingアルゴリズムで最適なバリアントを自動選択し、インプレッションを記録します。

**レスポンス**: `200 OK`
```json
{
  "variant_id": "uuid",
  "variant_name": "B",
  "config": {
    "cta_text": "無料で診断する"
  },
  "thompson_score": 0.523,
  "current_traffic_allocation": 0.62
}
```

#### 4. コンバージョン記録

```http
POST /api/v1/tenants/{tenant_id}/ab-tests/{test_id}/record-conversion
```

**リクエストボディ**:
```json
{
  "variant_id": "uuid"
}
```

**レスポンス**: `200 OK`
```json
{
  "success": true,
  "variant_id": "uuid",
  "conversions": 45,
  "impressions": 150,
  "conversion_rate": 0.30
}
```

#### 5. テスト結果取得

```http
GET /api/v1/tenants/{tenant_id}/ab-tests/{test_id}/results
```

**レスポンス**: `200 OK`
```json
{
  "test": {
    "id": "uuid",
    "name": "CTA文言テスト",
    "status": "running",
    "total_impressions": 500,
    "total_conversions": 125,
    "overall_conversion_rate": 0.25
  },
  "variants": [
    {
      "id": "uuid",
      "name": "A",
      "impressions": 180,
      "conversions": 40,
      "conversion_rate": 0.222,
      "bayesian_estimate": 0.225,
      "confidence_interval_lower": 0.18,
      "confidence_interval_upper": 0.27,
      "current_traffic_allocation": 0.35,
      "expected_loss": 0.025
    },
    {
      "id": "uuid",
      "name": "B",
      "impressions": 320,
      "conversions": 85,
      "conversion_rate": 0.265,
      "bayesian_estimate": 0.267,
      "confidence_interval_lower": 0.23,
      "confidence_interval_upper": 0.31,
      "current_traffic_allocation": 0.65,
      "expected_loss": 0.003
    }
  ],
  "winner_analysis": {
    "has_winner": false,
    "reason": "insufficient_confidence",
    "confidence": 0.87
  }
}
```

#### 6. テスト完了

```http
POST /api/v1/tenants/{tenant_id}/ab-tests/{test_id}/complete
```

**クエリパラメータ**:
- `force` (boolean): 信頼度不足でも強制完了

**レスポンス**: `200 OK`
```json
{
  "id": "uuid",
  "status": "completed",
  "winner_variant_id": "uuid",
  "completed_at": "2025-11-17T18:00:00Z"
}
```

#### 7. テスト一覧取得

```http
GET /api/v1/tenants/{tenant_id}/ab-tests
```

**クエリパラメータ**:
- `assessment_id` (uuid): 診断IDでフィルタ
- `status` (enum): ステータスでフィルタ (draft, running, paused, completed)
- `skip` (int): ページネーション
- `limit` (int): 取得件数（デフォルト: 50）

**レスポンス**: `200 OK`
```json
[
  {
    "id": "uuid",
    "name": "CTA文言テスト",
    "status": "running",
    "total_impressions": 500,
    "overall_conversion_rate": 0.25,
    "created_at": "2025-11-17T12:00:00Z"
  },
  ...
]
```

---

## SMSキャンペーン API

Twilio経由でのSMS一斉配信機能。

### エンドポイント一覧

#### 1. SMSキャンペーン作成

```http
POST /api/v1/tenants/{tenant_id}/sms/campaigns
```

**リクエストボディ**:
```json
{
  "assessment_id": "uuid",
  "qr_code_id": "uuid",
  "name": "11月診断キャンペーン",
  "message_template": "【DiagnoLeads】あなたの企業課題を無料診断！\n{url}\n※診断は3分で完了します",
  "recipients": [
    "+819012345678",
    "+819087654321"
  ],
  "scheduled_at": "2025-11-20T10:00:00Z"
}
```

**制限事項**:
- 最大1000件の電話番号
- 電話番号はE.164形式（`+`始まり）
- メッセージは160文字以内推奨（SMSセグメント制限）

**レスポンス**: `201 Created`
```json
{
  "id": "uuid",
  "tenant_id": "uuid",
  "name": "11月診断キャンペーン",
  "total_recipients": 2,
  "status": "pending",
  "estimated_cost": {
    "num_messages": 2,
    "region": "JP",
    "cost_per_message": 0.073,
    "total_cost": 0.146,
    "currency": "USD"
  },
  "created_at": "2025-11-17T12:00:00Z"
}
```

#### 2. SMSキャンペーン一覧取得

```http
GET /api/v1/tenants/{tenant_id}/sms/campaigns
```

**クエリパラメータ**:
- `skip` (int): ページネーション
- `limit` (int): 取得件数（デフォルト: 50）

**レスポンス**: `200 OK`
```json
[
  {
    "id": "uuid",
    "name": "11月診断キャンペーン",
    "total_recipients": 2,
    "sent_count": 2,
    "delivered_count": 2,
    "failed_count": 0,
    "status": "delivered",
    "created_at": "2025-11-17T12:00:00Z",
    "sent_at": "2025-11-17T12:05:00Z"
  },
  ...
]
```

#### 3. キャンペーン詳細取得

```http
GET /api/v1/tenants/{tenant_id}/sms/campaigns/{campaign_id}
```

**レスポンス**: `200 OK`
```json
{
  "id": "uuid",
  "name": "11月診断キャンペーン",
  "message_template": "【DiagnoLeads】あなたの企業課題を...",
  "total_recipients": 2,
  "sent_count": 2,
  "delivered_count": 2,
  "failed_count": 0,
  "status": "delivered",
  "created_at": "2025-11-17T12:00:00Z",
  "sent_at": "2025-11-17T12:05:00Z"
}
```

#### 4. キャンペーンメッセージ一覧取得

```http
GET /api/v1/tenants/{tenant_id}/sms/campaigns/{campaign_id}/messages
```

**レスポンス**: `200 OK`
```json
[
  {
    "id": "uuid",
    "phone_number": "+819012345678",
    "message_text": "【DiagnoLeads】あなたの企業課題を無料診断！\nhttps://short.url/abc\n※診断は3分で完了します",
    "twilio_sid": "SM123456789abcdef",
    "status": "delivered",
    "sent_at": "2025-11-17T12:05:00Z",
    "delivered_at": "2025-11-17T12:05:15Z",
    "clicked": true,
    "clicked_at": "2025-11-17T12:10:00Z"
  },
  ...
]
```

#### 5. テストSMS送信

```http
POST /api/v1/tenants/{tenant_id}/sms/test
```

**リクエストボディ**:
```json
{
  "to": "+819012345678",
  "message": "これはテストメッセージです"
}
```

**レスポンス**: `200 OK`
```json
{
  "success": true,
  "sid": "SM123456789abcdef",
  "status": "sent",
  "message": "テストSMSを送信しました"
}
```

#### 6. コスト見積もり

```http
POST /api/v1/tenants/{tenant_id}/sms/estimate
```

**リクエストボディ**:
```json
{
  "num_messages": 100,
  "region": "JP"
}
```

**レスポンス**: `200 OK`
```json
{
  "num_messages": 100,
  "region": "JP",
  "cost_per_message": 0.073,
  "total_cost": 7.30,
  "currency": "USD"
}
```

**対応リージョン**:
- `JP`: 日本 ($0.073/SMS)
- `US`: アメリカ ($0.0079/SMS)
- `OTHER`: その他 ($0.05/SMS)

---

## QRコード画像ダウンロード API

QRコードの画像生成・ダウンロード機能。

### エンドポイント一覧

#### 1. PNG画像ダウンロード

```http
GET /api/v1/tenants/{tenant_id}/qr-codes/{qr_code_id}/download/png
```

**クエリパラメータ**:
- `size` (int): サイズ（px）、デフォルト: 300
- `style` (enum): モジュールスタイル（square, rounded, circle）
- `color` (string): 前景色（16進数、`#`なし）、デフォルト: 000000
- `bg_color` (string): 背景色（16進数、`#`なし）、デフォルト: FFFFFF
- `logo` (boolean): ロゴ埋め込み

**レスポンス**: `200 OK`
- Content-Type: `image/png`
- Content-Disposition: `attachment; filename="qrcode-{qr_code_id}.png"`

#### 2. SVG画像ダウンロード

```http
GET /api/v1/tenants/{tenant_id}/qr-codes/{qr_code_id}/download/svg
```

**クエリパラメータ**:
- `color` (string): 前景色（16進数、`#`なし）
- `bg_color` (string): 背景色（16進数、`#`なし）

**レスポンス**: `200 OK`
- Content-Type: `image/svg+xml`
- Content-Disposition: `attachment; filename="qrcode-{qr_code_id}.svg"`

#### 3. プレビュー画像（Base64）

```http
GET /api/v1/tenants/{tenant_id}/qr-codes/{qr_code_id}/preview
```

**クエリパラメータ**: PNG画像と同じ

**レスポンス**: `200 OK`
```json
{
  "image_base64": "iVBORw0KGgoAAAANSUhEUgAA...",
  "size": 300,
  "format": "png"
}
```

**使用例（フロントエンド）**:
```javascript
const response = await fetch('/api/v1/tenants/xxx/qr-codes/xxx/preview?size=300');
const data = await response.json();
const imgSrc = `data:image/png;base64,${data.image_base64}`;
```

#### 4. 印刷用テンプレートダウンロード

```http
GET /api/v1/tenants/{tenant_id}/qr-codes/{qr_code_id}/download/print
```

**クエリパラメータ**:
- `size` (int): QRコードサイズ（px）
- `style` (enum): モジュールスタイル
- `color` (string): 前景色
- `bg_color` (string): 背景色
- `title` (string): タイトル文字
- `description` (string): 説明文字

**レスポンス**: `200 OK`
- Content-Type: `image/png`
- Content-Disposition: `attachment; filename="qrcode-print-{qr_code_id}.png"`

**出力イメージ**:
- A4印刷用（600x800px）
- QRコード + タイトル + 説明文
- フレーム付き

---

## 認証・権限

### 認証方式

すべてのAPIエンドポイントは**JWT認証**が必要です。

**リクエストヘッダー**:
```http
Authorization: Bearer <jwt_token>
```

### 権限レベル

| エンドポイント | 必要な権限 |
|---------------|-----------|
| A/Bテスト作成・編集 | `tenant_admin` または `user` |
| A/Bテスト閲覧 | `tenant_admin` または `user` |
| SMSキャンペーン作成 | `tenant_admin` のみ |
| SMSキャンペーン閲覧 | `tenant_admin` または `user` |
| QRコードダウンロード | `tenant_admin` または `user` |

### エラーレスポンス

#### 401 Unauthorized

```json
{
  "detail": "Unauthorized"
}
```

#### 403 Forbidden

```json
{
  "detail": "Permission denied"
}
```

#### 404 Not Found

```json
{
  "detail": "Resource not found"
}
```

#### 422 Unprocessable Entity

```json
{
  "detail": [
    {
      "loc": ["body", "recipients", 0],
      "msg": "Invalid phone number format. Must be E.164 format (+country_code + number)",
      "type": "value_error"
    }
  ]
}
```

#### 500 Internal Server Error

```json
{
  "detail": "Internal server error"
}
```

---

## レート制限

| API種別 | レート制限 |
|---------|----------|
| A/Bテスト API | 100 req/min |
| SMS API | 10 req/min（コスト制御のため） |
| QRコード画像 | 50 req/min |

レート制限超過時:

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 60

{
  "detail": "Rate limit exceeded. Please try again in 60 seconds."
}
```

---

## 使用例

### A/Bテスト実装例（JavaScript）

```javascript
// 1. バリアント選択
const selectVariant = async (testId) => {
  const response = await fetch(
    `/api/v1/tenants/${tenantId}/ab-tests/${testId}/select-variant`,
    {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    }
  );
  const data = await response.json();

  // 選択されたバリアントの設定を適用
  applyVariantConfig(data.config);

  return data.variant_id;
};

// 2. コンバージョン記録
const recordConversion = async (testId, variantId) => {
  await fetch(
    `/api/v1/tenants/${tenantId}/ab-tests/${testId}/record-conversion`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ variant_id: variantId })
    }
  );
};
```

### SMSキャンペーン実装例（Python）

```python
import requests

# SMSキャンペーン作成
def create_sms_campaign(tenant_id, token, recipients):
    url = f"/api/v1/tenants/{tenant_id}/sms/campaigns"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "assessment_id": "xxx",
        "qr_code_id": "yyy",
        "name": "テストキャンペーン",
        "message_template": "診断はこちら: {url}",
        "recipients": recipients
    }

    response = requests.post(url, headers=headers, json=data)
    return response.json()

# 使用例
recipients = ["+819012345678", "+819087654321"]
campaign = create_sms_campaign("tenant_id", "jwt_token", recipients)
print(f"Campaign created: {campaign['id']}")
```

---

## 変更履歴

| バージョン | 日付 | 変更内容 |
|-----------|------|---------|
| 1.0 | 2025-11-17 | 初版リリース（Phase 1機能） |

---

## サポート

API仕様に関する質問は、開発チームまでお問い合わせください。
