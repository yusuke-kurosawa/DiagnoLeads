# Google Analytics 4 Integration - Implementation Guide

## 概要

このガイドは、DiagnoLeadsプラットフォームへのGoogle Analytics 4（GA4）統合の実装手順を説明します。

## アーキテクチャ概要

```
┌─────────────────────────────────────────────────────────────────┐
│                    DiagnoLeads Platform                         │
│                                                                 │
│  ┌──────────────┐        ┌──────────────┐      ┌─────────────┐│
│  │   React      │        │   Embed      │      │   Backend   ││
│  │   Admin      │───────▶│   Widget     │◀─────│   (FastAPI) ││
│  │   (gtag.js)  │        │   (gtag.js)  │      │   (MP API)  ││
│  └──────┬───────┘        └──────┬───────┘      └──────┬──────┘│
│         │                       │                     │        │
│         │                       │                     │        │
└─────────┼───────────────────────┼─────────────────────┼────────┘
          │                       │                     │
          │                       │                     │
          ▼                       ▼                     ▼
    ┌─────────────────────────────────────────────────────┐
    │         Google Analytics 4 (GA4)                    │
    │                                                     │
    │  ┌──────────────┐  ┌──────────────┐  ┌──────────┐ │
    │  │  gtag.js     │  │  gtag.js     │  │ Measure- │ │
    │  │  (Frontend)  │  │  (Embed)     │  │ ment     │ │
    │  │  Events      │  │  Events      │  │ Protocol │ │
    │  └──────────────┘  └──────────────┘  └──────────┘ │
    │                                                     │
    │       ┌─────────────────────────┐                  │
    │       │  GA4 Property           │                  │
    │       │  (Per Tenant)           │                  │
    │       │  - Events               │                  │
    │       │  - User Properties      │                  │
    │       │  - Conversions          │                  │
    │       └─────────────────────────┘                  │
    └─────────────────────────────────────────────────────┘
```

## 実装フロー

### 1. データベーススキーマ

**マイグレーションファイル:** `alembic/versions/xxxx_add_google_analytics_integration.py`

```python
"""Add Google Analytics integration table

Revision ID: xxxx
Revises: yyyy
Create Date: 2025-11-18
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    op.create_table(
        'google_analytics_integrations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('measurement_id', sa.String(length=20), nullable=False),
        sa.Column('measurement_protocol_api_secret', sa.String(length=255), nullable=True),
        sa.Column('enabled', sa.Boolean(), default=True),
        sa.Column('track_frontend', sa.Boolean(), default=True),
        sa.Column('track_embed_widget', sa.Boolean(), default=True),
        sa.Column('track_server_events', sa.Boolean(), default=False),
        sa.Column('custom_dimensions', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('tenant_id', name='uq_ga_integration_tenant')
    )

    # Indexes
    op.create_index('ix_ga_integration_tenant_id', 'google_analytics_integrations', ['tenant_id'])
    op.create_index('ix_ga_integration_enabled', 'google_analytics_integrations', ['enabled'])

    # Row-Level Security
    op.execute("""
        ALTER TABLE google_analytics_integrations ENABLE ROW LEVEL SECURITY;

        CREATE POLICY tenant_isolation_policy ON google_analytics_integrations
            USING (tenant_id = current_setting('app.current_tenant_id')::uuid);
    """)

def downgrade():
    op.drop_table('google_analytics_integrations')
```

### 2. バックエンド実装

#### モデル定義

**File:** `backend/app/models/google_analytics_integration.py`

```python
"""Google Analytics Integration Model"""
from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from app.db.base_class import Base

class GoogleAnalyticsIntegration(Base):
    __tablename__ = "google_analytics_integrations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    measurement_id = Column(String(20), nullable=False)  # G-XXXXXXXXXX
    measurement_protocol_api_secret = Column(String(255), nullable=True)  # Encrypted
    enabled = Column(Boolean, default=True)
    track_frontend = Column(Boolean, default=True)
    track_embed_widget = Column(Boolean, default=True)
    track_server_events = Column(Boolean, default=False)
    custom_dimensions = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), onupdate=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant", back_populates="google_analytics_integration")
```

#### API エンドポイント

**File:** `backend/app/api/v1/google_analytics.py`

```python
"""Google Analytics Integration API"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.services.google_analytics_service import GoogleAnalyticsService
from app.schemas.google_analytics import (
    GoogleAnalyticsIntegrationCreate,
    GoogleAnalyticsIntegrationUpdate,
    GoogleAnalyticsIntegrationResponse
)

router = APIRouter()

@router.put("/tenants/{tenant_id}/integrations/google-analytics")
async def create_or_update_ga_integration(
    tenant_id: UUID,
    data: GoogleAnalyticsIntegrationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create or update Google Analytics integration"""
    # Check tenant access
    if current_user.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    service = GoogleAnalyticsService(db)
    integration = await service.create_or_update(tenant_id, data)
    return integration

@router.get("/tenants/{tenant_id}/integrations/google-analytics")
async def get_ga_integration(
    tenant_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get Google Analytics integration settings"""
    if current_user.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    service = GoogleAnalyticsService(db)
    integration = await service.get_by_tenant(tenant_id)
    if not integration:
        raise HTTPException(status_code=404, detail="GA integration not found")
    return integration

@router.post("/tenants/{tenant_id}/integrations/google-analytics/test")
async def test_ga_connection(
    tenant_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Test Google Analytics connection"""
    if current_user.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    service = GoogleAnalyticsService(db)
    result = await service.test_connection(tenant_id)
    return result
```

#### Measurement Protocol クライアント

**File:** `backend/app/integrations/google_analytics/measurement_protocol.py`

```python
"""Google Analytics 4 Measurement Protocol Client"""
import httpx
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class GA4MeasurementProtocol:
    """GA4 Measurement Protocol API Client"""

    ENDPOINT = "https://www.google-analytics.com/mp/collect"
    DEBUG_ENDPOINT = "https://www.google-analytics.com/debug/mp/collect"

    def __init__(self, measurement_id: str, api_secret: str, debug: bool = False):
        self.measurement_id = measurement_id
        self.api_secret = api_secret
        self.endpoint = self.DEBUG_ENDPOINT if debug else self.ENDPOINT

    async def send_event(
        self,
        client_id: str,
        event_name: str,
        event_params: Dict,
        user_properties: Optional[Dict] = None
    ) -> bool:
        """Send event to GA4"""
        url = f"{self.endpoint}?measurement_id={self.measurement_id}&api_secret={self.api_secret}"

        payload = {
            "client_id": client_id,
            "events": [{
                "name": event_name,
                "params": event_params
            }]
        }

        if user_properties:
            payload["user_properties"] = user_properties

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()

                logger.info(f"GA4 event sent: {event_name}, client_id: {client_id}")
                return True

        except httpx.HTTPError as e:
            logger.error(f"GA4 event send failed: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending GA4 event: {str(e)}")
            return False

    async def send_batch_events(
        self,
        client_id: str,
        events: list[Dict]
    ) -> bool:
        """Send multiple events in a single request"""
        url = f"{self.endpoint}?measurement_id={self.measurement_id}&api_secret={self.api_secret}"

        payload = {
            "client_id": client_id,
            "events": events
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()

                logger.info(f"GA4 batch events sent: {len(events)} events")
                return True

        except Exception as e:
            logger.error(f"GA4 batch events send failed: {str(e)}")
            return False
```

### 3. フロントエンド実装（React）

#### GA4フック

**File:** `frontend/src/hooks/useGoogleAnalytics.ts`

```typescript
import { useEffect } from 'react';
import ReactGA from 'react-ga4';
import { useAuthStore } from '@/store/authStore';
import { tenantService } from '@/services/tenantService';

export const useGoogleAnalytics = () => {
  const { user } = useAuthStore();

  useEffect(() => {
    const initGA = async () => {
      if (!user?.tenant_id) return;

      try {
        // Fetch GA configuration from backend
        const gaConfig = await tenantService.getGoogleAnalyticsConfig(user.tenant_id);

        if (gaConfig.enabled && gaConfig.track_frontend && gaConfig.measurement_id) {
          // Initialize GA4
          ReactGA.initialize(gaConfig.measurement_id, {
            gaOptions: {
              send_page_view: false // Manual page view tracking
            }
          });

          // Set user properties
          ReactGA.set({
            tenant_id: user.tenant_id,
            user_id: user.id,
          });

          console.log('Google Analytics initialized:', gaConfig.measurement_id);
        }
      } catch (error) {
        console.error('Failed to initialize Google Analytics:', error);
      }
    };

    initGA();
  }, [user]);

  const trackPageView = (path: string, title?: string) => {
    ReactGA.send({
      hitType: 'pageview',
      page: path,
      title: title || document.title,
    });
  };

  const trackEvent = (eventName: string, params: Record<string, any> = {}) => {
    ReactGA.event(eventName, {
      ...params,
      tenant_id: user?.tenant_id,
    });
  };

  return { trackPageView, trackEvent };
};
```

#### ルーター統合

**File:** `frontend/src/App.tsx`

```typescript
import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { useGoogleAnalytics } from '@/hooks/useGoogleAnalytics';

function App() {
  const location = useLocation();
  const { trackPageView } = useGoogleAnalytics();

  useEffect(() => {
    trackPageView(location.pathname);
  }, [location, trackPageView]);

  return (
    // ... rest of the app
  );
}
```

#### イベント送信例

**File:** `frontend/src/pages/assessments/CreateAssessmentPage.tsx`

```typescript
const handleCreateAssessment = async (data: AssessmentData) => {
  try {
    const assessment = await assessmentService.create(data);

    // Track GA4 event
    trackEvent('assessment_created', {
      assessment_id: assessment.id,
      assessment_title: assessment.title,
      creation_method: data.ai_generated ? 'ai_generated' : 'manual',
    });

    navigate(`/assessments/${assessment.id}`);
  } catch (error) {
    // ...
  }
};
```

### 4. 埋め込みウィジェット実装

**File:** `embed/src/utils/analytics.ts`

```typescript
interface GA4Config {
  measurement_id: string;
  enabled: boolean;
}

export class EmbedAnalytics {
  private measurementId: string | null = null;
  private initialized: boolean = false;

  async init(assessmentId: string) {
    try {
      // Fetch GA config from public API
      const response = await fetch(
        `${API_BASE_URL}/public/assessments/${assessmentId}/google-analytics-config`
      );

      if (!response.ok) return;

      const config: GA4Config = await response.json();

      if (config.enabled && config.measurement_id) {
        this.measurementId = config.measurement_id;
        this.loadGtagScript();
      }
    } catch (error) {
      console.error('Failed to initialize GA4:', error);
    }
  }

  private loadGtagScript() {
    if (this.initialized || !this.measurementId) return;

    // Load gtag.js
    const script = document.createElement('script');
    script.src = `https://www.googletagmanager.com/gtag/js?id=${this.measurementId}`;
    script.async = true;
    document.head.appendChild(script);

    // Initialize gtag
    window.dataLayer = window.dataLayer || [];
    function gtag(...args: any[]) {
      window.dataLayer.push(arguments);
    }
    gtag('js', new Date());
    gtag('config', this.measurementId, {
      send_page_view: false,
      page_location: window.location.href,
      page_referrer: document.referrer,
    });

    this.initialized = true;
  }

  trackEvent(eventName: string, params: Record<string, any> = {}) {
    if (!this.initialized || !window.gtag) return;

    window.gtag('event', eventName, {
      ...params,
      page_location: window.location.href,
    });
  }

  // Convenience methods
  trackAssessmentView(assessmentId: string, assessmentTitle: string) {
    this.trackEvent('assessment_view', {
      assessment_id: assessmentId,
      assessment_title: assessmentTitle,
    });
  }

  trackAssessmentStarted(assessmentId: string, totalQuestions: number) {
    this.trackEvent('assessment_started', {
      assessment_id: assessmentId,
      total_questions: totalQuestions,
    });
  }

  trackQuestionAnswered(
    assessmentId: string,
    questionNumber: number,
    questionId: string,
    timeSpent: number
  ) {
    this.trackEvent('question_answered', {
      assessment_id: assessmentId,
      question_number: questionNumber,
      question_id: questionId,
      time_spent_seconds: timeSpent,
    });
  }

  trackAssessmentCompleted(
    assessmentId: string,
    totalTime: number,
    questionsAnswered: number
  ) {
    this.trackEvent('assessment_completed', {
      assessment_id: assessmentId,
      total_time_seconds: totalTime,
      questions_answered: questionsAnswered,
    });
  }

  trackLeadGenerated(
    assessmentId: string,
    leadScore: number,
    leadTier: 'hot' | 'warm' | 'cold'
  ) {
    this.trackEvent('lead_generated', {
      assessment_id: assessmentId,
      lead_score: leadScore,
      lead_tier: leadTier,
    });

    // If hot lead, track conversion event
    if (leadTier === 'hot') {
      this.trackEvent('hot_lead_generated', {
        assessment_id: assessmentId,
        lead_score: leadScore,
        value: 1000, // Estimated lead value
        currency: 'JPY',
      });
    }
  }
}

export const embedAnalytics = new EmbedAnalytics();
```

### 5. テナント設定画面

**File:** `frontend/src/pages/settings/IntegrationsPage.tsx`

```typescript
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useToast } from '@/contexts/ToastContext';

interface GAIntegrationForm {
  measurement_id: string;
  measurement_protocol_api_secret?: string;
  enabled: boolean;
  track_frontend: boolean;
  track_embed_widget: boolean;
  track_server_events: boolean;
}

export const IntegrationsPage = () => {
  const { register, handleSubmit, formState: { errors } } = useForm<GAIntegrationForm>();
  const { showToast } = useToast();
  const [testing, setTesting] = useState(false);

  const onSubmit = async (data: GAIntegrationForm) => {
    try {
      await gaIntegrationService.createOrUpdate(tenantId, data);
      showToast('Google Analytics settings saved successfully', 'success');
    } catch (error) {
      showToast('Failed to save settings', 'error');
    }
  };

  const handleTestConnection = async () => {
    setTesting(true);
    try {
      const result = await gaIntegrationService.testConnection(tenantId);
      if (result.status === 'success') {
        showToast('Connection test successful! Check GA4 Realtime Report.', 'success');
      } else {
        showToast(`Connection test failed: ${result.message}`, 'error');
      }
    } catch (error) {
      showToast('Failed to test connection', 'error');
    } finally {
      setTesting(false);
    }
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Google Analytics Integration</h2>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div>
          <label>Measurement ID</label>
          <Input
            {...register('measurement_id', {
              required: 'Measurement ID is required',
              pattern: {
                value: /^G-[A-Z0-9]{10}$/,
                message: 'Invalid format. Should be G-XXXXXXXXXX',
              },
            })}
            placeholder="G-XXXXXXXXXX"
          />
          {errors.measurement_id && (
            <p className="text-red-500 text-sm">{errors.measurement_id.message}</p>
          )}
        </div>

        <div>
          <label>
            <input type="checkbox" {...register('track_frontend')} />
            Track admin dashboard events
          </label>
        </div>

        <div>
          <label>
            <input type="checkbox" {...register('track_embed_widget')} />
            Track embed widget events
          </label>
        </div>

        <div className="flex gap-4">
          <Button type="submit">Save Settings</Button>
          <Button type="button" onClick={handleTestConnection} disabled={testing}>
            {testing ? 'Testing...' : 'Test Connection'}
          </Button>
        </div>
      </form>
    </div>
  );
};
```

## テストガイド

### 1. ユニットテスト

```python
# backend/tests/test_google_analytics.py
import pytest
from app.integrations.google_analytics.measurement_protocol import GA4MeasurementProtocol

@pytest.mark.asyncio
async def test_send_event():
    client = GA4MeasurementProtocol(
        measurement_id="G-TEST123456",
        api_secret="test_secret",
        debug=True
    )

    result = await client.send_event(
        client_id="test-client-123",
        event_name="test_event",
        event_params={"test_param": "test_value"}
    )

    assert result is True
```

### 2. E2Eテスト

```typescript
// frontend/src/__tests__/e2e/analytics.test.ts
describe('Google Analytics Integration', () => {
  it('should send assessment_created event', async () => {
    // Create assessment
    await createAssessment({ title: 'Test Assessment' });

    // Verify GA4 event was sent
    expect(window.gtag).toHaveBeenCalledWith('event', 'assessment_created', {
      assessment_title: 'Test Assessment',
      creation_method: 'manual',
      tenant_id: expect.any(String),
    });
  });
});
```

### 3. GA4での確認

1. **リアルタイムレポート**
   - GA4管理画面 → Reports → Realtime
   - イベント名でフィルタリング

2. **デバッグビュー**
   - GA4管理画面 → Configure → DebugView
   - chrome拡張「Google Analytics Debugger」を使用

3. **イベント設定**
   - GA4管理画面 → Configure → Events
   - カスタムイベントが表示されることを確認

## デプロイチェックリスト

- [ ] データベースマイグレーション実行
- [ ] 環境変数設定（API Secret暗号化キー）
- [ ] バックエンドAPIデプロイ
- [ ] フロントエンドビルド＆デプロイ
- [ ] 埋め込みウィジェットビルド＆デプロイ
- [ ] GA4プロパティ作成（テスト用）
- [ ] 接続テスト実行
- [ ] リアルタイムレポートで確認
- [ ] プライバシーポリシー更新
- [ ] ユーザーガイド作成

## トラブルシューティング

### イベントがGA4に表示されない

1. **Measurement IDの確認**
   - 正しいフォーマット（G-XXXXXXXXXX）か確認
   - GA4プロパティが有効か確認

2. **API Secretの確認**
   - 正しいAPI Secretを設定しているか
   - 暗号化が正しく行われているか

3. **リアルタイムレポート**
   - 24時間以内のイベントのみ表示される
   - デバッグモードで詳細確認

### クロスドメイントラッキングが動作しない

1. **linkerパラメータ設定**
   - gtag config で linker を設定
   - 埋め込み元ドメインを許可リストに追加

2. **Cookie設定**
   - サードパーティCookieがブロックされていないか
   - Same-Site属性の確認

## 参考リンク

- [GA4 Measurement Protocol](https://developers.google.com/analytics/devguides/collection/protocol/ga4)
- [react-ga4 GitHub](https://github.com/codler/react-ga4)
- [GA4 Events Reference](https://support.google.com/analytics/answer/9267735)

---

**Last Updated:** 2025-11-18
**Version:** 1.0
