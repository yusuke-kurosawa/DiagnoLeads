# Advanced Reporting & Business Intelligence

**Status**: Approved
**Priority**: High
**Phase**: 2 (Growth & Analytics)
**Estimated Effort**: 8-10 weeks
**Dependencies**: Analytics Dashboard, Data Warehouse, Export Service

## Overview

高度なレポーティング・BI機能により、テナントが診断データを深く分析し、データドリブンな意思決定を行えるようにします。カスタムレポートビルダー、スケジュールレポート配信、予測分析、クロス診断分析により、DiagnoLeadsを単なるリード獲得ツールから「ビジネスインテリジェンスプラットフォーム」へと進化させます。

## Business Value

- **データドリブン経営**: 意思決定の質向上 +80%
- **顧客満足度**: レポート機能による差別化で NPS +25ポイント
- **解約率低減**: データ活用による価値実感で -30%
- **アップセル機会**: Professionalプランへのアップグレード +40%
- **競争優位**: 主要競合にない高度分析機能

## Core Features

### 1. カスタムレポートビルダー
- ドラッグ&ドロップでレポート作成
- 30種類以上のチャート・ビジュアライゼーション
- リアルタイム更新
- 共有・埋め込み対応

### 2. スケジュールレポート配信
- 日次・週次・月次レポート自動生成
- メール・Slack配信
- PDF/Excel エクスポート
- カスタムフォーマット

### 3. データエクスポート
- CSV、Excel、JSON形式
- 一括エクスポート・API経由エクスポート
- フィルター・ソート対応
- 大容量データ対応（ストリーミング）

### 4. クロス診断分析
- 複数診断の横断分析
- コホート分析
- ファネル分析
- リテンション分析

### 5. 予測分析（AI活用）
- リード獲得予測
- トレンド分析・季節性検出
- 異常検知（CV率急落など）
- レコメンデーション

### 6. データダッシュボード
- カスタムダッシュボード作成
- ウィジェット配置・リサイズ
- フィルター・ドリルダウン
- リアルタイム更新

## User Stories

### 1. カスタムレポート作成

**As a** マーケティングマネージャー
**I want to** 自由にカスタムレポートを作成
**So that** 必要な指標を好きな形式で可視化できる

**Acceptance Criteria**:

**Given**: レポートビルダーにアクセス
**When**: 新規レポート作成
**Then**:
- レポート名・説明入力
- データソース選択:
  - リード
  - 診断回答
  - エンゲージメント
  - コンバージョン
- ディメンション選択（X軸）:
  - 日付（日別、週別、月別、四半期別）
  - 業界
  - 企業規模
  - 診断タイプ
  - 地域
- メトリクス選択（Y軸）:
  - リード数
  - コンバージョン率
  - 平均スコア
  - 完了率
  - 離脱率
- チャートタイプ選択:
  - 折れ線グラフ
  - 棒グラフ
  - 円グラフ
  - ヒートマップ
  - ファネルチャート
  - テーブル
- フィルター設定:
  - 日付範囲
  - セグメント
  - カスタム条件
- リアルタイムプレビュー
- 保存

**Given**: レポートが作成されている
**When**: レポートを表示
**Then**:
- チャートが描画される
- データが最新（または指定日時）
- インタラクティブ操作可能:
  - ズーム
  - ツールチップ
  - ドリルダウン
  - データポイントクリックで詳細表示
- エクスポートボタン（PDF、PNG、CSV）
- 共有ボタン（URL生成）

### 2. スケジュールレポート配信

**As a** セールスディレクター
**I want to** 毎週月曜朝にレポートをメール受信
**So that** 週次ミーティングで最新データを確認できる

**Acceptance Criteria**:

**Given**: カスタムレポートが作成されている
**When**: 「スケジュール配信設定」をクリック
**Then**:
- 配信頻度選択:
  - 日次（毎日、平日のみ）
  - 週次（曜日選択）
  - 月次（日付または第N営業日）
  - カスタム（Cronジョブ）
- 配信時刻選択（例: 09:00 JST）
- 受信者設定:
  - メールアドレス入力（複数可）
  - チーム選択
  - Slackチャンネル選択
- フォーマット選択:
  - PDF（推奨）
  - Excel
  - CSV
  - 埋め込みHTML
- 件名・メッセージカスタマイズ
- プレビュー送信
- 有効化

**Given**: スケジュールレポートが設定されている
**When**: 配信時刻になる
**Then**:
- レポートが自動生成される
- 最新データで描画
- PDF/Excelファイル生成
- メール送信:
  - 件名: 「【DiagnoLeads】週次レポート - 2025年11月18日」
  - 本文: カスタムメッセージ
  - 添付ファイル: レポートPDF
- Slack配信（設定されている場合）:
  - レポートサマリー投稿
  - PDFリンク
- 配信履歴に記録

**Given**: 配信が失敗した
**When**: エラーが発生
**Then**:
- 3回リトライ（1時間間隔）
- 管理者に通知
- エラーログ記録

### 3. データエクスポート

**As a** データアナリスト
**I want to** 全リードデータをExcelでエクスポート
**So that** 外部ツールで詳細分析できる

**Acceptance Criteria**:

**Given**: リード一覧ページにアクセス
**When**: 「エクスポート」ボタンをクリック
**Then**:
- エクスポート設定モーダル表示
- フォーマット選択:
  - CSV
  - Excel (.xlsx)
  - JSON
- カラム選択:
  - すべてのカラム
  - 表示中のカラムのみ
  - カスタム選択
- フィルター適用:
  - 現在のフィルターを適用
  - または全データ
- データ範囲:
  - 全データ
  - 最新N件
  - 日付範囲指定
- エクスポート実行

**Given**: データ量が大きい（10,000件以上）
**When**: エクスポート実行
**Then**:
- バックグラウンドジョブで処理
- 進捗通知表示
- 完了時にメール通知
- ダウンロードリンク（24時間有効）

**Given**: エクスポート履歴ページにアクセス
**When**: 過去のエクスポート確認
**Then**:
- エクスポート履歴一覧表示:
  - ファイル名
  - フォーマット
  - レコード数
  - エクスポート日時
  - ステータス（処理中、完了、失敗）
  - ダウンロードボタン（24時間以内）

### 4. クロス診断分析

**As a** プロダクトマネージャー
**I want to** 複数の診断を横断的に分析
**So that** 診断間の関係性や傾向を把握できる

**Acceptance Criteria**:

**Given**: クロス診断分析ページにアクセス
**When**: 比較する診断を選択（最大5つ）
**Then**:
- 診断選択UI表示
- 選択した診断の統計サマリー:
  - 診断ごとのリード数
  - 平均完了率
  - 平均スコア
- 比較チャート:
  - **完了率比較**（棒グラフ）
  - **時系列トレンド**（折れ線グラフ）
  - **業界分布比較**（積み上げ棒グラフ）
  - **スコア分布比較**（箱ひげ図）
- 重複リード分析:
  - 複数診断を完了したリード数
  - ベン図で可視化
  - クロスセル機会の特定

**Given**: ファネル分析を選択
**When**: 複数診断のファネルを比較
**Then**:
- 各診断のファネルチャート並列表示:
  - 開始
  - 50%完了
  - 100%完了
  - リード情報入力
  - 送信完了
- 診断ごとの離脱率比較
- ボトルネック特定
- 改善提案（AIレコメンデーション）

### 5. 予測分析

**As a** マーケティングマネージャー
**I want to** 来月のリード獲得数を予測
**So that** 予算配分とKPI設定を最適化できる

**Acceptance Criteria**:

**Given**: 過去3ヶ月以上のデータがある
**When**: 予測分析ページにアクセス
**Then**:
- **リード獲得予測**表示:
  - 今後4週間の予測値（信頼区間付き）
  - 折れ線グラフで可視化
  - 「このペースだと月間目標に対して-15%」などのインサイト
- **トレンド分析**:
  - 増加傾向・減少傾向の検出
  - 季節性パターン（曜日別、月別）
  - 外れ値検出
- **異常検知**:
  - CV率の急落を検出
  - 「過去平均より30%低い」などのアラート
  - 原因仮説提示（AIが自動生成）

**Given**: 予測が表示されている
**When**: シナリオシミュレーション
**Then**:
- パラメータ調整UI:
  - 広告予算増額: +20%
  - 新しい診断追加
  - キャンペーン実施
- 予測値の再計算
- Before/After比較表示
- ROI試算

### 6. カスタムダッシュボード

**As a** エグゼクティブ
**I want to** 重要KPIを一画面で確認
**So that** 毎朝5分でビジネス状況を把握できる

**Acceptance Criteria**:

**Given**: ダッシュボードビルダーにアクセス
**When**: 新規ダッシュボード作成
**Then**:
- ダッシュボード名入力
- グリッドレイアウトエディター表示
- ウィジェット追加:
  - KPI カード（数値表示）
  - チャート（レポートから選択）
  - テーブル
  - テキスト（メモ）
- ウィジェット配置:
  - ドラッグ&ドロップ
  - リサイズ
  - レイアウト自動調整
- 各ウィジェットの設定:
  - データソース
  - フィルター
  - 更新頻度（リアルタイム、10分、1時間）
- プレビュー・保存

**Given**: ダッシュボードが作成されている
**When**: ダッシュボードを開く
**Then**:
- すべてのウィジェットが読み込まれる
- データが最新
- インタラクティブ操作:
  - フィルター変更→全ウィジェット連動
  - 日付範囲選択
  - ドリルダウン
- 「更新」ボタンで手動リフレッシュ
- 全画面表示モード
- 共有リンク生成（公開/非公開）

## Technical Architecture

### Report Builder Service

```python
# backend/app/services/reporting/report_builder.py
from typing import List, Dict
from app.models import CustomReport, ReportSchedule
from app.services.analytics.data_aggregator import DataAggregator

class ReportBuilderService:
    """カスタムレポート構築"""

    async def create_report(
        self,
        tenant_id: str,
        name: str,
        data_source: str,
        dimensions: List[str],
        metrics: List[str],
        chart_type: str,
        filters: Dict = None
    ) -> CustomReport:
        """レポート作成"""

        report = await CustomReport.create(
            tenant_id=tenant_id,
            name=name,
            data_source=data_source,
            dimensions=dimensions,
            metrics=metrics,
            chart_type=chart_type,
            filters=filters or {}
        )

        return report

    async def generate_report_data(
        self,
        report: CustomReport,
        date_range: Dict = None
    ) -> Dict:
        """レポートデータ生成"""

        aggregator = DataAggregator()

        # データ集計
        data = await aggregator.aggregate(
            tenant_id=report.tenant_id,
            data_source=report.data_source,
            dimensions=report.dimensions,
            metrics=report.metrics,
            filters=report.filters,
            date_range=date_range
        )

        # チャート用にフォーマット
        formatted_data = self._format_for_chart(
            data,
            report.chart_type
        )

        return {
            "report_id": str(report.id),
            "name": report.name,
            "chart_type": report.chart_type,
            "data": formatted_data,
            "generated_at": datetime.utcnow().isoformat()
        }

    def _format_for_chart(self, data: List[Dict], chart_type: str) -> Dict:
        """チャート形式にフォーマット"""

        formatters = {
            "line": self._format_line_chart,
            "bar": self._format_bar_chart,
            "pie": self._format_pie_chart,
            "table": self._format_table
        }

        formatter = formatters.get(chart_type, self._format_table)
        return formatter(data)

    def _format_line_chart(self, data: List[Dict]) -> Dict:
        """折れ線グラフ用フォーマット"""
        return {
            "labels": [row["dimension"] for row in data],
            "datasets": [{
                "label": "Value",
                "data": [row["value"] for row in data]
            }]
        }
```

### Scheduled Report Service

```python
# backend/app/services/reporting/scheduled_report_service.py
from app.services.reporting.report_export import ReportExportService
from app.services.email.email_service import EmailService

class ScheduledReportService:
    """スケジュールレポート配信"""

    async def create_schedule(
        self,
        report_id: str,
        frequency: str,  # daily, weekly, monthly
        schedule_time: str,  # "09:00"
        recipients: List[str],
        format: str = "pdf"
    ) -> ReportSchedule:
        """スケジュール作成"""

        schedule = await ReportSchedule.create(
            report_id=report_id,
            frequency=frequency,
            schedule_time=schedule_time,
            recipients=recipients,
            format=format,
            is_active=True
        )

        # Cronジョブ登録
        await self._register_cron_job(schedule)

        return schedule

    async def execute_scheduled_report(self, schedule_id: str):
        """スケジュールレポート実行"""

        schedule = await ReportSchedule.get(schedule_id)
        report = await CustomReport.get(schedule.report_id)

        # レポート生成
        report_builder = ReportBuilderService()
        report_data = await report_builder.generate_report_data(report)

        # エクスポート
        exporter = ReportExportService()

        if schedule.format == "pdf":
            file_path = await exporter.export_to_pdf(report, report_data)
        elif schedule.format == "excel":
            file_path = await exporter.export_to_excel(report, report_data)
        else:
            file_path = await exporter.export_to_csv(report, report_data)

        # メール送信
        email_service = EmailService()
        await email_service.send_scheduled_report(
            recipients=schedule.recipients,
            report_name=report.name,
            file_path=file_path,
            schedule=schedule
        )

        # 配信履歴記録
        await ReportDeliveryHistory.create(
            schedule_id=schedule.id,
            delivered_at=datetime.utcnow(),
            status="success",
            recipients=schedule.recipients
        )
```

### Data Export Service

```python
# backend/app/services/reporting/data_export_service.py
import csv
import pandas as pd
from io import StringIO, BytesIO

class DataExportService:
    """データエクスポート"""

    async def export_leads(
        self,
        tenant_id: str,
        format: str,
        filters: Dict = None,
        columns: List[str] = None
    ) -> str:
        """リードデータエクスポート"""

        # データ取得
        query = Lead.query.filter(Lead.tenant_id == tenant_id)

        if filters:
            query = self._apply_filters(query, filters)

        leads = await query.all()

        # フォーマット別エクスポート
        if format == "csv":
            return await self._export_to_csv(leads, columns)
        elif format == "excel":
            return await self._export_to_excel(leads, columns)
        elif format == "json":
            return await self._export_to_json(leads, columns)

    async def _export_to_csv(
        self,
        leads: List[Lead],
        columns: List[str] = None
    ) -> str:
        """CSV エクスポート"""

        output = StringIO()
        writer = csv.writer(output)

        # ヘッダー
        if not columns:
            columns = ["id", "company_name", "contact_name", "email", "score", "created_at"]

        writer.writerow(columns)

        # データ行
        for lead in leads:
            row = [getattr(lead, col) for col in columns]
            writer.writerow(row)

        # ファイル保存
        content = output.getvalue()
        file_path = f"/exports/{datetime.now().strftime('%Y%m%d_%H%M%S')}_leads.csv"

        await self._upload_to_storage(file_path, content)

        return file_path

    async def _export_to_excel(
        self,
        leads: List[Lead],
        columns: List[str] = None
    ) -> str:
        """Excel エクスポート"""

        # DataFrameに変換
        data = [lead.to_dict() for lead in leads]
        df = pd.DataFrame(data)

        if columns:
            df = df[columns]

        # Excelに書き出し
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Leads', index=False)

        # ファイル保存
        content = output.getvalue()
        file_path = f"/exports/{datetime.now().strftime('%Y%m%d_%H%M%S')}_leads.xlsx"

        await self._upload_to_storage(file_path, content)

        return file_path

    async def _export_large_dataset(
        self,
        tenant_id: str,
        format: str,
        filters: Dict = None
    ):
        """大容量データエクスポート（バックグラウンドジョブ）"""

        # エクスポートジョブ作成
        export_job = await ExportJob.create(
            tenant_id=tenant_id,
            format=format,
            filters=filters,
            status="processing"
        )

        # バックグラウンド処理
        from app.tasks import process_large_export
        process_large_export.delay(export_job.id)

        return export_job
```

### Predictive Analytics Service

```python
# backend/app/services/reporting/predictive_analytics.py
import numpy as np
from sklearn.linear_regression import LinearRegression
from statsmodels.tsa.holtwinters import ExponentialSmoothing

class PredictiveAnalyticsService:
    """予測分析"""

    async def forecast_leads(
        self,
        tenant_id: str,
        periods: int = 4  # 週数
    ) -> Dict:
        """リード獲得予測"""

        # 過去データ取得（過去12週間）
        historical_data = await self._get_historical_lead_data(tenant_id, weeks=12)

        # 時系列予測（Exponential Smoothing）
        model = ExponentialSmoothing(
            historical_data["values"],
            seasonal_periods=7,  # 週次季節性
            trend="add",
            seasonal="add"
        )

        fitted_model = model.fit()
        forecast = fitted_model.forecast(periods)

        # 信頼区間計算
        confidence_intervals = self._calculate_confidence_intervals(
            historical_data,
            forecast
        )

        return {
            "historical": historical_data,
            "forecast": {
                "values": forecast.tolist(),
                "periods": periods,
                "confidence_lower": confidence_intervals["lower"],
                "confidence_upper": confidence_intervals["upper"]
            },
            "insights": self._generate_insights(historical_data, forecast)
        }

    async def detect_anomalies(
        self,
        tenant_id: str,
        metric: str = "conversion_rate"
    ) -> List[Dict]:
        """異常検知"""

        # 過去データ取得
        data = await self._get_time_series_data(tenant_id, metric)

        # 移動平均と標準偏差計算
        window = 7  # 7日間
        rolling_mean = pd.Series(data["values"]).rolling(window=window).mean()
        rolling_std = pd.Series(data["values"]).rolling(window=window).std()

        # 異常検知（3σルール）
        anomalies = []
        for i, value in enumerate(data["values"]):
            if i < window:
                continue

            z_score = (value - rolling_mean[i]) / rolling_std[i]

            if abs(z_score) > 3:  # 3σ以上
                anomalies.append({
                    "date": data["dates"][i],
                    "value": value,
                    "expected": rolling_mean[i],
                    "z_score": z_score,
                    "severity": "high" if abs(z_score) > 4 else "medium"
                })

        return anomalies

    def _generate_insights(
        self,
        historical: Dict,
        forecast: np.ndarray
    ) -> List[str]:
        """インサイト生成"""

        insights = []

        # トレンド分析
        trend = np.polyfit(range(len(historical["values"])), historical["values"], 1)[0]

        if trend > 0:
            insights.append(f"増加傾向（週あたり+{trend:.1f}リード）")
        elif trend < 0:
            insights.append(f"減少傾向（週あたり{trend:.1f}リード）")
        else:
            insights.append("横ばい傾向")

        # 予測値と目標比較
        avg_forecast = np.mean(forecast)
        # 仮に目標が100リード/週
        target = 100

        if avg_forecast < target * 0.85:
            insights.append(f"⚠️ 目標に対して{(1 - avg_forecast/target)*100:.0f}%不足")
        elif avg_forecast > target * 1.15:
            insights.append(f"✅ 目標を{(avg_forecast/target - 1)*100:.0f}%上回る見込み")

        return insights
```

## API Endpoints

### カスタムレポート

```
POST   /api/v1/reports/custom
       - カスタムレポート作成

GET    /api/v1/reports/custom
       - レポート一覧

GET    /api/v1/reports/custom/{id}
       - レポート詳細

GET    /api/v1/reports/custom/{id}/data
       - レポートデータ生成
       - Query: ?date_range=last_30_days

DELETE /api/v1/reports/custom/{id}
       - レポート削除
```

### スケジュールレポート

```
POST   /api/v1/reports/schedules
       - スケジュール設定

GET    /api/v1/reports/schedules
       - スケジュール一覧

PUT    /api/v1/reports/schedules/{id}
       - スケジュール更新

DELETE /api/v1/reports/schedules/{id}
       - スケジュール削除

POST   /api/v1/reports/schedules/{id}/test
       - テスト送信
```

### データエクスポート

```
POST   /api/v1/exports/leads
       - リードエクスポート
       - Request: { format, filters, columns }

GET    /api/v1/exports/jobs
       - エクスポートジョブ一覧

GET    /api/v1/exports/jobs/{id}
       - ジョブステータス取得

GET    /api/v1/exports/jobs/{id}/download
       - ファイルダウンロード
```

### 予測分析

```
GET    /api/v1/analytics/forecast
       - リード獲得予測
       - Query: ?metric=leads&periods=4

GET    /api/v1/analytics/anomalies
       - 異常検知
       - Query: ?metric=conversion_rate

GET    /api/v1/analytics/trends
       - トレンド分析
```

## Database Schema

```sql
-- カスタムレポート
CREATE TABLE custom_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,

    name VARCHAR(255) NOT NULL,
    description TEXT,

    -- レポート設定
    data_source VARCHAR(100) NOT NULL,  -- leads, responses, engagement
    dimensions TEXT[] NOT NULL,  -- ["date", "industry"]
    metrics TEXT[] NOT NULL,  -- ["count", "conversion_rate"]
    chart_type VARCHAR(50) NOT NULL,  -- line, bar, pie, table

    -- フィルター
    filters JSONB,

    -- 共有設定
    is_public BOOLEAN DEFAULT FALSE,
    share_token VARCHAR(255) UNIQUE,

    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    INDEX idx_custom_reports_tenant (tenant_id)
);

-- レポートスケジュール
CREATE TABLE report_schedules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    report_id UUID NOT NULL REFERENCES custom_reports(id) ON DELETE CASCADE,

    frequency VARCHAR(50) NOT NULL,  -- daily, weekly, monthly
    schedule_time VARCHAR(10) NOT NULL,  -- "09:00"
    timezone VARCHAR(50) DEFAULT 'Asia/Tokyo',

    -- 配信設定
    recipients TEXT[] NOT NULL,
    slack_channels TEXT[],
    format VARCHAR(20) DEFAULT 'pdf',  -- pdf, excel, csv

    -- カスタムメッセージ
    subject VARCHAR(255),
    message TEXT,

    is_active BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    INDEX idx_schedules_report (report_id)
);

-- 配信履歴
CREATE TABLE report_delivery_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    schedule_id UUID NOT NULL REFERENCES report_schedules(id) ON DELETE CASCADE,

    delivered_at TIMESTAMP DEFAULT NOW(),
    status VARCHAR(50) DEFAULT 'success',  -- success, failed
    recipients TEXT[],
    error_message TEXT,

    INDEX idx_delivery_schedule (schedule_id, delivered_at DESC)
);

-- エクスポートジョブ
CREATE TABLE export_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,

    format VARCHAR(20) NOT NULL,  -- csv, excel, json
    data_type VARCHAR(50) NOT NULL,  -- leads, responses, analytics
    filters JSONB,
    columns TEXT[],

    status VARCHAR(50) DEFAULT 'processing',  -- processing, completed, failed
    file_path TEXT,
    file_size INTEGER,
    record_count INTEGER,

    error_message TEXT,

    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    expires_at TIMESTAMP,  -- 24時間後

    INDEX idx_exports_tenant (tenant_id, created_at DESC)
);

-- カスタムダッシュボード
CREATE TABLE custom_dashboards (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,

    name VARCHAR(255) NOT NULL,
    description TEXT,

    -- レイアウト設定
    layout JSONB NOT NULL,  -- グリッドレイアウト定義
    widgets JSONB NOT NULL,  -- ウィジェット配置

    is_default BOOLEAN DEFAULT FALSE,

    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    INDEX idx_dashboards_tenant (tenant_id)
);
```

## Frontend Components

### Report Builder

```typescript
// frontend/src/features/reporting/ReportBuilder.tsx
import { useState } from 'react'
import { Select } from '@/components/ui/select'
import { Card } from '@/components/ui/card'
import { ChartPreview } from './ChartPreview'

export function ReportBuilder() {
  const [config, setConfig] = useState({
    dataSource: 'leads',
    dimensions: [],
    metrics: [],
    chartType: 'line'
  })

  return (
    <div className="grid md:grid-cols-2 gap-6">
      <div>
        <h2 className="text-2xl font-bold mb-6">レポート設定</h2>

        <Card className="p-6 space-y-6">
          <div>
            <Label>データソース</Label>
            <Select
              value={config.dataSource}
              onChange={(v) => setConfig({ ...config, dataSource: v })}
            >
              <SelectItem value="leads">リード</SelectItem>
              <SelectItem value="responses">診断回答</SelectItem>
              <SelectItem value="engagement">エンゲージメント</SelectItem>
            </Select>
          </div>

          <div>
            <Label>ディメンション（X軸）</Label>
            <MultiSelect
              options={dimensionOptions}
              value={config.dimensions}
              onChange={(v) => setConfig({ ...config, dimensions: v })}
            />
          </div>

          <div>
            <Label>メトリクス（Y軸）</Label>
            <MultiSelect
              options={metricOptions}
              value={config.metrics}
              onChange={(v) => setConfig({ ...config, metrics: v })}
            />
          </div>

          <div>
            <Label>チャートタイプ</Label>
            <ChartTypeSelector
              value={config.chartType}
              onChange={(v) => setConfig({ ...config, chartType: v })}
            />
          </div>
        </Card>
      </div>

      <div>
        <h2 className="text-2xl font-bold mb-6">プレビュー</h2>
        <ChartPreview config={config} />
      </div>
    </div>
  )
}
```

## Security Considerations

- **データアクセス制御**: テナント分離、ロールベースアクセス
- **エクスポート制限**: ファイルサイズ上限、レート制限
- **共有リンク**: トークン認証、有効期限設定
- **機密データマスキング**: エクスポート時に個人情報マスク（オプション）

## Testing Strategy

### 単体テスト
- データ集計ロジック
- チャートフォーマット変換
- 予測モデル

### 統合テスト
- レポート生成 → エクスポート
- スケジュール実行 → メール送信
- 大容量データエクスポート

### E2Eテスト
- レポート作成 → スケジュール設定 → 配信確認
- カスタムダッシュボード作成 → ウィジェット配置

## Performance Requirements

- **レポート生成**: <3秒（10,000レコードまで）
- **エクスポート**: <10秒（100,000レコードまで）
- **予測計算**: <5秒
- **ダッシュボード読み込み**: <2秒

## Rollout Plan

### Week 1-3: カスタムレポートビルダー
### Week 4-6: スケジュールレポート・エクスポート
### Week 7-8: 予測分析
### Week 9-10: カスタムダッシュボード・最終調整

## Success Metrics

- **レポート作成数**: テナントあたり平均5個以上
- **スケジュールレポート利用率**: Professional以上のテナントの60%
- **エクスポート利用率**: 月1回以上 70%
- **ダッシュボード利用率**: 毎日アクセス 50%

## Related Specifications

- [Analytics Dashboard](./analytics-dashboard.md) - 基本分析機能
- [Lead Nurturing](./lead-nurturing-automation.md) - キャンペーン分析
- [Subscription & Billing](./subscription-billing.md) - プラン別機能制限

## References

- [Business Intelligence Best Practices](https://www.tableau.com/learn/articles/business-intelligence)
- [Data Visualization Principles](https://www.interaction-design.org/literature/article/data-visualization-principles)
- [Predictive Analytics Guide](https://www.ibm.com/topics/predictive-analytics)
