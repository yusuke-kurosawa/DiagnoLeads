# Feature: QR Code Distribution with Comprehensive Tracking

**Status**: Approved  
**Priority**: High  
**Category**: Multi-Channel Distribution  
**Created**: 2025-11-11  
**Last Updated**: 2025-11-13  
**Effort**: Small (1-2週間)  
**Version**: 2.0 (UTM, Device/Geo, Funnel Tracking 追加)

## 概要

診断ごとの専用QRコードを生成し、オフラインマーケティング（名刺、ポスター、展示会ブース）で活用できるようにする。

**主要機能**:
- ✅ UTM パラメータベースのトラッキング
- ✅ デバイス・OS・ブラウザ情報の記録
- ✅ GeoIP ベースの地理情報取得
- ✅ スキャン→診断開始→完了のファネル分析

## User Stories

- マーケティング担当者として、展示会ブース用のQRコード付きポスターを作成したい
- 営業担当者として、名刺にQRコードを印刷して診断に誘導したい
- 管理者として、どのQRコードが何回スキャンされたか分析したい
- イベント担当者として、イベントごとに異なるQRコードを発行して効果測定したい

## Requirements

### Functional Requirements

1. **QRコード生成**
   - 診断ごとの専用QRコード
   - トラッキング用のユニークパラメータ付きURL
   - カスタムUTMパラメータ対応
   - 複数QRコードの発行（チャネル別）

2. **QRコード管理**
   - QRコード一覧表示
   - ダウンロード（PNG, SVG形式）
   - 印刷用高解像度バージョン
   - QRコードの有効/無効切り替え

3. **UTM パラメータ追跡** ⭐ NEW
   - **UTM Source**: トラッキングソース（e.g., "booth", "email", "flyer"）
   - **UTM Medium**: トラッキングメディウム（e.g., "qr_code", "print", "digital"）
   - **UTM Campaign**: キャンペーン名（e.g., "spring2025", "tech_expo"）
   - **UTM Term**: キーワード（オプション）
   - **UTM Content**: バリエーション（オプション）
   - 各QRコードは独立した UTM パラメータを持つ

4. **デバイス・OS・ブラウザ追跡** ⭐ NEW
   - **Device Type**: スキャンデバイス種別（mobile, tablet, desktop）
   - **OS**: オペレーティングシステム（iOS, Android, Windows, macOS）
   - **Browser**: ブラウザ情報（Safari, Chrome, Firefox, Edge）
   - User Agent から自動解析
   - デバイス別のスキャン数集計

5. **地理情報追跡 (GeoIP)** ⭐ NEW
   - **IP Address**: スキャン元 IP（ハッシュ化して保存）
   - **Country**: ISO 3166-1 alpha-2 国コード
   - **City**: 都市名
   - **Latitude/Longitude**: 近似座標
   - GeoIP データベースで自動取得
   - 国別・都市別のスキャン数集計

6. **ファネル追跡** ⭐ NEW
   - **Stage 1 - Scan**: QRコードスキャン時点
   - **Stage 2 - Start**: 診断最初の質問回答
   - **Stage 3 - Complete**: 診断完了
   - **Stage 4 - Lead**: リード情報送信
   - 各ステージ間の進行率（conversion rate）を計算
   - ドロップオフポイントの特定

7. **トラッキング**
   - スキャン数のカウント
   - スキャン元の地域・デバイス情報
   - スキャン→診断開始→完了のファネル分析
   - 時系列グラフ表示

8. **カスタマイズ**
   - ブランドカラーでのQRコード生成
   - ロゴ埋め込み（中央）
   - フレーム付きデザイン（"Scan Here"など）

### Non-Functional Requirements

- **パフォーマンス**: QRコード生成は3秒以内
- **可用性**: リダイレクトサーバーの99.9% uptime
- **スケーラビリティ**: 10万QRコード/テナントに対応
- **互換性**: iOS/Androidの標準カメラアプリで読取可能

## API Design

### QRコード生成

```
POST /api/v1/tenants/{tenant_id}/assessments/{assessment_id}/qr-codes
  Request:
  {
    "name": "展示会2025",
    "utm_source": "booth",
    "utm_medium": "qr",
    "utm_campaign": "tech_expo_2025",
    "style": {
      "color": "#1E40AF",
      "logo_url": "https://example.com/logo.png",
      "frame": "rounded"
    }
  }
  
  Response:
  {
    "id": "qr_abc123",
    "short_url": "https://dgnl.ds/abc123",
    "qr_code_url": "https://api.diagnoleads.com/qr/abc123.png",
    "tracking_id": "trk_xyz789"
  }
```

### QRコード一覧取得

```
GET /api/v1/tenants/{tenant_id}/assessments/{assessment_id}/qr-codes
  Response:
  {
    "qr_codes": [
      {
        "id": "qr_abc123",
        "name": "展示会2025",
        "short_url": "https://dgnl.ds/abc123",
        "scan_count": 145,
        "created_at": "2025-11-01T10:00:00Z"
      }
    ]
  }
```

### トラッキング統計

```
GET /api/v1/tenants/{tenant_id}/qr-codes/{qr_id}/analytics
  Response:
  {
    # Funnel Metrics
    "funnel": {
      "scans": 145,              # Stage 1: Scan
      "started": 67,             # Stage 2: Start
      "completed": 42,           # Stage 3: Complete
      "leads": 12,               # Stage 4: Lead
      
      # Conversion rates
      "start_rate": 0.46,        # started / scans
      "completion_rate": 0.63,   # completed / started
      "lead_rate": 0.29,         # leads / completed
      "overall_conversion": 0.08 # leads / scans
    },
    
    # Time Series
    "scans_by_date": [
      {"date": "2025-11-10", "scans": 20, "completed": 5},
      {"date": "2025-11-11", "scans": 25, "completed": 8}
    ],
    
    # Device/Browser Tracking
    "scans_by_device": {
      "mobile": {"count": 89, "percentage": 61},
      "tablet": {"count": 28, "percentage": 19},
      "desktop": {"count": 28, "percentage": 19}
    },
    "scans_by_os": {
      "iOS": {"count": 60, "percentage": 41},
      "Android": {"count": 52, "percentage": 36},
      "Windows": {"count": 20, "percentage": 14},
      "macOS": {"count": 13, "percentage": 9}
    },
    "scans_by_browser": {
      "Safari": {"count": 65, "percentage": 45},
      "Chrome": {"count": 68, "percentage": 47},
      "Firefox": {"count": 8, "percentage": 5},
      "Edge": {"count": 4, "percentage": 3}
    },
    
    # GeoIP Tracking
    "scans_by_country": {
      "JP": {"count": 90, "percentage": 62},
      "US": {"count": 30, "percentage": 21},
      "CN": {"count": 15, "percentage": 10},
      "Other": {"count": 10, "percentage": 7}
    },
    "scans_by_city": {
      "Tokyo": {"count": 45, "percentage": 31},
      "Osaka": {"count": 25, "percentage": 17},
      "Yokohama": {"count": 20, "percentage": 14}
    },
    
    # Summary
    "unique_scans": 98,
    "average_completion_per_scan": 0.29
  }
```

### QRコード画像取得

```
GET /api/v1/qr-codes/{qr_id}.png?size=512
GET /api/v1/qr-codes/{qr_id}.svg
```

### 短縮URL→診断へのリダイレクト

```
GET /r/{short_code}
  - トラッキング情報を記録
  - 診断ページにリダイレクト
```

## Data Model

### QRCode

```python
class QRCode(Base):
    __tablename__ = "qr_codes"
    
    id: UUID
    tenant_id: UUID  # FK to Tenant
    assessment_id: UUID  # FK to Assessment
    
    # Basic Info
    name: str  # "展示会2025"
    short_code: str  # "abc123" (unique)
    short_url: str  # "https://dgnl.ds/abc123"
    
    # UTM Parameters
    utm_source: str | None
    utm_medium: str | None
    utm_campaign: str | None
    utm_term: str | None
    utm_content: str | None
    
    # Style
    style: dict  # JSONB
    # {
    #   "color": "#1E40AF",
    #   "logo_url": "...",
    #   "frame": "rounded"
    # }
    
    # Tracking
    scan_count: int = 0
    unique_scan_count: int = 0
    last_scanned_at: datetime | None
    
    # Status
    enabled: bool = True
    
    created_at: datetime
    updated_at: datetime
```

### QRCodeScan (トラッキング)

```python
class QRCodeScan(Base):
    __tablename__ = "qr_code_scans"
    
    id: UUID
    qr_code_id: UUID  # FK to QRCode
    
    # User Agent Information (Device/Browser Tracking)
    user_agent: str
    device_type: str  # "mobile", "tablet", "desktop"
    os: str  # "iOS", "Android", "Windows", "macOS"
    browser: str | None  # "Safari", "Chrome", "Firefox", "Edge"
    
    # Location Information (GeoIP Tracking)
    ip_address: str  # Hashed for privacy
    country: str | None  # ISO 3166-1 alpha-2
    city: str | None
    latitude: float | None  # Approximate location
    longitude: float | None
    
    # Funnel Tracking
    scanned_at: datetime  # Stage 1: Scan
    assessment_started: bool = False  # Stage 2: Start
    assessment_completed: bool = False  # Stage 3: Complete
    lead_created: bool = False  # Stage 4: Lead
    lead_id: UUID | None  # FK to Lead
    
    # Session Tracking
    session_id: str | None  # From browser cookie/localStorage
    
    created_at: datetime
```

**トラッキング段階**:
1. **Scan**: QRCodeScan 作成時点
2. **Start**: `assessment_started = True` （最初の質問回答時）
3. **Complete**: `assessment_completed = True` （診断完了時）
4. **Lead**: `lead_created = True` （リード作成時）

## UI/UX Design

### QRコード管理画面

```
┌─────────────────────────────────────────────────────┐
│ 診断: 営業課題診断                                    │
├─────────────────────────────────────────────────────┤
│                                                     │
│ [+ 新しいQRコードを作成]                             │
│                                                     │
│ ┌───────────────────────────────────────────────┐  │
│ │ 📱 展示会2025                                   │  │
│ │ https://dgnl.ds/abc123                        │  │
│ │                                               │  │
│ │ [QRコード画像]    スキャン: 145回              │  │
│ │                   完了率: 29%                 │  │
│ │                                               │  │
│ │ [ダウンロード PNG] [ダウンロード SVG]          │  │
│ │ [統計を見る] [無効化]                          │  │
│ └───────────────────────────────────────────────┘  │
│                                                     │
│ ┌───────────────────────────────────────────────┐  │
│ │ 📱 名刺用QRコード                               │  │
│ │ ...                                           │  │
│ └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

### QRコード作成フォーム

```
┌─────────────────────────────────────────────────────┐
│ QRコードを作成                                       │
├─────────────────────────────────────────────────────┤
│                                                     │
│ 名前 *                                              │
│ [展示会2025                              ]          │
│                                                     │
│ UTMパラメータ（トラッキング用）                      │
│ UTM Source:   [booth                    ]          │
│ UTM Medium:   [qr                       ]          │
│ UTM Campaign: [tech_expo_2025           ]          │
│                                                     │
│ デザインカスタマイズ                                 │
│ カラー: [#1E40AF] [カラーピッカー]                  │
│ □ ロゴを埋め込む                                    │
│   ロゴURL: [https://...              ]             │
│                                                     │
│ フレーム: ( ) なし (•) Rounded ( ) Square          │
│                                                     │
│ ┌─────────────────┐                                │
│ │  QRコード       │  ← プレビュー                  │
│ │  プレビュー     │                                │
│ └─────────────────┘                                │
│                                                     │
│ [キャンセル]              [作成]                    │
└─────────────────────────────────────────────────────┘
```

### トラッキング統計画面

```
┌─────────────────────────────────────────────────────┐
│ QRコード統計: 展示会2025                             │
├─────────────────────────────────────────────────────┤
│                                                     │
│ 📊 概要                                             │
│ ┌─────────┬─────────┬─────────┬─────────┐         │
│ │ 総スキャン │ 診断開始 │ 診断完了 │ 完了率   │         │
│ │   145    │   67    │   42    │  29%    │         │
│ └─────────┴─────────┴─────────┴─────────┘         │
│                                                     │
│ 📈 スキャン数推移                                    │
│ [グラフ: 日別スキャン数]                             │
│                                                     │
│ 📱 デバイス別                                        │
│ iOS:     60 (41%)  ████████░░                      │
│ Android: 38 (26%)  █████░░░░░                      │
│ Other:   47 (33%)  ██████░░░░                      │
│                                                     │
│ 🌍 国別                                              │
│ 日本:     90 (62%)  ████████████░                   │
│ 米国:      8 (6%)   █░░░░░░░░░░░                   │
│ その他:   47 (32%)  ██████░░░░░░                   │
└─────────────────────────────────────────────────────┘
```

## Business Logic

### QRコード生成フロー

1. ユーザーがQRコード作成をリクエスト
2. 短縮コード（7文字の英数字）を生成
3. 短縮URL（https://dgnl.ds/{short_code}）を生成
4. UTMパラメータを埋め込んだフルURLを生成
5. QRコードライブラリでQR画像を生成
6. スタイル適用（カラー、ロゴ、フレーム）
7. 画像をS3/Cloudflareに保存
8. DBにQRCodeレコードを作成

### トラッキングフロー

1. ユーザーがQRコードをスキャン
2. 短縮URL（/r/{short_code}）にアクセス
3. サーバーが以下を記録:
   - User Agent解析（デバイス、OS、ブラウザ）
   - IP→地域情報（GeoIP）
   - タイムスタンプ
4. QRCodeScanレコードを作成
5. QRCode.scan_countをインクリメント
6. 診断ページにリダイレクト（UTMパラメータ付き）

### ファネル分析

- **スキャン**: QRCodeScan作成時
- **診断開始**: 最初の質問回答時に`assessment_started = True`
- **診断完了**: Response作成時に`assessment_completed = True`
- **リード作成**: Lead作成時に`lead_created = True`, `lead_id`を設定

## Technical Implementation

### QRコード生成ライブラリ

```python
# backend/app/services/qr_code_service.py
import qrcode
from PIL import Image, ImageDraw
import io

class QRCodeService:
    def generate_qr_code(
        self,
        url: str,
        color: str = "#000000",
        logo_url: str | None = None,
        frame: str = "none",
        size: int = 512
    ) -> bytes:
        # QRコード生成
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color=color, back_color="white")
        
        # ロゴ埋め込み
        if logo_url:
            logo = self._download_logo(logo_url)
            logo_size = size // 5
            logo = logo.resize((logo_size, logo_size))
            
            pos = ((size - logo_size) // 2, (size - logo_size) // 2)
            img.paste(logo, pos)
        
        # フレーム追加
        if frame != "none":
            img = self._add_frame(img, frame)
        
        # バイト配列に変換
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return buffer.getvalue()
```

### 短縮URL生成

```python
import secrets
import string

def generate_short_code(length: int = 7) -> str:
    """衝突の可能性が低い短縮コードを生成"""
    alphabet = string.ascii_letters + string.digits
    while True:
        short_code = ''.join(secrets.choice(alphabet) for _ in range(length))
        
        # DB で重複チェック
        existing = db.query(QRCode).filter(
            QRCode.short_code == short_code
        ).first()
        
        if not existing:
            return short_code
```

### リダイレクトエンドポイント

```python
# backend/app/api/v1/redirect.py
@router.get("/r/{short_code}")
async def redirect_qr_code(
    short_code: str,
    request: Request,
    db: Session = Depends(get_db)
):
    # QRコードを検索
    qr_code = db.query(QRCode).filter(
        QRCode.short_code == short_code,
        QRCode.enabled == True
    ).first()
    
    if not qr_code:
        raise HTTPException(404, "QR code not found")
    
    # トラッキング記録（非同期）
    await record_qr_scan(qr_code.id, request)
    
    # 診断ページにリダイレクト
    redirect_url = build_assessment_url(
        qr_code.assessment_id,
        qr_code.utm_source,
        qr_code.utm_medium,
        qr_code.utm_campaign
    )
    
    return RedirectResponse(url=redirect_url)
```

## Testing Strategy

### Unit Tests

- `QRCodeService.generate_qr_code()`: QRコード画像生成
- `generate_short_code()`: 短縮コード生成（重複なし）
- `build_assessment_url()`: UTMパラメータ付きURL生成

### Integration Tests

- QRコード作成API
- QRコード一覧取得API
- リダイレクトエンドポイント
- トラッキング統計API

### E2E Tests

- QRコード作成 → ダウンロード → スキャン → 診断完了 → 統計確認

## Implementation Notes

### 推定工数

- **バックエンド**: 3-5日
  - QRコード生成ロジック: 1日
  - API実装: 1日
  - トラッキングロジック: 1日
  - テスト: 1-2日

- **フロントエンド**: 3-5日
  - QRコード管理画面: 2日
  - 作成フォーム: 1日
  - 統計ダッシュボード: 1-2日

- **合計**: 1-2週間

### 技術スタック

- **QRコード生成**: `qrcode` (Python), `qrcode.react` (React)
- **画像処理**: Pillow (Python)
- **GeoIP**: MaxMind GeoLite2
- **User Agent解析**: `user-agents` (Python)
- **短縮URLドメイン**: `dgnl.ds` (要取得)

### 依存関係

```
# backend/requirements.txt
qrcode[pil]==7.4.2
pillow==10.1.0
user-agents==2.2.0
geoip2==4.7.0
```

```json
// frontend/package.json
{
  "dependencies": {
    "qrcode.react": "^3.1.0"
  }
}
```

## Related Specs

- [Multi-Channel Distribution](../../changes/2025-11-10-innovative-features/innovative-features.md#3-multi-channel-assessment-distribution)
- [Analytics Dashboard](./analytics-dashboard.md)
- [Assessment CRUD](./assessment-crud.md)

## Success Metrics

- QRコード生成成功率: 99%以上
- リダイレクトレスポンスタイム: 500ms以内
- QRコード→診断完了CVR: 20%以上（業界平均）

---

**Status**: 承認済み、実装待ち  
**Next Steps**: バックエンドAPI実装から開始
