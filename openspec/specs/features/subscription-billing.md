# Subscription & Billing Management System

**Status**: Approved
**Priority**: Critical
**Phase**: 1.5 (Revenue Foundation)
**Estimated Effort**: 8-10 weeks
**Dependencies**: Stripe API, Webhook Infrastructure, Email Service

## Overview

サブスクリプション・請求管理システムは、DiagnoLeadsの収益化基盤となる機能です。Stripe統合により、自動課金、プラン管理、利用量ベースの従量課金、請求書発行を実現し、運用コストを最小化しながらスケーラブルな収益モデルを構築します。

## Business Value

- **収益自動化**: 手動請求作業 100%削減
- **ARR成長**: 自動アップセル・アップグレードで +30%
- **解約率低減**: 柔軟なプラン変更で -20%
- **運用効率**: 請求処理時間 95%削減（月間40時間 → 2時間）
- **キャッシュフロー改善**: 自動回収で平均回収期間 60日 → 1日

## Revenue Model

### Pricing Tiers

| プラン | 月額料金 | 診断数 | リード数 | 特徴 |
|--------|----------|--------|----------|------|
| **Free** | ¥0 | 1 | 50 | 基本機能のみ |
| **Starter** | ¥29,800 | 5 | 500 | AI生成、分析 |
| **Professional** | ¥98,000 | 20 | 3,000 | Teams統合、A/Bテスト |
| **Business** | ¥298,000 | 100 | 15,000 | ホワイトラベル、SSO |
| **Enterprise** | 個別見積 | 無制限 | 無制限 | 専任サポート、SLA |

### Usage-Based Pricing (従量課金)

- **追加診断**: ¥5,000/診断/月
- **追加リード**: ¥10/リード（クォータ超過時）
- **AI生成**: ¥500/診断生成
- **外部連携API呼び出し**: ¥0.5/リクエスト

## Core Features

### 1. サブスクリプション管理
- プラン選択・変更（即時/次回更新時）
- 自動アップグレード・ダウングレード
- 日割り計算（プロレーション）
- 無料トライアル（14日間）
- クーポン・プロモーションコード

### 2. 自動請求・決済
- クレジットカード決済（Stripe）
- 請求書払い（Enterprise向け）
- 自動リトライ（決済失敗時）
- ダンニング管理（督促自動化）
- 領収書自動発行・送信

### 3. 利用量トラッキング
- リアルタイム利用状況監視
- クォータアラート（80%, 100%）
- 自動スケーリング（従量課金移行）
- 月次レポート生成

### 4. 請求書管理
- PDF請求書自動生成
- インボイス制度対応（適格請求書）
- 請求書履歴・ダウンロード
- 会計システム連携（freee, マネーフォワード）

## User Stories

### 1. プラン選択・支払い

**As a** 新規テナント管理者
**I want to** 有料プランに簡単に登録
**So that** すぐに高度な機能を使い始められる

**Acceptance Criteria**:

**Given**: テナントがFreeプランを使用中
**When**: 「プランをアップグレード」をクリック
**Then**:
- プラン比較表が表示される
- 各プランの機能差分が明確
- 「14日間無料トライアル」が強調表示
- プラン選択 → Stripeチェックアウトに遷移
- クレジットカード情報入力
- 決済完了 → 即座にアップグレード
- ウェルカムメール送信
- ダッシュボードに新機能が表示

**Given**: トライアル期間中
**When**: トライアル終了3日前
**Then**:
- リマインダーメール送信
- ダッシュボードにバナー表示
- ワンクリックで有料プランに移行可能

### 2. 利用量クォータ管理

**As a** テナント管理者
**I want to** 現在の利用状況を常に把握
**So that** クォータ超過を事前に防げる

**Acceptance Criteria**:

**Given**: Starterプラン（診断5個、リード500件）
**When**: 4個目の診断を作成
**Then**:
- 「残り1診断」の警告表示
- アップグレード提案バナー表示
- 利用状況ダッシュボードにグラフ表示

**Given**: リード数が480件（96%）
**When**: ダッシュボードにアクセス
**Then**:
- 「クォータ残り4%」のアラート表示
- オプション提示:
  - アップグレード（Professionalプラン）
  - 追加リードパック購入（500件 ¥5,000）
- 予測メッセージ: 「現在のペースだと3日後に上限到達」

**Given**: リード数が501件（100%超過）
**When**: 新規リードが獲得される
**Then**:
- リードは記録される（データロスなし）
- 超過分が自動的に従量課金として請求
- 管理者に即座にメール通知
- ダッシュボードに「超過中」バッジ表示

### 3. プラン変更

**As a** テナント管理者
**I want to** プランをいつでも変更
**So that** ビジネスの成長に合わせて柔軟に対応できる

**Acceptance Criteria**:

**Given**: Starterプラン利用中
**When**: Professionalプランにアップグレード
**Then**:
- 現在の課金サイクル残日数を計算
- 日割り差額を即座に請求（例: 残り15日分の差額）
- アップグレード即時反映
- 新機能が即座に利用可能
- 次回更新日は変更なし

**Given**: Professionalプラン利用中
**When**: Starterプランにダウングレード
**Then**:
- 「次回更新時にダウングレード」が選択肢として表示
- 即時ダウングレードの場合、返金なし（クレジット付与）
- 機能制限の影響を警告（例: 「6個の診断を削除または無効化する必要があります」）
- 確認後、ダウングレード予約
- 更新日にダウングレード実行

### 4. 請求書管理

**As a** 経理担当者
**I want to** 請求書を簡単にダウンロード
**So that** 経費処理をスムーズに行える

**Acceptance Criteria**:

**Given**: 請求が発生している
**When**: 請求書ページにアクセス
**Then**:
- 過去の請求書一覧が表示（月別）
- 各請求書にステータス表示（支払済、未払、失敗）
- PDFダウンロードボタン
- 請求書には以下が含まれる:
  - 適格請求書番号（インボイス制度対応）
  - 発行元情報（DiagnoLeads運営会社）
  - 請求先情報（テナント企業）
  - 明細（基本料金、従量課金、税金）
  - 合計金額
- 一括ダウンロード機能（ZIP）

**Given**: Enterpriseプラン（請求書払い）
**When**: 月末締め日
**Then**:
- 請求書が自動生成
- PDFがメール送付
- 請求書データがAPI経由で会計システムに連携
- 支払期限: 請求日から30日後

### 5. 決済失敗ハンドリング

**As a** システム
**I want to** 決済失敗時に自動的にリトライ・督促
**So that** 解約率を最小化できる

**Acceptance Criteria**:

**Given**: 月次更新時にクレジットカード決済が失敗
**When**: 決済エラーが発生
**Then**:
- 即座にテナント管理者にメール通知
- ダッシュボードに「決済失敗」バナー表示
- 3日後、7日後、14日後に自動リトライ
- リトライごとにリマインダーメール送信
- 14日後も失敗の場合:
  - アカウントを「制限モード」に移行
  - 新規診断作成・リード獲得を停止
  - 既存データは閲覧可能
  - 30日後も未払いの場合、アカウント一時停止

**Given**: 決済失敗後、カード情報を更新
**When**: 新しいカード情報を登録
**Then**:
- 即座に未払い請求を再試行
- 成功した場合、制限モード解除
- ウェルカムバックメール送信

## Technical Architecture

### Stripe Integration

```python
# backend/app/services/billing/stripe_service.py
import stripe
from typing import Optional, Dict
from app.models import Tenant, Subscription
from app.core.config import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

class StripeService:
    """Stripe決済サービス"""

    async def create_customer(self, tenant: Tenant) -> str:
        """Stripeカスタマー作成"""
        customer = stripe.Customer.create(
            email=tenant.admin_email,
            name=tenant.company_name,
            metadata={
                "tenant_id": str(tenant.id),
                "environment": settings.ENVIRONMENT
            }
        )

        # テナントにStripe Customer IDを保存
        tenant.stripe_customer_id = customer.id
        await tenant.save()

        return customer.id

    async def create_subscription(
        self,
        tenant: Tenant,
        price_id: str,
        trial_days: int = 14,
        coupon: Optional[str] = None
    ) -> Subscription:
        """サブスクリプション作成"""

        # Stripe Customer未作成の場合は作成
        if not tenant.stripe_customer_id:
            await self.create_customer(tenant)

        # Stripeサブスクリプション作成
        stripe_sub = stripe.Subscription.create(
            customer=tenant.stripe_customer_id,
            items=[{"price": price_id}],
            trial_period_days=trial_days,
            coupon=coupon,
            payment_behavior="default_incomplete",
            payment_settings={"save_default_payment_method": "on_subscription"},
            expand=["latest_invoice.payment_intent"],
            metadata={
                "tenant_id": str(tenant.id)
            }
        )

        # DBにサブスクリプション記録
        subscription = await Subscription.create(
            tenant_id=tenant.id,
            stripe_subscription_id=stripe_sub.id,
            stripe_price_id=price_id,
            plan_name=self._get_plan_name(price_id),
            status=stripe_sub.status,
            current_period_start=stripe_sub.current_period_start,
            current_period_end=stripe_sub.current_period_end,
            trial_end=stripe_sub.trial_end
        )

        return subscription

    async def change_subscription_plan(
        self,
        subscription: Subscription,
        new_price_id: str,
        prorate: bool = True
    ) -> Subscription:
        """プラン変更"""

        stripe_sub = stripe.Subscription.retrieve(
            subscription.stripe_subscription_id
        )

        # プラン変更
        updated_sub = stripe.Subscription.modify(
            subscription.stripe_subscription_id,
            items=[{
                "id": stripe_sub["items"]["data"][0].id,
                "price": new_price_id
            }],
            proration_behavior="always_invoice" if prorate else "none"
        )

        # DB更新
        subscription.stripe_price_id = new_price_id
        subscription.plan_name = self._get_plan_name(new_price_id)
        subscription.status = updated_sub.status
        await subscription.save()

        return subscription

    async def cancel_subscription(
        self,
        subscription: Subscription,
        at_period_end: bool = True
    ):
        """サブスクリプションキャンセル"""

        stripe.Subscription.modify(
            subscription.stripe_subscription_id,
            cancel_at_period_end=at_period_end
        )

        if not at_period_end:
            stripe.Subscription.cancel(subscription.stripe_subscription_id)
            subscription.status = "canceled"
        else:
            subscription.cancel_at_period_end = True

        await subscription.save()

    async def record_usage(
        self,
        subscription: Subscription,
        quantity: int,
        action: str = "set"  # set, increment
    ):
        """使用量記録（従量課金）"""

        stripe_sub = stripe.Subscription.retrieve(
            subscription.stripe_subscription_id
        )

        # メータリング対象のSubscription Itemを取得
        usage_item = next(
            (item for item in stripe_sub["items"]["data"]
             if item.price.recurring.usage_type == "metered"),
            None
        )

        if usage_item:
            stripe.SubscriptionItem.create_usage_record(
                usage_item.id,
                quantity=quantity,
                action=action,
                timestamp=int(time.time())
            )
```

### Usage Tracking Service

```python
# backend/app/services/billing/usage_tracker.py
from app.models import Tenant, Subscription, UsageRecord
from app.services.billing.stripe_service import StripeService

class UsageTracker:
    """利用量トラッキング"""

    def __init__(self):
        self.stripe_service = StripeService()

    async def check_quota(self, tenant: Tenant, resource: str) -> Dict:
        """クォータチェック"""
        subscription = await tenant.subscription
        plan_limits = self._get_plan_limits(subscription.plan_name)

        current_usage = await self._get_current_usage(tenant, resource)
        limit = plan_limits.get(resource, float('inf'))

        return {
            "resource": resource,
            "current": current_usage,
            "limit": limit,
            "percentage": (current_usage / limit * 100) if limit != float('inf') else 0,
            "available": max(0, limit - current_usage),
            "exceeded": current_usage > limit
        }

    async def increment_usage(
        self,
        tenant: Tenant,
        resource: str,
        amount: int = 1
    ):
        """使用量をインクリメント"""

        # 使用量記録
        await UsageRecord.create(
            tenant_id=tenant.id,
            resource=resource,
            amount=amount,
            timestamp=datetime.utcnow()
        )

        # クォータチェック
        quota_status = await self.check_quota(tenant, resource)

        # クォータ超過時の処理
        if quota_status["exceeded"]:
            await self._handle_quota_exceeded(tenant, resource, quota_status)

        # アラート閾値チェック (80%, 100%)
        elif quota_status["percentage"] >= 80:
            await self._send_quota_alert(tenant, resource, quota_status)

        # Stripeに使用量報告（従量課金の場合）
        if await self._is_metered_resource(resource):
            subscription = await tenant.subscription
            await self.stripe_service.record_usage(
                subscription,
                amount,
                action="increment"
            )

    async def _handle_quota_exceeded(
        self,
        tenant: Tenant,
        resource: str,
        quota_status: Dict
    ):
        """クォータ超過ハンドリング"""

        # オーバージャージ設定確認
        if tenant.allow_overage:
            # 従量課金として記録
            overage_amount = quota_status["current"] - quota_status["limit"]
            await self._record_overage_charge(tenant, resource, overage_amount)

            # 通知
            await self._send_overage_notification(tenant, resource, overage_amount)
        else:
            # 機能制限
            await self._apply_resource_restriction(tenant, resource)

            # 緊急通知
            await self._send_quota_exceeded_alert(tenant, resource)

    def _get_plan_limits(self, plan_name: str) -> Dict[str, int]:
        """プラン別のリソース上限"""
        return {
            "free": {
                "assessments": 1,
                "leads": 50,
                "ai_generations": 0
            },
            "starter": {
                "assessments": 5,
                "leads": 500,
                "ai_generations": 10
            },
            "professional": {
                "assessments": 20,
                "leads": 3000,
                "ai_generations": 50
            },
            "business": {
                "assessments": 100,
                "leads": 15000,
                "ai_generations": 200
            },
            "enterprise": {
                "assessments": float('inf'),
                "leads": float('inf'),
                "ai_generations": float('inf')
            }
        }.get(plan_name.lower(), {})
```

### Webhook Handler

```python
# backend/app/api/v1/webhooks/stripe.py
from fastapi import APIRouter, Request, HTTPException
from app.services.billing.webhook_handler import StripeWebhookHandler

router = APIRouter()
webhook_handler = StripeWebhookHandler()

@router.post("/stripe")
async def stripe_webhook(request: Request):
    """Stripe Webhookエンドポイント"""

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # イベントタイプ別処理
    await webhook_handler.handle_event(event)

    return {"status": "success"}


class StripeWebhookHandler:
    """Stripe Webhookハンドラー"""

    async def handle_event(self, event: dict):
        """イベント処理ルーティング"""

        handlers = {
            "customer.subscription.created": self._handle_subscription_created,
            "customer.subscription.updated": self._handle_subscription_updated,
            "customer.subscription.deleted": self._handle_subscription_deleted,
            "invoice.payment_succeeded": self._handle_payment_succeeded,
            "invoice.payment_failed": self._handle_payment_failed,
            "customer.subscription.trial_will_end": self._handle_trial_ending
        }

        handler = handlers.get(event["type"])
        if handler:
            await handler(event["data"]["object"])

    async def _handle_payment_failed(self, invoice: dict):
        """決済失敗処理"""

        customer_id = invoice["customer"]
        tenant = await Tenant.get_by_stripe_customer(customer_id)

        if not tenant:
            return

        # リトライカウント増加
        subscription = await tenant.subscription
        subscription.payment_retry_count += 1
        await subscription.save()

        # 通知送信
        await self._send_payment_failed_email(tenant, invoice)

        # 一定回数失敗したら制限モード
        if subscription.payment_retry_count >= 3:
            await self._apply_account_restrictions(tenant)
```

## API Endpoints

### サブスクリプション管理

```
GET    /api/v1/billing/plans
       - 利用可能なプラン一覧
       - Response: [{ id, name, price, features, limits }]

POST   /api/v1/billing/subscriptions
       - サブスクリプション作成
       - Request: { price_id, payment_method_id, coupon? }
       - Response: { subscription_id, client_secret, status }

GET    /api/v1/billing/subscriptions/current
       - 現在のサブスクリプション取得
       - Response: { plan, status, current_period_end, cancel_at_period_end }

PUT    /api/v1/billing/subscriptions/plan
       - プラン変更
       - Request: { new_price_id, prorate: true }
       - Response: { subscription_id, plan, effective_date }

DELETE /api/v1/billing/subscriptions
       - サブスクリプションキャンセル
       - Request: { at_period_end: true }
       - Response: { status, cancellation_date }

POST   /api/v1/billing/subscriptions/reactivate
       - キャンセル予定のサブスクリプションを再開
```

### 利用量管理

```
GET    /api/v1/billing/usage
       - 現在の利用状況
       - Response: {
           assessments: { current, limit, percentage },
           leads: { current, limit, percentage },
           ai_generations: { current, limit, percentage }
         }

GET    /api/v1/billing/usage/history
       - 利用履歴（日別・月別）
       - Query: ?period=monthly&year=2025
       - Response: [{ date, resource, amount }]

POST   /api/v1/billing/usage/reset
       - 使用量リセット（テスト用・管理者のみ）
```

### 請求書管理

```
GET    /api/v1/billing/invoices
       - 請求書一覧
       - Response: [{ id, date, amount, status, pdf_url }]

GET    /api/v1/billing/invoices/{invoice_id}
       - 請求書詳細
       - Response: { id, line_items, subtotal, tax, total }

GET    /api/v1/billing/invoices/{invoice_id}/pdf
       - 請求書PDF取得
       - Response: Binary PDF

POST   /api/v1/billing/invoices/{invoice_id}/send
       - 請求書再送信
```

### 支払い方法管理

```
GET    /api/v1/billing/payment-methods
       - 登録済み支払い方法一覧
       - Response: [{ id, type, last4, exp_month, exp_year, is_default }]

POST   /api/v1/billing/payment-methods
       - 支払い方法追加
       - Request: { payment_method_id }
       - Response: { id, status }

PUT    /api/v1/billing/payment-methods/{pm_id}/default
       - デフォルト支払い方法設定

DELETE /api/v1/billing/payment-methods/{pm_id}
       - 支払い方法削除
```

## Database Schema

```sql
-- サブスクリプション
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,

    -- Stripe連携
    stripe_subscription_id VARCHAR(255) UNIQUE NOT NULL,
    stripe_customer_id VARCHAR(255) NOT NULL,
    stripe_price_id VARCHAR(255) NOT NULL,

    -- プラン情報
    plan_name VARCHAR(50) NOT NULL,  -- free, starter, professional, business, enterprise
    status VARCHAR(50) NOT NULL,  -- active, trialing, past_due, canceled, unpaid

    -- 期間
    current_period_start TIMESTAMP NOT NULL,
    current_period_end TIMESTAMP NOT NULL,
    trial_start TIMESTAMP,
    trial_end TIMESTAMP,

    -- キャンセル
    cancel_at_period_end BOOLEAN DEFAULT FALSE,
    canceled_at TIMESTAMP,

    -- 決済失敗管理
    payment_retry_count INTEGER DEFAULT 0,
    last_payment_error TEXT,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(tenant_id)  -- 1テナント1サブスクリプション
);

-- 利用量記録
CREATE TABLE usage_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,

    resource VARCHAR(50) NOT NULL,  -- assessments, leads, ai_generations, api_calls
    amount INTEGER NOT NULL DEFAULT 1,

    -- メタデータ
    metadata JSONB,

    timestamp TIMESTAMP DEFAULT NOW(),

    INDEX idx_usage_tenant_resource (tenant_id, resource, timestamp),
    INDEX idx_usage_timestamp (timestamp)
);

-- 請求書（Stripeと同期）
CREATE TABLE invoices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,

    stripe_invoice_id VARCHAR(255) UNIQUE NOT NULL,

    -- 請求情報
    invoice_number VARCHAR(100) UNIQUE NOT NULL,  -- 適格請求書番号
    amount_due INTEGER NOT NULL,  -- 金額（円）
    amount_paid INTEGER DEFAULT 0,
    tax INTEGER DEFAULT 0,

    -- 期間
    period_start TIMESTAMP NOT NULL,
    period_end TIMESTAMP NOT NULL,

    -- ステータス
    status VARCHAR(50) NOT NULL,  -- draft, open, paid, void, uncollectible
    paid BOOLEAN DEFAULT FALSE,

    -- PDF
    pdf_url TEXT,

    -- 明細
    line_items JSONB,  -- [{ description, amount, quantity }]

    due_date TIMESTAMP,
    paid_at TIMESTAMP,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    INDEX idx_invoices_tenant (tenant_id),
    INDEX idx_invoices_status (status),
    INDEX idx_invoices_date (created_at)
);

-- クーポン使用履歴
CREATE TABLE coupon_redemptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,

    coupon_code VARCHAR(100) NOT NULL,
    stripe_coupon_id VARCHAR(255),

    discount_amount INTEGER,  -- 割引額
    discount_percentage DECIMAL(5,2),  -- 割引率

    redeemed_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP,

    INDEX idx_coupons_tenant (tenant_id)
);

-- テナントテーブルに追加カラム
ALTER TABLE tenants ADD COLUMN stripe_customer_id VARCHAR(255) UNIQUE;
ALTER TABLE tenants ADD COLUMN current_plan VARCHAR(50) DEFAULT 'free';
ALTER TABLE tenants ADD COLUMN allow_overage BOOLEAN DEFAULT FALSE;  -- 従量課金許可
ALTER TABLE tenants ADD COLUMN account_status VARCHAR(50) DEFAULT 'active';  -- active, restricted, suspended
```

## Frontend Components

### Pricing Page

```typescript
// frontend/src/features/billing/PricingPage.tsx
import { useState } from 'react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Check, Zap } from 'lucide-react'

const plans = [
  {
    name: 'Free',
    price: 0,
    priceId: null,
    features: ['診断1個', 'リード50件', '基本分析'],
    limits: { assessments: 1, leads: 50 }
  },
  {
    name: 'Starter',
    price: 29800,
    priceId: 'price_starter_monthly',
    features: ['診断5個', 'リード500件', 'AI生成', '高度な分析'],
    limits: { assessments: 5, leads: 500 },
    popular: true
  },
  {
    name: 'Professional',
    price: 98000,
    priceId: 'price_professional_monthly',
    features: ['診断20個', 'リード3,000件', 'Teams統合', 'A/Bテスト'],
    limits: { assessments: 20, leads: 3000 }
  }
]

export function PricingPage() {
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'yearly'>('monthly')

  const handleSelectPlan = async (priceId: string) => {
    const response = await fetch('/api/v1/billing/subscriptions', {
      method: 'POST',
      body: JSON.stringify({ price_id: priceId })
    })

    const { client_secret } = await response.json()

    // Stripe Checkoutにリダイレクト
    const stripe = await loadStripe(STRIPE_PUBLISHABLE_KEY)
    await stripe?.redirectToCheckout({ sessionId: client_secret })
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-16">
      <h1 className="text-4xl font-bold text-center mb-12">
        プランを選択
      </h1>

      <div className="grid md:grid-cols-3 gap-8">
        {plans.map((plan) => (
          <Card
            key={plan.name}
            className={plan.popular ? 'border-primary shadow-lg' : ''}
          >
            {plan.popular && (
              <div className="bg-primary text-white text-center py-2">
                <Zap className="inline mr-2" size={16} />
                人気プラン
              </div>
            )}

            <div className="p-6">
              <h3 className="text-2xl font-bold">{plan.name}</h3>
              <div className="mt-4">
                <span className="text-4xl font-bold">
                  ¥{plan.price.toLocaleString()}
                </span>
                <span className="text-muted-foreground">/月</span>
              </div>

              <ul className="mt-6 space-y-3">
                {plan.features.map((feature) => (
                  <li key={feature} className="flex items-center">
                    <Check className="mr-2 text-primary" size={20} />
                    {feature}
                  </li>
                ))}
              </ul>

              <Button
                className="w-full mt-8"
                variant={plan.popular ? 'default' : 'outline'}
                onClick={() => handleSelectPlan(plan.priceId)}
              >
                {plan.price === 0 ? '無料で始める' : '14日間無料トライアル'}
              </Button>
            </div>
          </Card>
        ))}
      </div>
    </div>
  )
}
```

### Usage Dashboard

```typescript
// frontend/src/features/billing/UsageDashboard.tsx
import { useQuery } from '@tanstack/react-query'
import { Progress } from '@/components/ui/progress'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { AlertTriangle } from 'lucide-react'

export function UsageDashboard() {
  const { data: usage } = useQuery({
    queryKey: ['billing', 'usage'],
    queryFn: () => fetch('/api/v1/billing/usage').then(r => r.json())
  })

  const getProgressColor = (percentage: number) => {
    if (percentage >= 100) return 'bg-red-500'
    if (percentage >= 80) return 'bg-yellow-500'
    return 'bg-green-500'
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">利用状況</h2>

      {usage?.assessments.percentage >= 80 && (
        <Alert variant="warning">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            診断数がクォータの{usage.assessments.percentage}%に達しています。
            <a href="/billing/upgrade" className="underline ml-2">
              プランをアップグレード
            </a>
          </AlertDescription>
        </Alert>
      )}

      <div className="grid gap-6">
        {Object.entries(usage || {}).map(([resource, data]) => (
          <Card key={resource}>
            <CardHeader>
              <CardTitle className="flex justify-between">
                <span>{resourceLabels[resource]}</span>
                <span>{data.current} / {data.limit}</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Progress
                value={data.percentage}
                className={getProgressColor(data.percentage)}
              />
              <p className="text-sm text-muted-foreground mt-2">
                残り: {data.available}
              </p>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
```

## Security Considerations

- **Stripe Webhook署名検証**: すべてのWebhookリクエストを検証
- **PCI DSS準拠**: カード情報は一切サーバーに保存しない（Stripeに委譲）
- **API鍵管理**: Stripe APIキーは環境変数で管理、暗号化
- **テナント分離**: 請求情報は必ずテナントIDでフィルタリング
- **監査ログ**: すべての請求イベントを記録
- **HTTPS必須**: すべての決済関連通信はHTTPSのみ

## Testing Strategy

### 単体テスト
- プラン変更ロジック
- 日割り計算
- クォータチェック
- 使用量集計

### 統合テスト
- Stripe API呼び出し（テストモード使用）
- Webhook処理
- 決済フロー

### E2Eテスト
- プラン登録 → トライアル → 有料移行
- プラン変更（アップグレード・ダウングレード）
- 決済失敗 → リトライ → 制限モード
- クォータ超過 → 従量課金

## Performance Requirements

- **Webhookレスポンス**: 200ms以内
- **使用量チェック**: 50ms以内（キャッシュ活用）
- **請求書生成**: 3秒以内
- **プラン変更反映**: 即時（5秒以内）

## Rollout Plan

### Week 1-2: Stripe統合基盤
- Stripe Account設定
- Customer・Subscription作成API
- Webhook受信基盤

### Week 3-4: プラン管理
- プラン定義・価格設定
- サブスクリプション作成フロー
- チェックアウトページ

### Week 5-6: 利用量トラッキング
- 使用量記録システム
- クォータチェック
- アラート通知

### Week 7-8: 請求書・支払い管理
- 請求書生成・PDF出力
- 決済失敗ハンドリング
- 支払い方法管理

### Week 9-10: テスト・最適化
- E2Eテスト
- パフォーマンス最適化
- ドキュメント作成

## Success Metrics

- **課金開始率**: トライアルユーザーの40%が有料プランに移行
- **MRR成長率**: 月次+15%
- **解約率**: 月次3%以下
- **決済成功率**: 98%以上
- **アップグレード率**: 四半期あたり20%
- **平均顧客単価（ARPU）**: ¥50,000/月

## Related Specifications

- [Analytics Dashboard](./analytics-dashboard.md) - 収益分析ダッシュボード
- [White Label Branding](./white-label-branding.md) - Enterpriseプラン機能
- [Multi-Tenant Architecture](../auth/multi-tenant.md) - テナント分離
- [Integrations](./integrations.md) - 会計システム連携

## References

- [Stripe API Documentation](https://stripe.com/docs/api)
- [Stripe Billing Best Practices](https://stripe.com/docs/billing/subscriptions/overview)
- [SaaS Metrics Guide](https://www.forentrepreneurs.com/saas-metrics-2/)
- [PCI DSS Compliance](https://www.pcisecuritystandards.org/)
