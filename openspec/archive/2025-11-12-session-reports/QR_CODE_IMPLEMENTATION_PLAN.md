# QRコード配信機能 - 実装計画書

**Status**: Ready for Implementation  
**Priority**: High  
**Estimated Effort**: 1-2 weeks (1 backend dev + 1 frontend dev)  
**Target Sprint**: Next Sprint  
**Created**: 2025-11-11

## 📋 目次

1. [概要](#概要)
2. [実装タスク分解](#実装タスク分解)
3. [ファイル構成](#ファイル構成)
4. [データモデル詳細](#データモデル詳細)
5. [API設計詳細](#api設計詳細)
6. [フロントエンド実装](#フロントエンド実装)
7. [テスト戦略](#テスト戦略)
8. [デプロイメント計画](#デプロイメント計画)
9. [リスクと対策](#リスクと対策)

---

## 概要

診断ごとの専用QRコードを生成し、オフラインマーケティングで活用。スキャン数のトラッキングとファネル分析を提供。

**主要機能:**
- QRコード生成（PNG/SVG、カスタマイズ可能）
- 短縮URLとリダイレクト
- スキャントラッキング（デバイス、地域、ファネル）
- 統計ダッシュボード

**技術スタック:**
- Backend: Python (qrcode, Pillow, geoip2, user-agents)
- Frontend: React (qrcode.react, recharts)
- Database: PostgreSQL
- Storage: S3/Cloudflare R2 (QRコード画像)

---

## 実装タスク分解

### Week 1: バックエンド実装 (5日間)

#### Day 1: データモデルとマイグレーション
**担当**: Backend Developer  
**所要時間**: 1日

- [ ] **Task 1.1**: QRCodeモデルの作成
  - ファイル: `backend/app/models/qr_code.py`
  - フィールド: id, tenant_id, assessment_id, short_code, utm_params, style, scan_count, enabled
  - リレーション: Tenant, Assessment

- [ ] **Task 1.2**: QRCodeScanモデルの作成
  - ファイル: `backend/app/models/qr_code_scan.py`
  - フィールド: id, qr_code_id, user_agent, device_type, ip_address, location, behavior
  - リレーション: QRCode, Lead (optional)

- [ ] **Task 1.3**: Alembicマイグレーション作成
  - ファイル: `backend/alembic/versions/XXXX_add_qr_code_tables.py`
  - インデックス: qr_code.short_code (unique), qr_code_scan.qr_code_id

- [ ] **Task 1.4**: Pydanticスキーマ定義
  - ファイル: `backend/app/schemas/qr_code.py`
  - スキーマ: QRCodeCreate, QRCodeUpdate, QRCodeResponse, QRCodeScanResponse

**成果物:**
- データモデル2つ
- マイグレーションファイル
- Pydanticスキーマ4つ

---

#### Day 2: QRコード生成サービス
**担当**: Backend Developer  
**所要時間**: 1日

- [ ] **Task 2.1**: QRCodeServiceクラスの実装
  - ファイル: `backend/app/services/qr_code_service.py`
  - メソッド: generate_qr_code(), generate_short_code(), upload_to_storage()

- [ ] **Task 2.2**: QRコード画像生成ロジック
  - ライブラリ: qrcode, Pillow
  - 機能: カラーカスタマイズ、ロゴ埋め込み、フレーム追加
  - 出力: PNG (512x512), SVG

- [ ] **Task 2.3**: 短縮URL生成ロジック
  - アルゴリズム: 7文字のランダム英数字
  - 重複チェック: データベースクエリ
  - フォーマット: `https://dgnl.ds/{short_code}`

- [ ] **Task 2.4**: 画像ストレージ統合
  - AWS S3 または Cloudflare R2
  - パス: `qr-codes/{tenant_id}/{qr_code_id}.png`
  - 公開URL生成

**成果物:**
- QRCodeServiceクラス
- ユニットテスト5つ
- 画像生成機能

---

#### Day 3: API エンドポイント（CRUD）
**担当**: Backend Developer  
**所要時間**: 1日

- [ ] **Task 3.1**: QRコード作成エンドポイント
  - エンドポイント: `POST /api/v1/tenants/{tenant_id}/assessments/{assessment_id}/qr-codes`
  - リクエスト: name, utm_params, style
  - レスポンス: QRCodeResponse (short_url, qr_code_url)

- [ ] **Task 3.2**: QRコード一覧取得エンドポイント
  - エンドポイント: `GET /api/v1/tenants/{tenant_id}/assessments/{assessment_id}/qr-codes`
  - クエリパラメータ: page, limit
  - レスポンス: QRCodeResponse配列 + pagination

- [ ] **Task 3.3**: QRコード詳細取得エンドポイント
  - エンドポイント: `GET /api/v1/tenants/{tenant_id}/qr-codes/{qr_id}`
  - レスポンス: QRCodeResponse + 統計サマリー

- [ ] **Task 3.4**: QRコード更新/削除エンドポイント
  - エンドポイント: `PUT /api/v1/tenants/{tenant_id}/qr-codes/{qr_id}`
  - エンドポイント: `DELETE /api/v1/tenants/{tenant_id}/qr-codes/{qr_id}`
  - 機能: enabled切り替え、論理削除

**成果物:**
- APIエンドポイント4つ
- FastAPIルーター設定
- 統合テスト4つ

---

#### Day 4: リダイレクトとトラッキング
**担当**: Backend Developer  
**所要時間**: 1日

- [ ] **Task 4.1**: リダイレクトエンドポイント
  - エンドポイント: `GET /r/{short_code}`
  - 機能: QRコード検索、トラッキング記録、診断ページへリダイレクト
  - パフォーマンス: 500ms以内

- [ ] **Task 4.2**: トラッキングサービス
  - ファイル: `backend/app/services/tracking_service.py`
  - 機能: User Agent解析、GeoIP、デバイス判定
  - 非同期処理: Trigger.devまたはCelery

- [ ] **Task 4.3**: GeoIPデータベース統合
  - ライブラリ: geoip2
  - データ: MaxMind GeoLite2
  - 機能: IPアドレス→国・都市

- [ ] **Task 4.4**: User Agent解析
  - ライブラリ: user-agents
  - 機能: デバイスタイプ、OS、ブラウザ判定

**成果物:**
- リダイレクトエンドポイント
- TrackingServiceクラス
- GeoIP統合
- ユニットテスト5つ

---

#### Day 5: 統計・分析API
**担当**: Backend Developer  
**所要時間**: 1日

- [ ] **Task 5.1**: QRコード統計エンドポイント
  - エンドポイント: `GET /api/v1/tenants/{tenant_id}/qr-codes/{qr_id}/analytics`
  - レスポンス: total_scans, unique_scans, conversion_rate, scans_by_date, scans_by_device, scans_by_country

- [ ] **Task 5.2**: 時系列データ集計
  - 機能: 日別/週別/月別のスキャン数
  - 最適化: PostgreSQLのGROUP BY + 日付関数

- [ ] **Task 5.3**: ファネル分析
  - メトリクス: スキャン → 診断開始 → 診断完了 → リード作成
  - 計算: 各ステップのコンバージョン率

- [ ] **Task 5.4**: デバイス・地域別集計
  - 集計: device_type, country, city
  - パフォーマンス: インデックス最適化

**成果物:**
- 統計APIエンドポイント
- 集計ロジック
- ユニットテスト3つ

---

### Week 2: フロントエンド & テスト (5日間)

#### Day 6-7: フロントエンド管理画面
**担当**: Frontend Developer  
**所要時間**: 2日

- [ ] **Task 6.1**: QRコード管理ページ
  - パス: `/assessments/{id}/qr-codes`
  - コンポーネント: `QRCodeList.tsx`
  - 機能: 一覧表示、作成ボタン、編集/削除

- [ ] **Task 6.2**: QRコード作成フォーム
  - コンポーネント: `QRCodeCreateForm.tsx`
  - フィールド: name, utm_source/medium/campaign, color, logo_url, frame
  - バリデーション: React Hook Form + Zod

- [ ] **Task 6.3**: QRコードプレビュー
  - コンポーネント: `QRCodePreview.tsx`
  - ライブラリ: qrcode.react
  - 機能: リアルタイムプレビュー

- [ ] **Task 6.4**: QRコードダウンロード機能
  - 形式: PNG (512x512, 1024x1024), SVG
  - 機能: ブラウザダウンロード

**成果物:**
- Reactコンポーネント4つ
- フォームバリデーション
- プレビュー機能

---

#### Day 8: 統計ダッシュボード
**担当**: Frontend Developer  
**所要時間**: 1日

- [ ] **Task 8.1**: QRコード統計ページ
  - パス: `/qr-codes/{id}/analytics`
  - コンポーネント: `QRCodeAnalytics.tsx`
  - レイアウト: グリッド（KPI + グラフ）

- [ ] **Task 8.2**: スキャン数グラフ
  - ライブラリ: recharts
  - タイプ: LineChart（時系列）
  - 期間切り替え: 7日/30日/90日

- [ ] **Task 8.3**: デバイス・地域別グラフ
  - タイプ: PieChart（デバイス）、BarChart（国別）
  - 色: ブランドカラー

- [ ] **Task 8.4**: ファネル可視化
  - タイプ: FunnelChart または ステップ表示
  - メトリクス: スキャン→開始→完了→リード

**成果物:**
- 統計ページ
- グラフコンポーネント3つ
- ファネル可視化

---

#### Day 9-10: テストとバグ修正
**担当**: Backend + Frontend Developers  
**所要時間**: 2日

- [ ] **Task 9.1**: バックエンド統合テスト
  - ファイル: `backend/tests/test_qr_code_api.py`
  - カバレッジ: QRコードCRUD、リダイレクト、統計

- [ ] **Task 9.2**: フロントエンド単体テスト
  - ファイル: `frontend/src/features/qr-codes/__tests__/`
  - ツール: Vitest + React Testing Library

- [ ] **Task 9.3**: E2Eテスト
  - ツール: Playwright
  - シナリオ: QRコード作成 → スキャン → 統計確認

- [ ] **Task 9.4**: バグ修正とリファクタリング
  - コードレビュー
  - パフォーマンス最適化
  - エッジケース対応

**成果物:**
- 統合テスト10+
- E2Eテスト3つ
- バグ修正

---

## ファイル構成

### バックエンド

```
backend/
├── app/
│   ├── models/
│   │   ├── qr_code.py                    # QRCodeモデル
│   │   └── qr_code_scan.py               # QRCodeScanモデル
│   │
│   ├── schemas/
│   │   └── qr_code.py                    # Pydanticスキーマ
│   │
│   ├── services/
│   │   ├── qr_code_service.py            # QRコード生成・管理
│   │   └── tracking_service.py           # トラッキング・分析
│   │
│   ├── api/v1/
│   │   ├── qr_codes.py                   # QRコードCRUD API
│   │   └── redirect.py                   # リダイレクトエンドポイント
│   │
│   └── utils/
│       ├── qr_image_generator.py         # QR画像生成ユーティリティ
│       └── geoip.py                      # GeoIPヘルパー
│
├── alembic/versions/
│   └── XXXX_add_qr_code_tables.py        # マイグレーション
│
├── tests/
│   ├── test_qr_code_service.py
│   ├── test_qr_code_api.py
│   └── test_tracking_service.py
│
└── requirements.txt                       # 依存関係更新
```

### フロントエンド

```
frontend/
├── src/
│   ├── features/
│   │   └── qr-codes/
│   │       ├── components/
│   │       │   ├── QRCodeList.tsx
│   │       │   ├── QRCodeCreateForm.tsx
│   │       │   ├── QRCodePreview.tsx
│   │       │   ├── QRCodeAnalytics.tsx
│   │       │   ├── QRCodeScanChart.tsx
│   │       │   ├── DeviceDistribution.tsx
│   │       │   └── FunnelVisualization.tsx
│   │       │
│   │       ├── services/
│   │       │   └── qrCodeService.ts      # API呼び出し
│   │       │
│   │       ├── hooks/
│   │       │   ├── useQRCodes.ts
│   │       │   └── useQRCodeAnalytics.ts
│   │       │
│   │       └── __tests__/
│   │           ├── QRCodeList.test.tsx
│   │           └── QRCodeAnalytics.test.tsx
│   │
│   └── routes/
│       └── qr-codes.tsx                  # ルート設定
│
└── package.json                          # 依存関係更新
```

---

## データモデル詳細

### QRCode

```python
class QRCode(Base):
    __tablename__ = "qr_codes"
    
    # Primary Key
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    
    # Foreign Keys
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.id"), nullable=False)
    assessment_id: Mapped[UUID] = mapped_column(ForeignKey("assessments.id"), nullable=False)
    
    # Basic Info
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    short_code: Mapped[str] = mapped_column(String(10), unique=True, index=True, nullable=False)
    short_url: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # UTM Parameters
    utm_source: Mapped[str | None] = mapped_column(String(100))
    utm_medium: Mapped[str | None] = mapped_column(String(100))
    utm_campaign: Mapped[str | None] = mapped_column(String(100))
    utm_term: Mapped[str | None] = mapped_column(String(100))
    utm_content: Mapped[str | None] = mapped_column(String(100))
    
    # Style (JSONB)
    style: Mapped[dict] = mapped_column(JSONB, default=dict)
    # {
    #   "color": "#1E40AF",
    #   "logo_url": "https://...",
    #   "frame": "rounded",
    #   "size": 512
    # }
    
    # Storage
    qr_code_image_url: Mapped[str | None] = mapped_column(String(500))  # S3 URL
    qr_code_svg_url: Mapped[str | None] = mapped_column(String(500))
    
    # Tracking
    scan_count: Mapped[int] = mapped_column(Integer, default=0)
    unique_scan_count: Mapped[int] = mapped_column(Integer, default=0)
    last_scanned_at: Mapped[datetime | None] = mapped_column(DateTime)
    
    # Status
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tenant: Mapped["Tenant"] = relationship(back_populates="qr_codes")
    assessment: Mapped["Assessment"] = relationship(back_populates="qr_codes")
    scans: Mapped[list["QRCodeScan"]] = relationship(back_populates="qr_code", cascade="all, delete-orphan")
```

### QRCodeScan

```python
class QRCodeScan(Base):
    __tablename__ = "qr_code_scans"
    
    # Primary Key
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    
    # Foreign Key
    qr_code_id: Mapped[UUID] = mapped_column(ForeignKey("qr_codes.id"), nullable=False, index=True)
    
    # User Info
    user_agent: Mapped[str] = mapped_column(Text, nullable=False)
    device_type: Mapped[str] = mapped_column(String(50))  # "mobile", "tablet", "desktop"
    os: Mapped[str | None] = mapped_column(String(100))  # "iOS", "Android", "Windows"
    browser: Mapped[str | None] = mapped_column(String(100))  # "Safari", "Chrome"
    
    # Location (GeoIP)
    ip_address: Mapped[str] = mapped_column(String(45))  # IPv6対応、ハッシュ化推奨
    country: Mapped[str | None] = mapped_column(String(2))  # ISO 3166-1 alpha-2
    city: Mapped[str | None] = mapped_column(String(255))
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)
    
    # Behavior Tracking
    scanned_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    assessment_started: Mapped[bool] = mapped_column(Boolean, default=False)
    assessment_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    lead_created: Mapped[bool] = mapped_column(Boolean, default=False)
    lead_id: Mapped[UUID | None] = mapped_column(ForeignKey("leads.id"))
    
    # Session
    session_id: Mapped[str | None] = mapped_column(String(255))  # Cookie/LocalStorage
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    qr_code: Mapped["QRCode"] = relationship(back_populates="scans")
    lead: Mapped["Lead | None"] = relationship(back_populates="qr_code_scans")
```

### インデックス戦略

```sql
-- QRCodeテーブル
CREATE UNIQUE INDEX idx_qr_codes_short_code ON qr_codes(short_code);
CREATE INDEX idx_qr_codes_tenant_id ON qr_codes(tenant_id);
CREATE INDEX idx_qr_codes_assessment_id ON qr_codes(assessment_id);

-- QRCodeScanテーブル
CREATE INDEX idx_qr_code_scans_qr_code_id ON qr_code_scans(qr_code_id);
CREATE INDEX idx_qr_code_scans_scanned_at ON qr_code_scans(scanned_at);
CREATE INDEX idx_qr_code_scans_lead_id ON qr_code_scans(lead_id);
```

---

## API設計詳細

### 1. QRコード作成

```
POST /api/v1/tenants/{tenant_id}/assessments/{assessment_id}/qr-codes
```

**Request:**
```json
{
  "name": "展示会2025",
  "utm_source": "booth",
  "utm_medium": "qr",
  "utm_campaign": "tech_expo_2025",
  "utm_term": "tokyo",
  "utm_content": "main_banner",
  "style": {
    "color": "#1E40AF",
    "logo_url": "https://example.com/logo.png",
    "frame": "rounded",
    "size": 512
  }
}
```

**Response (201):**
```json
{
  "id": "qr_abc123...",
  "name": "展示会2025",
  "short_code": "a1B2c3D",
  "short_url": "https://dgnl.ds/a1B2c3D",
  "qr_code_image_url": "https://cdn.diagnoleads.com/qr-codes/tenant123/qr_abc123.png",
  "qr_code_svg_url": "https://cdn.diagnoleads.com/qr-codes/tenant123/qr_abc123.svg",
  "scan_count": 0,
  "enabled": true,
  "created_at": "2025-11-11T10:00:00Z"
}
```

---

### 2. QRコード一覧取得

```
GET /api/v1/tenants/{tenant_id}/assessments/{assessment_id}/qr-codes?page=1&limit=20
```

**Response (200):**
```json
{
  "qr_codes": [
    {
      "id": "qr_abc123...",
      "name": "展示会2025",
      "short_url": "https://dgnl.ds/a1B2c3D",
      "scan_count": 145,
      "unique_scan_count": 98,
      "last_scanned_at": "2025-11-11T09:30:00Z",
      "enabled": true,
      "created_at": "2025-11-01T10:00:00Z"
    }
  ],
  "pagination": {
    "total": 5,
    "page": 1,
    "limit": 20,
    "pages": 1
  }
}
```

---

### 3. QRコード統計

```
GET /api/v1/tenants/{tenant_id}/qr-codes/{qr_id}/analytics?period=30d
```

**Response (200):**
```json
{
  "summary": {
    "total_scans": 145,
    "unique_scans": 98,
    "assessment_started": 67,
    "assessment_completed": 42,
    "leads_created": 38,
    "conversion_rate": 0.262
  },
  "scans_by_date": [
    {"date": "2025-11-01", "scans": 12},
    {"date": "2025-11-02", "scans": 18}
  ],
  "scans_by_device": {
    "mobile": 87,
    "tablet": 23,
    "desktop": 35
  },
  "scans_by_country": {
    "JP": 120,
    "US": 15,
    "CN": 10
  },
  "funnel": {
    "scanned": 145,
    "started": 67,
    "completed": 42,
    "converted": 38
  }
}
```

---

### 4. リダイレクト

```
GET /r/{short_code}
```

**処理フロー:**
1. short_codeでQRCodeを検索
2. enabledチェック
3. トラッキング記録（非同期）
   - User Agent解析
   - GeoIP
   - QRCodeScanレコード作成
   - scan_countインクリメント
4. 診断ページへリダイレクト

**Redirect (302):**
```
Location: https://app.diagnoleads.com/assessments/{assessment_id}?utm_source=booth&utm_medium=qr&utm_campaign=tech_expo_2025&qr={short_code}
```

---

## フロントエンド実装

### コンポーネント階層

```
QRCodeManagementPage
├── QRCodeList
│   ├── QRCodeCard (for each QR code)
│   │   ├── QRCodePreview
│   │   ├── Stats (scan_count, conversion_rate)
│   │   └── Actions (View Analytics, Download, Edit, Delete)
│   └── CreateButton → QRCodeCreateModal
│
└── QRCodeAnalyticsPage
    ├── KPICards (Total Scans, Unique Scans, Conversion Rate, etc.)
    ├── ScanChart (Line chart)
    ├── DeviceDistribution (Pie chart)
    ├── CountryDistribution (Bar chart)
    └── FunnelVisualization
```

### 状態管理

```typescript
// Zustand store
interface QRCodeStore {
  qrCodes: QRCode[];
  selectedQRCode: QRCode | null;
  analytics: QRCodeAnalytics | null;
  
  fetchQRCodes: (assessmentId: string) => Promise<void>;
  createQRCode: (data: QRCodeCreate) => Promise<QRCode>;
  deleteQRCode: (qrCodeId: string) => Promise<void>;
  fetchAnalytics: (qrCodeId: string, period: string) => Promise<void>;
}
```

---

## テスト戦略

### バックエンド

#### Unit Tests (30+)

**QRCodeService:**
- `test_generate_qr_code_png()` - PNG生成
- `test_generate_qr_code_svg()` - SVG生成
- `test_generate_short_code_unique()` - 短縮コードの一意性
- `test_qr_code_with_logo()` - ロゴ埋め込み
- `test_qr_code_custom_color()` - カラーカスタマイズ

**TrackingService:**
- `test_parse_user_agent()` - User Agent解析
- `test_geoip_lookup()` - GeoIP
- `test_record_scan()` - スキャン記録
- `test_unique_scan_detection()` - ユニークスキャン判定

#### Integration Tests (10+)

**API Endpoints:**
- `test_create_qr_code()` - QRコード作成
- `test_list_qr_codes_pagination()` - 一覧取得
- `test_get_qr_code_analytics()` - 統計取得
- `test_redirect_valid_short_code()` - リダイレクト成功
- `test_redirect_invalid_short_code()` - リダイレクト失敗
- `test_tenant_isolation()` - テナント分離

### フロントエンド

#### Component Tests (15+)

- `QRCodeList.test.tsx` - 一覧表示
- `QRCodeCreateForm.test.tsx` - 作成フォーム
- `QRCodePreview.test.tsx` - プレビュー
- `QRCodeAnalytics.test.tsx` - 統計表示

#### E2E Tests (3+)

**Playwright:**
1. **QRコード作成フロー**
   - 診断ページからQRコード作成
   - フォーム入力
   - プレビュー確認
   - 作成完了
   - ダウンロード

2. **QRコードスキャンフロー**
   - リダイレクトURL訪問
   - 診断ページ表示
   - トラッキング記録確認

3. **統計表示フロー**
   - 統計ページ訪問
   - グラフ表示確認
   - 期間切り替え

---

## デプロイメント計画

### データベースマイグレーション

```bash
# ステージング環境
1. バックアップ取得
   pg_dump diagnoleads_staging > backup_YYYYMMDD.sql

2. マイグレーション実行
   cd backend
   alembic upgrade head

3. データ確認
   psql diagnoleads_staging -c "SELECT * FROM qr_codes LIMIT 1;"

# 本番環境（ダウンタイムなし）
1. バックアップ取得
2. マイグレーション実行（スキーマのみ）
3. アプリケーションデプロイ
4. ヘルスチェック
```

### アプリケーションデプロイ

```bash
# バックエンド (Railway/Fly.io)
1. 環境変数設定
   - GEOIP_DATABASE_PATH
   - S3_BUCKET_NAME (or R2)
   - SHORT_URL_DOMAIN

2. 依存関係追加
   pip install qrcode[pil] geoip2 user-agents

3. デプロイ
   git push railway main

# フロントエンド (Vercel)
1. 環境変数なし（既存設定使用）
2. ビルド
   npm run build
3. デプロイ
   vercel --prod
```

### 監視設定

```yaml
# Sentry
- qr_code_service エラー監視
- tracking_service エラー監視
- redirect エンドポイント監視

# Metrics
- QRコード作成数/日
- リダイレクト応答時間
- スキャン数/日
```

---

## リスクと対策

### リスク1: 短縮コードの衝突
**確率**: 低  
**影響**: 中  
**対策**:
- 7文字の英数字 = 62^7 = 3.5兆通り
- 重複チェックロジック実装
- 万が一の衝突時は再生成

### リスク2: リダイレクトのパフォーマンス
**確率**: 中  
**影響**: 高  
**対策**:
- Redisキャッシュ（short_code → assessment_id）
- トラッキングは非同期処理
- データベースインデックス最適化
- 目標: 500ms以内

### リスク3: GeoIPデータベースの精度
**確率**: 低  
**影響**: 低  
**対策**:
- MaxMind GeoLite2使用（無料、月次更新）
- 精度は参考値として扱う
- IPアドレスはハッシュ化してプライバシー保護

### リスク4: 画像ストレージコスト
**確率**: 中  
**影響**: 低  
**対策**:
- Cloudflare R2使用（無料枠10GB）
- 画像サイズ最適化（PNG: 512x512 = 約30KB）
- 未使用QRコードの定期削除

### リスク5: スパム/悪用
**確率**: 低  
**影響**: 中  
**対策**:
- QRコード作成にレート制限（10/hour）
- テナントごとの作成上限（100個）
- 異常なスキャン数の検知とアラート

---

## 実装チェックリスト

### Week 1: バックエンド

- [ ] Day 1: データモデルとマイグレーション (4 tasks)
- [ ] Day 2: QRコード生成サービス (4 tasks)
- [ ] Day 3: API エンドポイント（CRUD） (4 tasks)
- [ ] Day 4: リダイレクトとトラッキング (4 tasks)
- [ ] Day 5: 統計・分析API (4 tasks)

### Week 2: フロントエンド & テスト

- [ ] Day 6-7: フロントエンド管理画面 (4 tasks)
- [ ] Day 8: 統計ダッシュボード (4 tasks)
- [ ] Day 9-10: テストとバグ修正 (4 tasks)

### デプロイメント

- [ ] ステージング環境デプロイ
- [ ] QA/UAT実施
- [ ] 本番環境デプロイ
- [ ] 監視設定

---

## 次のステップ

1. **承認待ち**: プロダクトオーナー、テックリードのレビュー
2. **リソース確保**: Backend Dev 1名、Frontend Dev 1名
3. **Sprint計画**: 次回Sprint Planning Meetingで組み込み
4. **キックオフ**: 実装開始日決定

---

**Status**: ✅ Planning Complete, Ready for Implementation  
**Reviewed by**: [Name]  
**Approved by**: [Name]  
**Implementation Start Date**: TBD
