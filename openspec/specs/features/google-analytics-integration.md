# Feature: Google Analytics 4 (GA4) Integration

**Status**: ✅ Implemented
**Created**: 2025-11-18
**Implemented**: 2025-11-18
**Priority**: High
**Complexity**: Medium
**Effort**: 6 weeks (Completed)

## Overview

DiagnoLeadsプラットフォームとGoogle Analytics 4を統合し、診断体験の完全なユーザー行動追跡、ファネル分析、ROI測定を実現します。マルチテナント対応で、各テナントが独自のGA4プロパティを使用できます。

### Business Value

- **診断ファネルの可視化**: 開始→質問回答→完了→リード化の各ステップの離脱率を把握
- **ROI測定**: マーケティングチャネル別の診断完了率、リード獲得コスト（CPA）を計測
- **顧客行動理解**: 質問ごとの平均回答時間、離脱ポイント、再訪問率を分析
- **A/Bテストの基盤**: GA4イベントデータを活用した診断最適化の意思決定
- **既存GA環境との統合**: 企業サイトの既存GA4プロパティと診断データを統合分析

## User Stories

### US-GA-001: テナント管理者としてGA4を設定したい
```
As a テナント管理者
I want to 設定画面でGA4 Measurement IDを登録できる
So that 診断ウィジェットと管理画面のデータを自社のGA4プロパティに送信できる
```

**Acceptance Criteria:**
- テナント設定画面に「Google Analytics」セクションがある
- GA4 Measurement ID（G-XXXXXXXXXX形式）を入力・保存できる
- 接続テスト機能で正常にイベントが送信されることを確認できる
- 複数のGA4プロパティ（本番環境用、テスト環境用など）を切り替え可能

### US-GA-002: マーケターとして診断ファネルをGA4で見たい
```
As a マーケティング担当者
I want to GA4で診断のファネルレポートを見る
So that 各ステップの離脱率を把握し、診断を改善できる
```

**Acceptance Criteria:**
- 以下のイベントがGA4に送信される:
  - `assessment_view` (診断ページ表示)
  - `assessment_started` (診断開始)
  - `question_answered` (質問回答)
  - `assessment_completed` (診断完了)
  - `lead_generated` (リード情報入力完了)
- GA4の「ファネルデータ探索」で上記イベントを使ったファネルを作成できる
- カスタムパラメータ（assessment_id, question_number, tenant_idなど）が送信される

### US-GA-003: 埋め込みウィジェットでユーザー行動を追跡したい
```
As a テナント管理者
I want to 外部サイトに埋め込んだ診断ウィジェットのユーザー行動を追跡
So that どのページが最もコンバージョンが高いかを把握できる
```

**Acceptance Criteria:**
- 埋め込みウィジェットがテナントのGA4プロパティにイベントを送信する
- `page_location` パラメータで埋め込み元のURLが記録される
- クロスドメイントラッキングが正しく動作する（referrerが保持される）
- プライバシー設定（Cookie同意）に準拠したトラッキング

### US-GA-004: ホットリード獲得を即座にGA4で計測したい
```
As a 営業責任者
I want to スコア80点以上のホットリードが獲得された瞬間にGA4でコンバージョン計測
So that リアルタイムで営業チームに通知し、広告ROIを正確に測定できる
```

**Acceptance Criteria:**
- `hot_lead_generated` イベントがリアルタイムでGA4に送信される
- イベントパラメータに `lead_score`, `company_name`, `assessment_id` が含まれる
- GA4のコンバージョン設定で「ホットリード獲得」として計測可能
- サーバーサイド（Measurement Protocol）とクライアントサイドの両方から送信（冗長性確保）

## Functional Requirements

### FR-GA-001: マルチテナントGA4設定管理

**Description:**
各テナントが独自のGA4 Measurement IDを設定・管理できるバックエンドAPI

**API Endpoints:**
```
PUT /api/v1/tenants/{tenant_id}/integrations/google-analytics
GET /api/v1/tenants/{tenant_id}/integrations/google-analytics
DELETE /api/v1/tenants/{tenant_id}/integrations/google-analytics
POST /api/v1/tenants/{tenant_id}/integrations/google-analytics/test
```

**Data Model:**
```python
class GoogleAnalyticsIntegration(Base):
    __tablename__ = "google_analytics_integrations"

    id: UUID
    tenant_id: UUID  # 必須、テナント分離
    measurement_id: str  # G-XXXXXXXXXX形式
    measurement_protocol_api_secret: str | None  # サーバーサイド用（暗号化保存）
    enabled: bool  # トラッキング有効/無効
    track_frontend: bool  # React管理画面のトラッキング
    track_embed_widget: bool  # 埋め込みウィジェットのトラッキング
    track_server_events: bool  # サーバーサイドイベント送信
    custom_dimensions: dict | None  # カスタムディメンション設定
    created_at: datetime
    updated_at: datetime
```

**Validation:**
- Measurement ID形式チェック（正規表現: `^G-[A-Z0-9]{10}$`）
- テナントごとに1つのGA4統合のみ許可
- API Secret は環境変数またはKMS（暗号化）で管理

### FR-GA-002: フロントエンド（React管理画面）トラッキング

**Description:**
React管理画面でのページビュー、ユーザー操作をGA4に送信

**Implementation:**
- `react-ga4` ライブラリを使用
- テナントのGA4設定を取得し、動的に初期化
- ルーティング変更時に自動でページビューを送信

**Tracked Events:**
```typescript
// ページビュー（自動）
pageview({ page_path: '/assessments', page_title: '診断一覧' })

// カスタムイベント
event('assessment_created', {
  assessment_id: 'uuid',
  assessment_title: '営業課題診断',
  tenant_id: 'tenant_uuid',
  creation_method: 'manual' | 'ai_generated'
})

event('lead_status_changed', {
  lead_id: 'uuid',
  old_status: 'new',
  new_status: 'contacted',
  tenant_id: 'tenant_uuid'
})

event('dashboard_viewed', {
  tenant_id: 'tenant_uuid',
  view_type: 'overview' | 'analytics' | 'leads'
})
```

**Privacy Considerations:**
- Cookie同意バナー（GDPR/CCPA準拠）
- オプトアウト機能
- PII（個人識別情報）は送信しない（メール、電話番号など）

### FR-GA-003: 埋め込みウィジェットトラッキング

**Description:**
外部サイトに埋め込まれた診断ウィジェットでのユーザー行動追跡

**Implementation:**
- ウィジェット初期化時にテナントのGA4設定をAPIから取得
- gtag.js を動的にロード（または既存のgtag.jsを再利用）
- Shadow DOMを使用している場合でもイベント送信可能

**Tracked Events:**
```typescript
// ウィジェットライフサイクル
event('embed_widget_loaded', {
  tenant_id: 'uuid',
  assessment_id: 'uuid',
  page_location: window.location.href,
  embed_type: 'iframe' | 'inline' | 'modal'
})

// 診断フロー
event('assessment_view', {
  assessment_id: 'uuid',
  assessment_title: '営業課題診断',
  page_location: window.location.href
})

event('assessment_started', {
  assessment_id: 'uuid',
  total_questions: 10
})

event('question_answered', {
  assessment_id: 'uuid',
  question_number: 1,
  question_id: 'uuid',
  answer_value: '選択肢A', // 個人情報を含まない場合のみ
  time_spent_seconds: 15
})

event('question_skipped', {
  assessment_id: 'uuid',
  question_number: 3
})

event('assessment_completed', {
  assessment_id: 'uuid',
  total_time_seconds: 180,
  questions_answered: 10,
  questions_skipped: 0
})

event('assessment_abandoned', {
  assessment_id: 'uuid',
  last_question_number: 5,
  completion_percentage: 50
})

// リード獲得
event('lead_form_viewed', {
  assessment_id: 'uuid'
})

event('lead_generated', {
  assessment_id: 'uuid',
  lead_score: 75,
  lead_tier: 'warm' // 'hot' | 'warm' | 'cold'
})

event('hot_lead_generated', {
  assessment_id: 'uuid',
  lead_score: 92,
  value: 1000 // 推定リード価値（円）- GA4コンバージョン値
})
```

**Cross-Domain Tracking:**
- `linker` パラメータでクロスドメイントラッキングを有効化
- 診断ウィジェット → DiagnoLeads管理画面への遷移を追跡

### FR-GA-004: サーバーサイドトラッキング（Measurement Protocol）

**Description:**
バックエンドから重要なビジネスイベントをGA4 Measurement Protocol API経由で送信

**Use Cases:**
- クライアントサイドでトラッキングがブロックされた場合のバックアップ
- サーバーサイドでのみ把握できるイベント（外部API連携、バッチ処理など）
- より正確なコンバージョン計測（広告ブロッカー対策）

**Implementation:**
```python
# backend/app/integrations/google_analytics/measurement_protocol.py
class GA4MeasurementProtocol:
    """GA4 Measurement Protocol クライアント"""

    def __init__(self, measurement_id: str, api_secret: str):
        self.measurement_id = measurement_id
        self.api_secret = api_secret
        self.endpoint = f"https://www.google-analytics.com/mp/collect"

    async def send_event(
        self,
        client_id: str,  # ユーザー識別子（UUID）
        event_name: str,
        event_params: dict,
        user_properties: dict | None = None
    ) -> bool:
        """GA4にイベントを送信"""
        payload = {
            "client_id": client_id,
            "events": [{
                "name": event_name,
                "params": event_params
            }]
        }

        if user_properties:
            payload["user_properties"] = user_properties

        # リトライロジック（最大3回）
        # レート制限対応
        # エラーログ記録
        ...
```

**Tracked Server Events:**
```python
# リード生成
await ga4_client.send_event(
    client_id=lead.client_id,
    event_name="lead_generated",
    event_params={
        "assessment_id": str(assessment.id),
        "lead_score": lead.score,
        "lead_tier": lead.tier,
        "tenant_id": str(tenant.id)
    }
)

# ホットリード検出
await ga4_client.send_event(
    client_id=lead.client_id,
    event_name="hot_lead_generated",
    event_params={
        "assessment_id": str(assessment.id),
        "lead_score": lead.score,
        "value": 1000,  # 推定価値
        "currency": "JPY"
    }
)

# 外部連携（Salesforce同期など）
await ga4_client.send_event(
    client_id=tenant.client_id,
    event_name="integration_sync_completed",
    event_params={
        "integration_type": "salesforce",
        "sync_status": "success",
        "records_synced": 15
    }
)
```

### FR-GA-005: イベントスキーマとカスタムディメンション

**Standard Event Parameters:**
```typescript
interface BaseEventParams {
  tenant_id: string;           // すべてのイベントに含める
  assessment_id?: string;      // 診断関連イベント
  lead_id?: string;           // リード関連イベント
  user_id?: string;           // ログイン済みユーザー
  session_id?: string;        // セッション識別
  page_location?: string;     // URL
  page_referrer?: string;     // 流入元
}
```

**Custom Dimensions (GA4で設定):**
- `tenant_id`: テナント識別（マルチテナント分析）
- `assessment_title`: 診断タイトル
- `industry`: 業界（リードの業界）
- `company_size`: 企業規模
- `lead_tier`: リードランク（hot/warm/cold）
- `embed_location`: 埋め込み元ドメイン

**Recommended GA4 Conversions:**
- `assessment_completed`: 診断完了
- `lead_generated`: リード獲得
- `hot_lead_generated`: ホットリード獲得（スコア80+）
- `lead_converted`: 商談化

### FR-GA-006: プライバシーとコンプライアンス

**GDPR/CCPA Compliance:**
- Cookie同意バナーの実装（`@react-cookie-consent`）
- ユーザーが同意するまでGA4トラッキングを無効化
- オプトアウトリンクの提供
- データ保持期間の設定（GA4: 2ヶ月 or 14ヶ月）

**PII Protection:**
- メールアドレス、電話番号、氏名を **絶対に** GA4に送信しない
- `user_id` は匿名化されたUUIDを使用
- IP匿名化（GA4はデフォルトで有効）

**Data Governance:**
- テナント管理者がGA4トラッキングを無効化できる
- 個別ユーザーのオプトアウトリクエストに対応
- 監査ログに「GA4イベント送信」を記録

### FR-GA-007: 接続テストとモニタリング

**Connection Test:**
```
POST /api/v1/tenants/{tenant_id}/integrations/google-analytics/test
```

**Test Procedure:**
1. テストイベント `connection_test` を送信
2. GA4 Realtime Reportで受信を確認（API経由 or 手動）
3. 成功/失敗をユーザーに通知

**Monitoring:**
- GA4イベント送信の成功率をメトリクス化（Prometheus/Grafana）
- 失敗時のリトライキューを実装（Trigger.dev or Redis Queue）
- エラーログを集約（Sentry）

## Non-Functional Requirements

### NFR-GA-001: Performance
- GA4イベント送信が診断体験のパフォーマンスに影響しない（非同期送信）
- 埋め込みウィジェットのバンドルサイズ増加を最小化（+5KB以下）
- サーバーサイドイベント送信は別スレッド/非同期ジョブで実行

### NFR-GA-002: Reliability
- GA4 APIが一時的にダウンしても診断機能は正常動作
- イベント送信失敗時のリトライロジック（最大3回、指数バックオフ）
- 送信失敗イベントをキューに保存し、後で再送信

### NFR-GA-003: Security
- GA4 Measurement Protocol API Secretは暗号化保存（Supabase Vault or KMS）
- テナント間でGA4設定が漏洩しない（Row-Level Security）
- API Secretは絶対にフロントエンドに送信しない

### NFR-GA-004: Cost
- Measurement Protocol API呼び出し数を最適化（バッチ送信可能な場合はバッチ化）
- 無料枠内で運用可能（GA4は無料、Measurement Protocolも無料）
- サーバーサイド送信の頻度を制限（レート制限: 60リクエスト/分）

## API Specification

### 1. GA4統合設定の登録/更新

```http
PUT /api/v1/tenants/{tenant_id}/integrations/google-analytics
Authorization: Bearer <JWT>
Content-Type: application/json

{
  "measurement_id": "G-XXXXXXXXXX",
  "measurement_protocol_api_secret": "xxxxxxxxxxxx",  // Optional
  "enabled": true,
  "track_frontend": true,
  "track_embed_widget": true,
  "track_server_events": true,
  "custom_dimensions": {
    "default_currency": "JPY",
    "default_lead_value": 1000
  }
}

Response 200 OK:
{
  "id": "uuid",
  "tenant_id": "tenant_uuid",
  "measurement_id": "G-XXXXXXXXXX",
  "enabled": true,
  "track_frontend": true,
  "track_embed_widget": true,
  "track_server_events": true,
  "created_at": "2025-11-18T10:00:00Z",
  "updated_at": "2025-11-18T10:00:00Z"
}
```

### 2. GA4統合設定の取得

```http
GET /api/v1/tenants/{tenant_id}/integrations/google-analytics
Authorization: Bearer <JWT>

Response 200 OK:
{
  "id": "uuid",
  "tenant_id": "tenant_uuid",
  "measurement_id": "G-XXXXXXXXXX",
  "enabled": true,
  "track_frontend": true,
  "track_embed_widget": true,
  "track_server_events": true,
  "created_at": "2025-11-18T10:00:00Z",
  "updated_at": "2025-11-18T10:00:00Z"
}

Response 404 Not Found:
{
  "detail": "Google Analytics integration not configured for this tenant"
}
```

### 3. 接続テスト

```http
POST /api/v1/tenants/{tenant_id}/integrations/google-analytics/test
Authorization: Bearer <JWT>

Response 200 OK:
{
  "status": "success",
  "message": "Test event sent successfully to GA4",
  "event_name": "connection_test",
  "timestamp": "2025-11-18T10:00:00Z"
}

Response 400 Bad Request:
{
  "status": "failed",
  "message": "Invalid Measurement ID or API Secret",
  "error_details": "..."
}
```

### 4. 埋め込みウィジェット用GA4設定取得（Public API）

```http
GET /api/v1/public/assessments/{assessment_id}/google-analytics-config
# 認証不要（Public API）

Response 200 OK:
{
  "measurement_id": "G-XXXXXXXXXX",
  "enabled": true,
  "track_embed_widget": true
}

Response 404 Not Found:
{
  "detail": "Google Analytics not configured for this assessment"
}
```

## Implementation Plan

### Phase 1: バックエンド基盤（Week 1-2）

**Tasks:**
1. データベーススキーマ作成
   - [ ] `google_analytics_integrations` テーブルのマイグレーション
   - [ ] Row-Level Securityポリシー設定
2. バックエンドAPI実装
   - [ ] CRUD API (`PUT`, `GET`, `DELETE`)
   - [ ] 接続テストAPI
   - [ ] Public API（埋め込みウィジェット用）
3. Measurement Protocolクライアント実装
   - [ ] `GA4MeasurementProtocol` クラス
   - [ ] リトライロジック、エラーハンドリング
   - [ ] 非同期イベント送信（Trigger.dev統合）
4. テスト
   - [ ] API単体テスト
   - [ ] Measurement Protocol送信テスト

### Phase 2: フロントエンド（React管理画面）（Week 2-3）

**Tasks:**
1. GA4設定画面実装
   - [ ] テナント設定ページに「Google Analytics」セクション追加
   - [ ] Measurement ID入力フォーム
   - [ ] 接続テストボタン
2. react-ga4統合
   - [ ] `react-ga4` パッケージインストール
   - [ ] GA4初期化ロジック（テナント設定ベース）
   - [ ] ページビュー自動送信
3. カスタムイベント送信
   - [ ] 診断作成/編集/削除
   - [ ] リードステータス変更
   - [ ] ダッシュボード表示
4. Cookie同意バナー実装
   - [ ] `@react-cookie-consent` 導入
   - [ ] GDPR/CCPA準拠のオプトアウト

### Phase 3: 埋め込みウィジェット（Week 3-4）

**Tasks:**
1. ウィジェットGA4統合
   - [ ] テナントGA4設定をAPIから取得
   - [ ] gtag.js動的ロード
   - [ ] Shadow DOM対応
2. 診断フローイベント送信
   - [ ] `assessment_view`, `assessment_started`
   - [ ] `question_answered`, `question_skipped`
   - [ ] `assessment_completed`, `assessment_abandoned`
   - [ ] `lead_generated`, `hot_lead_generated`
3. クロスドメイントラッキング
   - [ ] `linker` パラメータ設定
   - [ ] referrer保持
4. テスト
   - [ ] 各イベントの送信確認
   - [ ] GA4リアルタイムレポートでの検証

### Phase 4: サーバーサイドイベント（Week 4-5）

**Tasks:**
1. ビジネスイベント送信実装
   - [ ] リード生成時イベント
   - [ ] ホットリード検出時イベント
   - [ ] 外部連携同期時イベント
2. 非同期ジョブ統合
   - [ ] Trigger.dev or Redis Queueでイベント送信
   - [ ] リトライロジック
3. モニタリング
   - [ ] 送信成功率メトリクス
   - [ ] エラーログ集約（Sentry）

### Phase 5: ドキュメントとテスト（Week 5-6）

**Tasks:**
1. ドキュメント作成
   - [ ] ユーザーガイド（GA4設定手順）
   - [ ] イベントスキーマドキュメント
   - [ ] GA4レポート作成ガイド（推奨ファネル設定など）
2. E2Eテスト
   - [ ] 診断作成→埋め込み→回答→リード獲得の全フローテスト
   - [ ] GA4でのデータ受信確認
3. セキュリティ監査
   - [ ] PII送信チェック
   - [ ] API Secretの暗号化確認
   - [ ] テナント分離の検証

## Testing Strategy

### Unit Tests
- [ ] API endpoints（CRUD、接続テスト）
- [ ] Measurement Protocolクライアント（モック使用）
- [ ] イベントパラメータバリデーション

### Integration Tests
- [ ] バックエンドからGA4へのイベント送信
- [ ] リトライロジックの動作確認
- [ ] テナント分離の検証（他テナントのGA4に送信されないこと）

### E2E Tests
- [ ] React管理画面でのページビュー送信
- [ ] 埋め込みウィジェットでの診断フロー
- [ ] GA4リアルタイムレポートでのイベント確認

### Manual Tests
- [ ] GA4管理画面でイベント設定
- [ ] ファネルレポート作成
- [ ] コンバージョン設定

## Security & Multi-Tenant Considerations

### テナント分離
- すべてのGA4設定は `tenant_id` でフィルタリング
- Row-Level Security（RLS）でデータ漏洩を防止
- API Secretは暗号化保存、フロントエンドに送信しない

### データプライバシー
- PII（メール、電話、氏名）をGA4に **絶対に** 送信しない
- Cookie同意バナー実装（GDPR/CCPA）
- オプトアウト機能
- 匿名化されたclient_id（UUID）を使用

### セキュリティ
- API認証（JWT）必須
- レート制限（60リクエスト/分）
- 入力バリデーション（Measurement ID形式チェック）
- XSS対策（ユーザー入力のサニタイズ）

## Success Metrics

### 実装成功の指標
- [ ] 95%以上のGA4イベント送信成功率
- [ ] ページビュー、カスタムイベントがGA4リアルタイムレポートに表示
- [ ] 診断完了→リード獲得のファネルレポートが作成可能
- [ ] 埋め込みウィジェットのバンドルサイズ増加が5KB以下

### ビジネスインパクト
- テナントの80%がGA4統合を有効化（6ヶ月以内）
- 診断ファネルの離脱率が可視化され、改善施策が実行される
- マーケティングROI（CPA、CVR）が正確に計測できる

## Risks & Mitigation

### Risk 1: GA4 API制限・ダウンタイム
**Impact:** High
**Probability:** Low
**Mitigation:**
- リトライロジック実装（最大3回）
- イベント送信失敗時はキューに保存し、後で再送信
- GA4が停止しても診断機能は正常動作（非同期送信）

### Risk 2: プライバシー規制違反
**Impact:** Critical
**Probability:** Low
**Mitigation:**
- PII送信チェックの自動テスト
- Cookie同意バナー実装
- 定期的なコンプライアンス監査

### Risk 3: パフォーマンス劣化
**Impact:** Medium
**Probability:** Low
**Mitigation:**
- 非同期イベント送信
- バンドルサイズ最適化
- パフォーマンステスト実施

### Risk 4: クロスドメイントラッキングの設定ミス
**Impact:** Medium
**Probability:** Medium
**Mitigation:**
- 詳細なドキュメント作成
- 接続テスト機能でクロスドメイン動作を確認
- テナント向けセットアップガイド提供

## Dependencies

### External Services
- Google Analytics 4 (無料)
- GA4 Measurement Protocol API (無料)

### Libraries
- **Frontend:**
  - `react-ga4`: React用GA4ライブラリ
  - `@react-cookie-consent`: Cookie同意バナー
- **Backend:**
  - `httpx`: 非同期HTTPクライアント（既存）
  - `cryptography`: API Secret暗号化

### Infrastructure
- Trigger.dev または Redis Queue（非同期イベント送信）
- Supabase Vault または KMS（API Secret暗号化）

## Future Enhancements

### Phase 2機能（3-6ヶ月後）
- **GA4レポート自動生成**: DiagnoLeads管理画面内でGA4データを表示
- **Server-Side GTM統合**: より高度なトラッキング設定
- **BigQuery Export**: GA4データをBigQueryにエクスポートし、DiagnoLeadsのデータと統合分析
- **予測分析**: GA4の機械学習機能を活用したリード予測

### 他の分析ツール統合
- **Adobe Analytics**: エンタープライズ顧客向け
- **Mixpanel**: プロダクト分析特化
- **Amplitude**: ユーザー行動分析

## References

- [GA4 Measurement Protocol API](https://developers.google.com/analytics/devguides/collection/protocol/ga4)
- [react-ga4 Documentation](https://github.com/codler/react-ga4)
- [GA4 Event Parameters](https://support.google.com/analytics/answer/9267735)
- [GDPR Compliance for GA4](https://support.google.com/analytics/answer/9019185)

## Appendix: Event Taxonomy

### 診断関連イベント
| Event Name | Trigger | Parameters |
|-----------|---------|------------|
| `assessment_view` | 診断ページ表示 | assessment_id, assessment_title, page_location |
| `assessment_started` | 診断開始ボタンクリック | assessment_id, total_questions |
| `question_answered` | 質問回答 | assessment_id, question_number, question_id, time_spent_seconds |
| `question_skipped` | 質問スキップ | assessment_id, question_number |
| `assessment_completed` | 診断完了 | assessment_id, total_time_seconds, questions_answered |
| `assessment_abandoned` | 診断途中離脱 | assessment_id, last_question_number, completion_percentage |

### リード関連イベント
| Event Name | Trigger | Parameters |
|-----------|---------|------------|
| `lead_form_viewed` | リード入力フォーム表示 | assessment_id |
| `lead_generated` | リード情報入力完了 | assessment_id, lead_score, lead_tier |
| `hot_lead_generated` | ホットリード獲得（スコア80+） | assessment_id, lead_score, value, currency |
| `lead_status_changed` | リードステータス変更 | lead_id, old_status, new_status |

### 管理画面イベント
| Event Name | Trigger | Parameters |
|-----------|---------|------------|
| `dashboard_viewed` | ダッシュボード表示 | view_type |
| `assessment_created` | 診断作成 | assessment_id, creation_method |
| `assessment_published` | 診断公開 | assessment_id |
| `integration_connected` | 外部連携設定 | integration_type |

---

**Status:** Ready for Review
**Next Steps:**
1. チームレビュー
2. セキュリティ監査
3. 実装開始（Phase 1）
