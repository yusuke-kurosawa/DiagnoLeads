# Report Export Formats

**Feature ID**: ANALYTICS-EXPORT-002
**Status**: Implemented
**Priority**: Medium (Data Export)
**Last Updated**: 2025-11-23

---

## 📋 Overview

DiagnoLeadsのレポートエクスポート機能。CSV、Excel（XLSX）、PDF形式でカスタムレポートを出力し、テナントがデータ分析・共有を行えます。

### ビジネス価値

- **データ分析**: Excel/CSVで高度な分析が可能
- **レポーティング**: PDF で経営層・クライアントへ共有
- **バックアップ**: データの外部保存
- **統合**: BIツール（Tableau、Looker等）へのデータ連携

---

## 🎯 対応フォーマット（3種類）

| 形式 | 拡張子 | 用途 | 実装状況 |
|------|--------|------|---------|
| **CSV** | .csv | データ分析、BIツール連携 | ✅ 実装済み |
| **Excel** | .xlsx | 高度な分析、グラフ作成 | ✅ 実装済み |
| **PDF** | .pdf | 印刷、プレゼンテーション | ⏸️ 部分実装 |

---

## 📊 CSV エクスポート

### 特徴

- **軽量**: 最小ファイルサイズ
- **互換性**: 全ツールで読み込み可能
- **UTF-8エンコード**: 日本語対応

### データ構造

```csv
Label,leads_total,conversion_rate,average_score
2025-01,120,0.18,67.5
2025-02,145,0.22,72.3
2025-03,138,0.20,69.8
```

**ヘッダー行**: Label + メトリクス名（ソート済み）
**データ行**: ラベル + 各メトリクスの値

### 実装

```python
def export_to_csv(self, report_name: str, data_points: List[Dict[str, Any]]) -> bytes:
    """CSV形式でエクスポート"""
    output = io.StringIO()
    writer = csv.writer(output)

    # メトリクス名を抽出
    metrics = set()
    for dp in data_points:
        metrics.update(dp.get("values", {}).keys())

    # ヘッダー行
    header = ["Label"] + sorted(list(metrics))
    writer.writerow(header)

    # データ行
    for dp in data_points:
        label = dp.get("label", "Unknown")
        values = dp.get("values", {})
        row = [label] + [values.get(metric, 0) for metric in sorted(metrics)]
        writer.writerow(row)

    return output.getvalue().encode("utf-8")
```

---

## 📈 Excel (XLSX) エクスポート

### 特徴

- **マルチシート**: データ、サマリー、設定の3シート
- **スタイリング**: ヘッダー色、フォント、数値フォーマット
- **列幅自動調整**: 読みやすさ向上

### シート構成

#### 1. Report Data シート

| Label | Leads Total | Conversion Rate | Average Score |
|-------|------------|-----------------|---------------|
| 2025-01 | 120 | 0.18 | 67.50 |
| 2025-02 | 145 | 0.22 | 72.30 |

**スタイル**:
- タイトル行（A1）: サイズ16、太字
- 生成日時（A2）: グレーテキスト
- ヘッダー行（row 4）: 太字、ブルー背景（#CCE5FF）
- 数値フォーマット: 小数点2桁（0.00）

#### 2. Summary シート

| Metric | Value |
|--------|-------|
| Total Leads | 403 |
| Average Score | 69.87 |
| Conversion Rate | 0.20 |

**スタイル**:
- タイトル行（A1）: サイズ14、太字
- メトリクス名: 太字

#### 3. Configuration シート

| Setting | Value |
|---------|-------|
| Report Type | monthly_leads |
| Date Range | 2025-01-01 to 2025-03-31 |
| Group By | month |
| Filters | status=qualified |

### 実装

```python
def export_to_excel(
    self,
    report_name: str,
    data_points: List[Dict[str, Any]],
    summary: Dict[str, Any],
    config: Dict[str, Any],
) -> bytes:
    """Excel形式でエクスポート"""
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill

    wb = Workbook()

    # データシート
    ws_data = wb.active
    ws_data.title = "Report Data"
    ws_data["A1"] = report_name
    ws_data["A1"].font = Font(size=16, bold=True)

    # ヘッダー行（太字、背景色）
    ws_data[f"A4"].font = Font(bold=True)
    ws_data[f"A4"].fill = PatternFill(
        start_color="CCE5FF",
        end_color="CCE5FF",
        fill_type="solid"
    )

    # サマリーシート
    ws_summary = wb.create_sheet("Summary")
    # ...

    # 設定シート
    ws_config = wb.create_sheet("Configuration")
    # ...

    # バイト列に変換
    output = io.BytesIO()
    wb.save(output)
    return output.getvalue()
```

**依存関係**: `openpyxl` （`pip install openpyxl`）

---

## 📄 PDF エクスポート（部分実装）

### 特徴

- **プレゼンテーション向け**: 印刷、メール共有
- **ブランディング**: ロゴ、カラースキーム
- **レイアウト**: レポートタイトル、表、グラフ、サマリー

### 実装オプション

#### Option 1: ReportLab

```python
def export_to_pdf(
    self,
    report_name: str,
    data_points: List[Dict[str, Any]],
    summary: Dict[str, Any],
) -> bytes:
    """PDF形式でエクスポート（ReportLab）"""
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Table, Paragraph
    from reportlab.lib.styles import getSampleStyleSheet

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []

    # タイトル
    styles = getSampleStyleSheet()
    title = Paragraph(report_name, styles['Title'])
    elements.append(title)

    # データテーブル
    table_data = [["Label", "Leads", "Score"]]
    for dp in data_points:
        table_data.append([
            dp["label"],
            dp["values"]["leads_total"],
            dp["values"]["average_score"],
        ])

    table = Table(table_data)
    elements.append(table)

    doc.build(elements)
    return buffer.getvalue()
```

**依存関係**: `reportlab` （`pip install reportlab`）

#### Option 2: WeasyPrint

HTML → PDF変換（よりリッチなデザイン可能）:

```python
def export_to_pdf_weasyprint(
    self,
    report_name: str,
    html_template: str,
) -> bytes:
    """PDF形式でエクスポート（WeasyPrint）"""
    from weasyprint import HTML

    html_content = f"""
    <html>
    <style>
        h1 {{ color: #3b82f6; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th {{ background-color: #3b82f6; color: white; padding: 10px; }}
        td {{ border: 1px solid #ddd; padding: 8px; }}
    </style>
    <body>
        <h1>{report_name}</h1>
        <table>...</table>
    </body>
    </html>
    """

    pdf_bytes = HTML(string=html_content).write_pdf()
    return pdf_bytes
```

**依存関係**: `weasyprint` （`pip install weasyprint`）

---

## 🔧 API統合

### カスタムレポートAPIからの利用

```python
# /backend/app/api/v1/reports.py
from app.services.report_export_service import ReportExportService

@router.post("/tenants/{tenant_id}/reports/{report_id}/export")
async def export_report(
    tenant_id: UUID,
    report_id: UUID,
    format: str = Query("csv", regex="^(csv|xlsx|pdf)$"),
    db: Session = Depends(get_db),
):
    """レポートをエクスポート"""
    # レポート実行
    result = await report_service.execute_report(report_id, tenant_id)

    # エクスポート
    export_service = ReportExportService()

    if format == "csv":
        file_bytes = export_service.export_to_csv(
            report_name=result["name"],
            data_points=result["data_points"],
        )
        media_type = "text/csv"
        filename = f"{result['name']}.csv"

    elif format == "xlsx":
        file_bytes = export_service.export_to_excel(
            report_name=result["name"],
            data_points=result["data_points"],
            summary=result["summary"],
            config=result["config"],
        )
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        filename = f"{result['name']}.xlsx"

    elif format == "pdf":
        file_bytes = export_service.export_to_pdf(...)
        media_type = "application/pdf"
        filename = f"{result['name']}.pdf"

    return Response(
        content=file_bytes,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
```

---

## 📊 ファイルサイズ制限

### 制限値

```python
# /backend/app/core/constants.py
class FileSizeLimit:
    REPORT_EXPORT_MAX = 50 * 1024 * 1024  # 50MB
```

### サイズ見積もり

| データ量 | CSV | XLSX | PDF |
|---------|-----|------|-----|
| 100行 | 5KB | 15KB | 25KB |
| 1,000行 | 50KB | 120KB | 200KB |
| 10,000行 | 500KB | 1.2MB | 2MB |
| 100,000行 | 5MB | 12MB | 20MB |

---

## 🚀 将来の改善

### 1. グラフ・チャート埋め込み

```python
# Excelにグラフ追加
from openpyxl.chart import BarChart, Reference

chart = BarChart()
chart.title = "Monthly Leads"
data = Reference(ws_data, min_col=2, min_row=4, max_row=row)
chart.add_data(data, titles_from_data=True)
ws_data.add_chart(chart, "E5")
```

### 2. 自動スケジュールエクスポート

```python
class ScheduledExportService:
    def schedule_export(self, report_id, format, frequency, recipients):
        """定期エクスポート + メール送信"""
        # 毎月1日にExcelエクスポート → メール送信
```

### 3. クラウドストレージ連携

```python
# S3/GCS へアップロード
def export_to_s3(self, file_bytes, tenant_id, report_name, format):
    s3_client.put_object(
        Bucket="diagnoleads-exports",
        Key=f"{tenant_id}/{report_name}.{format}",
        Body=file_bytes,
    )
    return presigned_url
```

### 4. カスタムテンプレート

テナントごとのExcel/PDFテンプレート：

```python
class TenantReportTemplate:
    def get_template(self, tenant_id, format):
        # テナント固有のロゴ、カラー、レイアウト
```

### 5. 圧縮エクスポート

大量データは ZIP圧縮：

```python
import zipfile

with zipfile.ZipFile("export.zip", "w", zipfile.ZIP_DEFLATED) as zf:
    zf.writestr("report.csv", csv_bytes)
    zf.writestr("summary.txt", summary_text)
```

---

## 📂 実装ファイル

| ファイル | 説明 |
|---------|------|
| `/backend/app/services/report_export_service.py` | ReportExportServiceクラス |
| `/backend/app/core/constants.py` | FileSizeLimit定義 |

---

## 🔗 関連仕様

- [Custom Reporting](./custom-reporting-export.md) - カスタムレポートビルダー
- [Lead Analytics](../features/lead-analytics.md) - リード分析

---

**実装ステータス**: ✅ CSV/Excel実装済み、⏸️ PDF部分実装
**拡張機能**: ⏳ グラフ、スケジュール、クラウド連携は未実装
