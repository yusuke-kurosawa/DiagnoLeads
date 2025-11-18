# Google Analytics 4 Tracking Examples

## Overview

このドキュメントでは、DiagnoLeadsのReact管理画面でGA4イベントを追跡する実装例を示します。

## Basic Usage

### 1. Page View Tracking (Automatic)

ページビューは`GATracker`コンポーネントによって自動的に追跡されます。特別な実装は不要です。

```tsx
// App.tsx で既に設定済み
<Router>
  <GATracker /> {/* 自動的にルート変更を追跡 */}
  <Routes>
    {/* ... */}
  </Routes>
</Router>
```

### 2. Custom Event Tracking in Components

#### Example 1: 診断作成イベント

```tsx
// CreateAssessmentPage.tsx
import { useTrackAssessmentEvents } from '../../hooks/useGoogleAnalytics';

export function CreateAssessmentPage() {
  const { tenantId } = useParams();
  const { trackAssessmentCreated } = useTrackAssessmentEvents();

  const handleCreateAssessment = async (data: AssessmentData) => {
    try {
      const assessment = await assessmentService.create(tenantId, data);

      // Track GA4 event
      trackAssessmentCreated(
        assessment.id,
        assessment.title,
        data.ai_generated ? 'ai' : 'manual'
      );

      navigate(`/tenants/${tenantId}/assessments/${assessment.id}`);
    } catch (error) {
      console.error('Failed to create assessment:', error);
    }
  };

  return (
    <div>
      <AssessmentForm onSubmit={handleCreateAssessment} />
    </div>
  );
}
```

#### Example 2: リードステータス変更イベント

```tsx
// LeadDetailPage.tsx
import { useTrackLeadEvents } from '../../hooks/useGoogleAnalytics';

export function LeadDetailPage() {
  const { leadId } = useParams();
  const { trackLeadStatusChanged } = useTrackLeadEvents();

  const handleStatusChange = async (newStatus: string) => {
    try {
      const oldStatus = lead.status;

      await leadService.updateStatus(leadId, newStatus);

      // Track GA4 event
      trackLeadStatusChanged(leadId, oldStatus, newStatus);

      // Update UI
      setLead({ ...lead, status: newStatus });
    } catch (error) {
      console.error('Failed to update status:', error);
    }
  };

  return (
    <div>
      <StatusDropdown value={lead.status} onChange={handleStatusChange} />
    </div>
  );
}
```

#### Example 3: ダッシュボード表示イベント

```tsx
// Dashboard.tsx
import { useEffect } from 'react';
import { useTrackDashboardEvents } from '../hooks/useGoogleAnalytics';

export function Dashboard() {
  const { trackDashboardViewed } = useTrackDashboardEvents();

  useEffect(() => {
    // Track dashboard view on mount
    trackDashboardViewed('overview');
  }, [trackDashboardViewed]);

  return (
    <div>
      {/* Dashboard content */}
    </div>
  );
}
```

### 3. Custom Events with useGoogleAnalytics Hook

低レベルAPIを使用したカスタムイベント追跡：

```tsx
import { useGoogleAnalytics } from '../hooks/useGoogleAnalytics';

export function MyComponent() {
  const { trackEvent } = useGoogleAnalytics();

  const handleButtonClick = () => {
    trackEvent('button_clicked', {
      button_name: 'export_data',
      page: 'analytics',
      format: 'csv',
    });

    // Actual button action
    exportData();
  };

  return <button onClick={handleButtonClick}>Export Data</button>;
}
```

## Event Taxonomy

### Standard Events

| Event Name | When to Track | Parameters |
|-----------|---------------|-----------|
| `assessment_created` | 診断作成時 | assessment_id, assessment_title, creation_method |
| `assessment_published` | 診断公開時 | assessment_id |
| `assessment_deleted` | 診断削除時 | assessment_id |
| `lead_status_changed` | リードステータス変更時 | lead_id, old_status, new_status |
| `lead_viewed` | リード詳細表示時 | lead_id, lead_score |
| `dashboard_viewed` | ダッシュボード表示時 | view_type |

### Custom Event Parameters

すべてのイベントに自動的に追加されるパラメータ：
- `tenant_id`: テナントID
- `timestamp`: イベント発生時刻（ISO 8601形式）

## Cookie Consent

### How It Works

1. ユーザーが初めて訪問すると、Cookie同意バナーが表示されます
2. ユーザーが「同意する」をクリックすると、GA4トラッキングが有効化されます
3. ユーザーが「拒否」をクリックすると、GA4トラッキングは無効のままです
4. 選択はlocalStorageに保存され、次回訪問時には表示されません

### Reset Consent (for testing)

```tsx
import { resetCookieConsent } from '../components/analytics/CookieConsent';

// 開発中に同意をリセット
resetCookieConsent();
window.location.reload();
```

### Check Consent Status

```tsx
import { hasCookieConsent } from '../components/analytics/CookieConsent';

if (hasCookieConsent()) {
  console.log('User has given cookie consent');
} else {
  console.log('User has not given cookie consent');
}
```

## GA4 Configuration Check

GA4が正しく設定されているか確認するには：

1. **設定ページで確認**
   - 設定 → 外部連携 → Google Analytics 4 統合
   - Measurement IDが設定されているか
   - 「管理画面のトラッキング」が有効か

2. **ブラウザコンソールで確認**
   ```javascript
   // GA4 initialized successfully の メッセージを確認
   // イベント送信時に "GA4: Event tracked - ..." が表示される
   ```

3. **GA4 Realtime Reportで確認**
   - [Google Analytics](https://analytics.google.com/)
   - Reports → Realtime
   - 過去30分のイベントが表示される

## Debugging

### Enable Debug Mode

デバッグモードは開発環境で自動的に有効化されます：

```tsx
// useGoogleAnalytics.ts
ReactGA.initialize(config.measurement_id, {
  gtagOptions: {
    debug_mode: import.meta.env.DEV, // 開発環境でtrue
  },
});
```

### Console Logging

すべてのGA4イベントはコンソールにログ出力されます：

```
GA4: Initialized with Measurement ID: G-ABC1234567
GA4: Page view tracked - /tenants/123/assessments
GA4: Event tracked - assessment_created { assessment_id: '...', ... }
```

### GA4 DebugView

GA4の公式デバッグツールを使用：

1. GA4管理画面 → Configure → DebugView
2. ブラウザでイベントを発生させる
3. DebugViewでリアルタイムにイベントを確認

## Best Practices

### 1. イベント名は明確に

```tsx
// Good
trackEvent('assessment_created', { ... });
trackEvent('lead_status_changed', { ... });

// Bad
trackEvent('create', { ... });
trackEvent('update', { ... });
```

### 2. 必要最小限のパラメータ

```tsx
// Good
trackEvent('button_clicked', {
  button_name: 'export',
  format: 'csv',
});

// Bad - Too much data
trackEvent('button_clicked', {
  button_name: 'export',
  user_email: 'user@example.com', // PII - ダメ！
  user_ip: '192.168.1.1', // PII - ダメ！
  entire_lead_object: {...}, // 大きすぎ
});
```

### 3. PII (Personal Identifiable Information) を送信しない

**絶対に送信しないデータ:**
- メールアドレス
- 電話番号
- 氏名
- IPアドレス
- その他の個人を特定できる情報

**代わりに:**
- UUID（匿名化されたID）
- スコア、カテゴリー、タグなどの集計可能なデータ

```tsx
// Good
trackEvent('lead_generated', {
  lead_id: 'uuid-1234', // OK - 匿名化されたID
  lead_score: 85, // OK - 集計可能
  lead_tier: 'hot', // OK - カテゴリー
});

// Bad
trackEvent('lead_generated', {
  email: 'user@example.com', // ダメ！
  phone: '090-1234-5678', // ダメ！
  name: '山田太郎', // ダメ！
});
```

### 4. エラーハンドリング

```tsx
const handleAction = async () => {
  try {
    await performAction();

    // 成功時のみイベント送信
    trackEvent('action_completed', { ... });
  } catch (error) {
    // エラーイベントも追跡（任意）
    trackEvent('action_failed', {
      error_type: error.name,
      // エラーメッセージに個人情報が含まれないよう注意
    });
  }
};
```

## Testing Checklist

Phase 3実装後の確認項目：

- [ ] Cookie同意バナーが初回訪問時に表示される
- [ ] 「同意する」をクリックするとGA4が初期化される
- [ ] ページビューが自動的に追跡される
- [ ] カスタムイベントがGA4に送信される
- [ ] GA4 Realtimeレポートでイベントが確認できる
- [ ] ブラウザコンソールにGA4ログが表示される
- [ ] PII（個人情報）が送信されていないことを確認
- [ ] エラーが発生してもアプリが正常動作する

## Troubleshooting

### イベントがGA4に表示されない

1. **設定を確認**
   - 設定 → 外部連携でMeasurement IDが正しいか
   - 「管理画面のトラッキング」が有効か

2. **Cookie同意を確認**
   - Cookie同意バナーで「同意する」をクリックしたか
   - localStorageに `diagnoleads_cookie_consent=accepted` があるか

3. **ブラウザコンソールを確認**
   - `GA4: Initialized with Measurement ID: ...` が表示されるか
   - エラーメッセージがないか

4. **GA4設定を確認**
   - Measurement IDが正しいか（G-XXXXXXXXXX形式）
   - Data Streamが有効か

### Cookie同意バナーが表示されない

```tsx
// localStorageをクリア
import { resetCookieConsent } from '../components/analytics/CookieConsent';
resetCookieConsent();
window.location.reload();
```

### GA4が初期化されない

1. ログインしているか確認（tenant_idが必要）
2. バックエンドAPIが起動しているか確認
3. GA4統合が設定されているか確認（404エラーの場合は未設定）

---

**Last Updated:** 2025-11-18
**Version:** Phase 3
