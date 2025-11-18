# Custom Reports Feature

**実装日**: 2025-11-18
**ステータス**: ✅ バックエンド完了 / ⏳ フロントエンド未実装
**関連機能**: F - カスタムレポート機能

## 概要

DiagnoLeadsのカスタムレポート機能により、ユーザーは独自のレポートを作成・保存・実行し、PDF/Excel/CSV形式でエクスポートできます。これにより、営業チームやマネージャーは自分のニーズに合わせたデータ分析とレポーティングが可能になります。

## 実装内容

### 1. Reportデータモデル

**ファイル**: `backend/app/models/report.py`

#### モデル構造

```python
class Report(Base):
    id: UUID                      # レポートID
    tenant_id: UUID               # テナントID（マルチテナント分離）
    name: str                     # レポート名
    description: str              # 説明
    report_type: str              # custom|lead_analysis|assessment_performance|conversion_funnel|ai_insights

    # レポート設定（JSON）
    config: Dict[str, Any]        # メトリクス、フィルター、グループ化、可視化設定

    # スケジューリング（オプション）
    is_scheduled: bool            # スケジュール有効/無効
    schedule_config: Dict         # 頻度、時刻、タイムゾーン、受信者
    last_generated_at: datetime   # 最終生成日時

    # 所有権と可視性
    created_by: UUID              # 作成者
    is_public: bool               # テナント内全ユーザーに公開するか

    created_at: datetime
    updated_at: datetime
```

#### config フィールド構造

```json
{
  "metrics": ["leads_total", "conversion_rate", "average_score"],
  "filters": {
    "date_range": {"start": "2024-01-01", "end": "2024-12-31"},
    "status": ["new", "qualified"],
    "score_range": {"min": 60, "max": 100}
  },
  "group_by": "status",  // status|industry|date|assessment
  "visualization": "bar_chart",  // bar_chart|line_chart|pie_chart|table
  "sort_by": "leads_total",
  "sort_order": "desc"
}
```

### 2. レポートスキーマ

**ファイル**: `backend/app/schemas/report.py`

#### 主要スキーマ

- **ReportCreate**: 新規レポート作成リクエスト
- **ReportUpdate**: レポート更新リクエスト
- **ReportResponse**: レポート定義レスポンス
- **ReportResultsResponse**: レポート実行結果レスポンス
- **ExportFormat**: エクスポート形式指定

### 3. ReportService（レポート生成・管理）

**ファイル**: `backend/app/services/report_service.py`

#### 主要機能

##### CRUD操作

- `create()`: 新規レポート作成
- `get_by_id()`: レポート取得（テナントチェック付き）
- `list_reports()`: レポート一覧取得（公開/プライベートフィルタリング）
- `update()`: レポート更新
- `delete()`: レポート削除

##### レポート実行

- `execute_report()`: レポート実行のメインメソッド
  - レポートタイプに応じて適切な実行メソッドを呼び出し
  - last_generated_at を更新

- `_execute_lead_analysis_report()`: リード分析レポート実行
- `_execute_assessment_performance_report()`: 診断パフォーマンスレポート実行
- `_execute_custom_report()`: カスタムレポート実行（複数データソース）

##### フィルタリング

- `_apply_lead_filters()`: リードクエリにフィルター適用
  - 日付範囲、ステータス、スコア範囲
- `_apply_assessment_filters()`: 診断クエリにフィルター適用
  - 日付範囲、ステータス、AI生成フラグ

##### グループ化と集計

- `_group_leads()`: リードをグループ化して集計
- `_group_assessments()`: 診断をグループ化して集計
- `_aggregate_leads()`: リードメトリクスの集計
- `_aggregate_assessments()`: 診断メトリクスの集計

##### サマリー計算

- `_calculate_lead_summary()`: リードサマリー統計
- `_calculate_assessment_summary()`: 診断サマリー統計

#### 対応メトリクス

**リードメトリクス**:
- `leads_total`: 総リード数
- `average_score`: 平均スコア
- `conversion_rate`: コンバージョン率
- `hot_leads`: ホットリード数（スコア61以上）

**診断メトリクス**:
- `assessments_total`: 総診断数
- `published_count`: 公開済み診断数
- `ai_generated_count`: AI生成診断数

### 4. ReportExportService（エクスポート機能）

**ファイル**: `backend/app/services/report_export_service.py`

#### エクスポート形式

##### CSV Export
- **メソッド**: `export_to_csv()`
- **依存**: Python標準ライブラリ（csv）
- **出力**: UTF-8エンコードのCSV
- **特徴**: シンプル、軽量、Excel/スプレッドシートで開ける

```python
def export_to_csv(report_name, data_points) -> bytes:
    # Header: Label + メトリクス名
    # Rows: ラベル + 各メトリクスの値
    return csv_bytes
```

##### Excel Export
- **メソッド**: `export_to_excel()`
- **依存**: `openpyxl` ライブラリ
- **出力**: XLSX形式
- **特徴**:
  - 3つのシート: Report Data, Summary, Configuration
  - スタイリング（ヘッダー色、フォント太字）
  - 数値フォーマット（小数点2桁）
  - 列幅自動調整

```python
def export_to_excel(report_name, data_points, summary, config) -> bytes:
    # Sheet 1: レポートデータ（タイトル、タイムスタンプ、データテーブル）
    # Sheet 2: サマリー統計
    # Sheet 3: レポート設定
    return xlsx_bytes
```

##### PDF Export
- **メソッド**: `export_to_pdf()`
- **依存**: `reportlab` ライブラリ
- **出力**: PDF形式（A4サイズ）
- **特徴**:
  - プロフェッショナルなレイアウト
  - タイトル、タイムスタンプ
  - サマリー統計テーブル
  - 詳細データテーブル
  - 設定情報（別ページ）
  - テーブルスタイリング（ヘッダー背景、行背景色交互）

```python
def export_to_pdf(report_name, data_points, summary, config, include_charts) -> bytes:
    # Page 1: タイトル、サマリー、データテーブル
    # Page 2: レポート設定
    return pdf_bytes
```

### 5. Report API エンドポイント

**ファイル**: `backend/app/api/v1/reports.py`

#### エンドポイント一覧

| メソッド | パス | 機能 |
|---------|------|------|
| POST | `/tenants/{tenant_id}/reports` | レポート作成 |
| GET | `/tenants/{tenant_id}/reports` | レポート一覧取得 |
| GET | `/tenants/{tenant_id}/reports/{report_id}` | レポート取得 |
| PUT | `/tenants/{tenant_id}/reports/{report_id}` | レポート更新 |
| DELETE | `/tenants/{tenant_id}/reports/{report_id}` | レポート削除 |
| POST | `/tenants/{tenant_id}/reports/{report_id}/execute` | レポート実行 |
| POST | `/tenants/{tenant_id}/reports/{report_id}/export?format={format}` | レポートエクスポート |

#### セキュリティ

- すべてのエンドポイントで JWT認証必須
- テナントIDによるマルチテナント分離
- ユーザーは自分のテナントのレポートのみアクセス可能
- プライベートレポートは作成者のみアクセス可能

### 6. データベースマイグレーション

**必要なマイグレーション**:

```sql
CREATE TABLE reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    report_type VARCHAR(50) NOT NULL DEFAULT 'custom',
    config JSONB NOT NULL DEFAULT '{}',
    is_scheduled BOOLEAN NOT NULL DEFAULT FALSE,
    schedule_config JSONB,
    last_generated_at TIMESTAMP,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    is_public BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_reports_tenant_id ON reports(tenant_id);
CREATE INDEX idx_reports_created_by ON reports(created_by);
CREATE INDEX idx_reports_is_public ON reports(is_public);
```

## 使用方法

### API使用例

#### 1. レポート作成

```bash
POST /api/v1/tenants/{tenant_id}/reports

{
  "name": "月次リード分析レポート",
  "description": "月ごとのリード獲得状況と成約率を分析",
  "report_type": "lead_analysis",
  "config": {
    "metrics": ["leads_total", "conversion_rate", "average_score"],
    "filters": {
      "date_range": {
        "start": "2024-01-01",
        "end": "2024-12-31"
      }
    },
    "group_by": "date",
    "visualization": "line_chart",
    "sort_by": "date",
    "sort_order": "asc"
  },
  "is_public": true
}
```

#### 2. レポート実行

```bash
POST /api/v1/tenants/{tenant_id}/reports/{report_id}/execute

# レスポンス
{
  "report_id": "uuid",
  "report_name": "月次リード分析レポート",
  "generated_at": "2024-11-18T10:30:00Z",
  "config": {...},
  "data_points": [
    {
      "label": "2024-01",
      "values": {
        "leads_total": 45,
        "conversion_rate": 22.5,
        "average_score": 67.8
      }
    },
    {
      "label": "2024-02",
      "values": {
        "leads_total": 52,
        "conversion_rate": 25.0,
        "average_score": 71.2
      }
    }
  ],
  "summary": {
    "period": "custom",
    "total_leads": 97,
    "overall_average_score": 69.5,
    "overall_conversion_rate": 23.75
  },
  "total_records": 97
}
```

#### 3. レポートエクスポート

```bash
# CSV
POST /api/v1/tenants/{tenant_id}/reports/{report_id}/export?format=csv

# Excel
POST /api/v1/tenants/{tenant_id}/reports/{report_id}/export?format=xlsx

# PDF
POST /api/v1/tenants/{tenant_id}/reports/{report_id}/export?format=pdf

# レスポンス: ファイルダウンロード
Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
Content-Disposition: attachment; filename="月次リード分析レポート.xlsx"
```

#### 4. レポート一覧取得

```bash
# 公開レポートのみ
GET /api/v1/tenants/{tenant_id}/reports

# 公開レポート + 自分のプライベートレポート
GET /api/v1/tenants/{tenant_id}/reports?include_private=true
```

## 技術仕様

### ファイル構成

```
backend/app/
├── models/
│   ├── report.py                 # 新規: Reportモデル
│   ├── tenant.py                 # 更新: reportsリレーションシップ追加
│   └── __init__.py               # 更新: Reportインポート追加
├── schemas/
│   └── report.py                 # 新規: レポートスキーマ
├── services/
│   ├── report_service.py         # 新規: レポート生成・管理
│   └── report_export_service.py  # 新規: エクスポート機能
├── api/v1/
│   └── reports.py                # 新規: Report APIエンドポイント
```

### 依存ライブラリ

**必須**:
- SQLAlchemy（既存）
- FastAPI（既存）
- Pydantic（既存）

**エクスポート機能用**:
```bash
# Excel export
pip install openpyxl

# PDF export
pip install reportlab

# オプション: 高度なExcel機能
pip install pandas
```

### データフロー

```
1. クライアント → POST /api/v1/tenants/{tenant_id}/reports
   ↓ (ReportCreate)

2. reports.py → ReportService.create()
   ↓

3. ReportService → Reportモデル作成 → DB保存
   ↓

4. クライアント → POST /api/v1/tenants/{tenant_id}/reports/{report_id}/execute
   ↓

5. ReportService.execute_report()
   ↓ report_type に応じて分岐
   ↓ _execute_lead_analysis_report() / _execute_assessment_performance_report() など

6. データ集計・フィルタリング・グループ化
   ↓ _apply_filters(), _group_*(), _aggregate_*()

7. results → data_points + summary
   ↓

8. クライアント → POST /api/v1/tenants/{tenant_id}/reports/{report_id}/export?format=xlsx
   ↓

9. ReportExportService.export_to_excel()
   ↓ openpyxl でExcelファイル生成

10. バイナリファイルダウンロード → クライアント
```

## レポートタイプ

### 1. Lead Analysis Report

**用途**: リード分析とセールスパフォーマンス

**メトリクス**:
- leads_total
- average_score
- conversion_rate
- hot_leads

**フィルター**:
- date_range
- status (new, contacted, qualified, converted, disqualified)
- score_range

**グループ化**:
- status
- date
- industry (将来実装)

### 2. Assessment Performance Report

**用途**: 診断コンテンツのパフォーマンス分析

**メトリクス**:
- assessments_total
- published_count
- ai_generated_count

**フィルター**:
- date_range
- status (draft, published, archived)
- ai_generated (ai, manual, hybrid)

**グループ化**:
- status
- date
- ai_generated

### 3. Custom Report

**用途**: 複数データソースの組み合わせ

リードと診断の両方のメトリクスを含むカスタムレポート。

## 今後の拡張案

### Phase 2: スケジュールレポート

**機能**:
- 定期的な自動レポート生成（daily/weekly/monthly）
- メール配信機能
- Trigger.dev との統合

**実装**:
```python
# backend/app/services/scheduled_report_service.py
class ScheduledReportService:
    def generate_scheduled_reports(self):
        # すべてのis_scheduled=Trueレポートを取得
        # スケジュールに基づいて実行
        # 結果をメール送信
```

### Phase 3: 高度なビジュアライゼーション

**機能**:
- インタラクティブなチャート（Chart.js, Recharts）
- PDFへのチャート埋め込み（matplotlib + reportlab）
- ダッシュボードウィジェット

### Phase 4: AI-powered インサイト

**機能**:
- Claude APIでレポートデータを分析
- トレンド検出と異常検知
- 自動レコメンデーション生成

**例**:
```python
async def generate_ai_insights(report_results):
    prompt = f"以下のレポートデータを分析し、重要なトレンドと推奨アクションを提示してください: {report_results}"
    insights = await claude_api.analyze(prompt)
    return insights
```

### Phase 5: レポートテンプレート

**機能**:
- プリセットレポートテンプレート
- 業界別ベストプラクティステンプレート
- ワンクリックレポート作成

### Phase 6: データエクスポートの拡張

**機能**:
- Google Sheetsへの直接エクスポート
- Power BI / Tableau 連携
- API経由のデータフィード

## テスト方法

### 1. 単体テスト

```python
# tests/test_report_service.py
import pytest
from app.services.report_service import ReportService

def test_create_report(db_session, test_tenant, test_user):
    service = ReportService(db_session)
    report_data = ReportCreate(
        name="Test Report",
        report_type="lead_analysis",
        config=ReportConfig(metrics=["leads_total"])
    )

    report = service.create(report_data, test_tenant.id, test_user.id)

    assert report.name == "Test Report"
    assert report.tenant_id == test_tenant.id

def test_execute_report_filters(db_session, test_tenant):
    # リードデータをセットアップ
    # レポート実行
    # フィルタリング結果を検証
    pass
```

### 2. API統合テスト

```python
# tests/test_reports_api.py
def test_create_report_api(client, auth_headers, tenant_id):
    response = client.post(
        f"/api/v1/tenants/{tenant_id}/reports",
        json={
            "name": "API Test Report",
            "report_type": "lead_analysis",
            "config": {"metrics": ["leads_total"]}
        },
        headers=auth_headers
    )

    assert response.status_code == 201
    assert response.json()["name"] == "API Test Report"

def test_export_report_csv(client, auth_headers, tenant_id, report_id):
    response = client.post(
        f"/api/v1/tenants/{tenant_id}/reports/{report_id}/export?format=csv",
        headers=auth_headers
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv"
```

### 3. エクスポート機能テスト

```python
# tests/test_report_export.py
from app.services.report_export_service import ReportExportService

def test_csv_export():
    service = ReportExportService()
    data_points = [
        {"label": "Jan", "values": {"leads": 10}},
        {"label": "Feb", "values": {"leads": 15}}
    ]

    csv_bytes = service.export_to_csv("Test", data_points)
    csv_text = csv_bytes.decode('utf-8')

    assert "Label,leads" in csv_text
    assert "Jan,10" in csv_text

def test_excel_export():
    # openpyxl が必要
    service = ReportExportService()
    # ... テストロジック
```

## トラブルシューティング

### よくある問題

**Q: Excel/PDFエクスポートで ImportError が発生する**

A: 必要なライブラリをインストールしてください:
```bash
pip install openpyxl reportlab
```

**Q: レポート実行が遅い**

A: 以下を確認してください:
- フィルターでデータ範囲を絞る
- データベースインデックスの確認（tenant_id, created_at）
- 大量データの場合はページネーションを検討

**Q: 日本語ファイル名が文字化けする**

A: ファイル名のエンコーディング処理を確認してください:
```python
filename = f"{report.name.replace(' ', '_')}.csv"
# URLエンコードが必要な場合:
from urllib.parse import quote
filename = quote(filename)
```

**Q: PDF生成で日本語フォントが表示されない**

A: reportlabで日本語フォントを設定してください:
```python
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# 日本語フォント登録
pdfmetrics.registerFont(TTFont('Japanese', 'path/to/font.ttf'))
```

## まとめ

このカスタムレポート機能により、DiagnoLeadsユーザーは:

**実装完了**:
- ✅ カスタムレポートの作成・保存・管理
- ✅ リード分析レポート
- ✅ 診断パフォーマンスレポート
- ✅ フィルタリングとグループ化
- ✅ CSV/Excel/PDFエクスポート
- ✅ マルチテナント分離とセキュリティ
- ✅ 公開/プライベートレポート機能

**今後実装予定**:
- ⏳ スケジュールレポート（自動生成・配信）
- ⏳ フロントエンドレポートビルダーUI
- ⏳ 高度なビジュアライゼーション
- ⏳ AI-powered インサイト生成

---

**実装者**: Claude Code
**レビュー**: Pending
**関連ドキュメント**:
- [AI Lead Analysis Enhancements](./AI_LEAD_ANALYSIS_ENHANCEMENTS.md)
- [AI Assessment Generation Improvements](./AI_ASSESSMENT_GENERATION_IMPROVEMENTS.md)
- [Google Analytics Complete Summary](./GOOGLE_ANALYTICS_COMPLETE_SUMMARY.md)
