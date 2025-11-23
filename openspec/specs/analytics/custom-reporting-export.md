# Custom Reporting & Export

**Feature ID**: ANALYTICS-REPORT-001
**Status**: Implemented
**Priority**: High (Enterprise Feature)
**Last Updated**: 2025-11-23

---

## 📋 Overview

DiagnoLeadsのカスタムレポートビルダーとエクスポート機能。テナントが独自のメトリクス・フィルター・グループ化を定義し、定期的なレポート生成・配信を自動化します。

### ビジネス価値

- **データドリブン経営**: テナント独自の KPI を可視化
- **営業効率化**: 定期レポートの自動生成・配信
- **ステークホルダー報告**: 経営層・営業チームへの定期報告
- **エンタープライズ要件**: 大企業顧客の必須機能

---

## 🎯 主要機能

### 1. カスタムレポート定義

ユーザーが以下を柔軟に設定可能：

| 設定項目 | 説明 | 例 |
|---------|------|-----|
| **メトリクス** | 集計する指標 | リード総数、平均スコア、成約率 |
| **フィルター** | データ絞り込み条件 | 期間、ステータス、スコア範囲 |
| **グループ化** | 集計軸 | ステータス別、業界別、日付別 |
| **ビジュアライゼーション** | 表示形式 | 棒グラフ、折れ線、円グラフ、テーブル |
| **ソート** | 並び順 | リード数降順、スコア昇順 |

### 2. レポートタイプ

| タイプ | 説明 | 用途 |
|--------|------|------|
| **custom** | 完全カスタマイズ | テナント独自の分析 |
| **lead_analysis** | リード分析テンプレート | 営業パイプライン分析 |
| **assessment_performance** | 診断パフォーマンステンプレート | 診断完了率・離脱率 |
| **conversion_funnel** | コンバージョンファネル | スキャン→診断→リード→成約 |
| **ai_insights** | AI分析レポート | AI生成診断の品質分析 |

### 3. スケジュール実行

| 頻度 | 説明 | 実行タイミング |
|-----|------|--------------|
| **daily** | 日次 | 毎日指定時刻 |
| **weekly** | 週次 | 毎週指定曜日・時刻 |
| **monthly** | 月次 | 毎月指定日・時刻 |
| **manual** | 手動 | オンデマンド実行 |

### 4. エクスポート形式

| 形式 | 用途 | 機能 |
|-----|------|------|
| **CSV** | データ分析 | UTF-8、動的列生成 |
| **Excel (XLSX)** | レポート配布 | 複数シート、スタイリング、自動列幅 |
| **PDF** | 印刷・プレゼン | セクション分割、表スタイル |

---

## 📊 データモデル

### Report

**テーブル**: `reports`

| フィールド | 型 | 制約 | 説明 |
|-----------|-----|-----|------|
| id | UUID | PK | レポートID |
| tenant_id | UUID | FK(Tenant), NOT NULL, INDEX | テナント所有 |
| name | String(255) | NOT NULL | レポート名 |
| description | Text | | レポート説明 |
| report_type | String(50) | DEFAULT 'custom' | レポートタイプ |
| config | JSON | NOT NULL, DEFAULT {} | レポート設定 |
| is_scheduled | Boolean | DEFAULT false, NOT NULL | スケジュール実行フラグ |
| schedule_config | JSON | | スケジュール設定 |
| last_generated_at | Timestamp | | 最終生成日時 |
| created_by | UUID | FK(User), SET NULL | 作成者 |
| is_public | Boolean | DEFAULT false, NOT NULL | テナント内公開フラグ |
| created_at | Timestamp | DEFAULT now(), NOT NULL | 作成日時 |
| updated_at | Timestamp | DEFAULT now(), NOT NULL | 更新日時 |

### Config JSON スキーマ

```json
{
  "metrics": [
    "leads_total",        // リード総数
    "conversion_rate",    // 成約率（%）
    "average_score",      // 平均スコア
    "hot_leads"          // ホットリード数
  ],
  "filters": {
    "date_range": {
      "start": "2025-01-01",
      "end": "2025-01-31"
    },
    "status": ["new", "qualified", "converted"],
    "score_range": {
      "min": 60,
      "max": 100
    }
  },
  "group_by": "status",    // status|industry|date|assessment
  "visualization": "bar_chart",  // bar_chart|line_chart|pie_chart|table
  "sort_by": "leads_total",
  "sort_order": "desc"    // asc|desc
}
```

### Schedule Config JSON スキーマ

```json
{
  "frequency": "weekly",     // daily|weekly|monthly
  "day_of_week": 1,         // Monday=0, Sunday=6
  "day_of_month": 1,        // 1-31
  "time": "09:00",          // HH:MM (24h format)
  "timezone": "Asia/Tokyo",
  "recipients": [
    "sales@example.com",
    "manager@example.com"
  ],
  "format": "xlsx"          // csv|xlsx|pdf
}
```

---

## 🔌 API仕様

### 1. カスタムレポート作成

```http
POST /api/v1/tenants/{tenant_id}/reports
Authorization: Bearer {token}
Content-Type: application/json
```

**リクエスト**:
```json
{
  "name": "月次営業レポート",
  "description": "営業チーム向け月次パフォーマンスレポート",
  "report_type": "lead_analysis",
  "config": {
    "metrics": ["leads_total", "conversion_rate", "average_score"],
    "filters": {
      "date_range": {"start": "2025-01-01", "end": "2025-01-31"},
      "status": ["new", "contacted", "qualified", "converted"]
    },
    "group_by": "status",
    "visualization": "bar_chart",
    "sort_by": "leads_total",
    "sort_order": "desc"
  },
  "is_scheduled": true,
  "schedule_config": {
    "frequency": "monthly",
    "day_of_month": 1,
    "time": "09:00",
    "timezone": "Asia/Tokyo",
    "recipients": ["sales@example.com"],
    "format": "xlsx"
  }
}
```

**レスポンス** (201 Created):
```json
{
  "id": "report_abc123",
  "tenant_id": "tenant_xyz",
  "name": "月次営業レポート",
  "report_type": "lead_analysis",
  "is_scheduled": true,
  "created_at": "2025-11-23T10:00:00Z"
}
```

**認証**: JWT必須
**認可**: Tenant Admin以上

---

### 2. レポート一覧取得

```http
GET /api/v1/tenants/{tenant_id}/reports?skip=0&limit=20
Authorization: Bearer {token}
```

**クエリパラメータ**:
| パラメータ | 型 | 説明 |
|-----------|-----|------|
| skip | Integer | ページネーション（デフォルト: 0） |
| limit | Integer | 取得件数（デフォルト: 20） |
| report_type | String | レポートタイプフィルター |
| is_scheduled | Boolean | スケジュールレポートのみ |
| is_public | Boolean | 公開レポートのみ |

**レスポンス**:
```json
{
  "total": 15,
  "skip": 0,
  "limit": 20,
  "items": [
    {
      "id": "report_abc123",
      "name": "月次営業レポート",
      "report_type": "lead_analysis",
      "is_scheduled": true,
      "last_generated_at": "2025-11-01T09:00:00Z",
      "created_by": "user_xyz",
      "created_at": "2025-10-15T10:00:00Z"
    }
  ]
}
```

---

### 3. レポート詳細取得

```http
GET /api/v1/tenants/{tenant_id}/reports/{report_id}
Authorization: Bearer {token}
```

**レスポンス**:
```json
{
  "id": "report_abc123",
  "tenant_id": "tenant_xyz",
  "name": "月次営業レポート",
  "description": "営業チーム向け月次パフォーマンスレポート",
  "report_type": "lead_analysis",
  "config": {...},
  "is_scheduled": true,
  "schedule_config": {...},
  "last_generated_at": "2025-11-01T09:00:00Z",
  "created_by": "user_xyz",
  "is_public": false,
  "created_at": "2025-10-15T10:00:00Z",
  "updated_at": "2025-10-15T10:00:00Z"
}
```

---

### 4. レポート更新

```http
PUT /api/v1/tenants/{tenant_id}/reports/{report_id}
Authorization: Bearer {token}
Content-Type: application/json
```

**リクエスト**: レポート作成と同形式

**レスポンス**: 更新後のレポート詳細

---

### 5. レポート削除

```http
DELETE /api/v1/tenants/{tenant_id}/reports/{report_id}
Authorization: Bearer {token}
```

**レスポンス**: 204 No Content

---

### 6. レポート実行（データ生成）

```http
POST /api/v1/tenants/{tenant_id}/reports/{report_id}/execute
Authorization: Bearer {token}
```

**レスポンス**:
```json
{
  "report_id": "report_abc123",
  "execution_time": "2025-11-23T10:30:00Z",
  "data_points": [
    {
      "label": "new",
      "leads_total": 145,
      "conversion_rate": 0.15,
      "average_score": 42.3
    },
    {
      "label": "contacted",
      "leads_total": 87,
      "conversion_rate": 0.28,
      "average_score": 58.7
    },
    {
      "label": "qualified",
      "leads_total": 52,
      "conversion_rate": 0.45,
      "average_score": 71.2
    },
    {
      "label": "converted",
      "leads_total": 23,
      "conversion_rate": 1.0,
      "average_score": 85.4
    }
  ],
  "summary": {
    "total_leads": 307,
    "overall_conversion_rate": 0.075,
    "overall_average_score": 58.9
  }
}
```

**注意**: 仕様では `GET /reports/custom/{id}/data` だったが、実装は `POST .../execute`（状態変化を伴うため適切）

---

### 7. レポートエクスポート

```http
POST /api/v1/tenants/{tenant_id}/reports/{report_id}/export?format=xlsx
Authorization: Bearer {token}
```

**クエリパラメータ**:
- `format`: `csv` | `xlsx` | `pdf` (デフォルト: `csv`)

**レスポンス** (200 OK):
```
Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
Content-Disposition: attachment; filename="monthly_sales_report_20251123.xlsx"

[バイナリデータ]
```

---

## 📄 エクスポート形式の詳細

### CSV エクスポート

**特徴**:
- UTF-8エンコード
- 動的列生成（メトリクスから自動抽出）
- カンマ区切り
- ヘッダー行付き

**例**:
```csv
label,leads_total,conversion_rate,average_score
new,145,0.15,42.3
contacted,87,0.28,58.7
qualified,52,0.45,71.2
converted,23,1.0,85.4
```

---

### Excel (XLSX) エクスポート

**特徴**:
- 複数シート構成:
  - **"Report Data"**: メインデータテーブル
  - **"Summary"**: 要約統計
  - **"Configuration"**: レポート設定
- スタイリング:
  - ヘッダー行: 青色背景 (#4472C4) + 白文字 + ボールド
  - 自動列幅調整
  - 数値フォーマット: 小数点2位 (`0.00`)
  - パーセント表示: `0.00%`

**実装**: openpyxl ライブラリ

---

### PDF エクスポート

**特徴**:
- セクション構成:
  1. **タイトル + 生成時刻**
  2. **要約統計テーブル**
  3. **詳細データテーブル**
  4. **レポート設定ページ**（ページ区切り後）
- 表スタイル:
  - グリッド線
  - 背景色（交互: #E0E0E0）
  - 右寄せセンタリング
- フォント: Helvetica
- ページサイズ: A4

**実装**: reportlab ライブラリ

---

## 🧮 レポートメトリクス

### リード分析メトリクス

| メトリクス | 説明 | 計算式 |
|-----------|------|--------|
| `leads_total` | リード総数 | COUNT(*) |
| `average_score` | 平均スコア | AVG(score) |
| `conversion_rate` | 成約率（%） | (converted / total) * 100 |
| `hot_leads` | ホットリード数 | COUNT(score >= 61) |
| `warm_leads` | ウォームリード数 | COUNT(score BETWEEN 31 AND 60) |
| `cold_leads` | コールドリード数 | COUNT(score <= 30) |

### 診断分析メトリクス

| メトリクス | 説明 | 計算式 |
|-----------|------|--------|
| `assessments_total` | 診断総数 | COUNT(*) |
| `published_count` | 公開済み数 | COUNT(status='published') |
| `draft_count` | 下書き数 | COUNT(status='draft') |
| `ai_generated_count` | AI生成数 | COUNT(ai_generated='ai') |
| `manual_created_count` | 手動作成数 | COUNT(ai_generated='manual') |

---

## 🔧 ビジネスロジック

### レポート実行フロー

1. **設定解析**: `config` JSON を解析
2. **フィルター適用**: `filters` に基づきクエリ構築
3. **データ集計**: `group_by` でグループ化、`metrics` で集計
4. **ソート**: `sort_by`, `sort_order` で並び替え
5. **サマリー計算**: 全体統計を算出
6. **結果返却**: JSON形式で返却

### グループ化オプション

| group_by | 説明 | SQL例 |
|----------|------|-------|
| `status` | ステータス別 | GROUP BY status |
| `industry` | 業界別 | GROUP BY industry |
| `date` | 日付別（トレンド） | GROUP BY DATE(created_at) |
| `assessment` | 診断別 | GROUP BY assessment_id |
| `ai_generated` | AI生成 vs 手動 | GROUP BY ai_generated |

### フィルター処理

```python
def _apply_lead_filters(query, filters):
    # 期間フィルター
    if "date_range" in filters:
        query = query.filter(
            Lead.created_at >= filters["date_range"]["start"],
            Lead.created_at <= filters["date_range"]["end"]
        )

    # ステータスフィルター
    if "status" in filters:
        query = query.filter(Lead.status.in_(filters["status"]))

    # スコア範囲フィルター
    if "score_range" in filters:
        query = query.filter(
            Lead.score >= filters["score_range"]["min"],
            Lead.score <= filters["score_range"]["max"]
        )

    return query
```

---

## 🔄 スケジュール実行（未実装）

### 実行エンジン

**候補**:
- Trigger.dev（非同期ジョブ実行）
- Celery（Pythonタスクキュー）
- GitHub Actions（scheduled workflow）

### 実行フロー

1. **スケジューラー**: 指定時刻にレポート実行をトリガー
2. **レポート実行**: `execute_report()` 実行
3. **エクスポート**: `schedule_config.format` に基づきエクスポート
4. **メール送信**: `schedule_config.recipients` にメール配信
5. **`last_generated_at` 更新**: 実行時刻を記録

---

## 🧪 テスト

### 実装済みテスト

- `backend/tests/test_report_service.py` - ReportService テスト
- `backend/tests/test_reports_api.py` - API エンドポイントテスト

### テストケース

- レポート作成・更新・削除
- レポート実行（リード分析、診断分析）
- フィルタリング（期間、ステータス、スコア範囲）
- グループ化（ステータス別、日付別）
- エクスポート（CSV/Excel/PDF）

### カバレッジ

- サービス層: 85%
- API層: 90%

---

## 📂 実装ファイル

| ファイル | 説明 |
|---------|------|
| `/backend/app/models/report.py` | Report モデル定義 |
| `/backend/app/services/report_service.py` | レポートサービス（14.3KB） |
| `/backend/app/services/report_export_service.py` | エクスポートサービス |
| `/backend/app/api/v1/reports.py` | APIエンドポイント（350行、7エンドポイント） |
| `/backend/app/schemas/report.py` | Pydantic スキーマ |

---

## 🚀 将来の改善

1. **グラフ生成**: matplotlib/plotly でグラフ画像生成
2. **ダッシュボード統合**: フロントエンドでのビジュアライゼーション
3. **スケジュール実行**: Trigger.dev 統合
4. **メール配信**: SendGrid/Mailgun 統合
5. **レポートテンプレート**: 業界別テンプレート（IT/製造/医療等）
6. **AI 分析**: Claude による自動インサイト生成
7. **Slack/Teams 配信**: チャットツールへの自動投稿
8. **データウェアハウス統合**: BigQuery/Snowflake エクスポート

---

## 🔗 関連仕様

- [Analytics Dashboard](./analytics-dashboard.md)
- [Lead Management](../features/lead-management.md)
- [Assessment CRUD](../features/assessment-crud.md)
- [Advanced Reporting & BI](../features/advanced-reporting-bi.md)

---

**実装ステータス**: ✅ バックエンド実装完了（フロントエンドUI未実装）
