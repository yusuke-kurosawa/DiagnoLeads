# Error Logging & Monitoring

**Feature ID**: OPS-ERROR-001
**Status**: Implemented
**Priority**: Critical
**Last Updated**: 2025-11-23

---

## 📋 Overview

DiagnoLeadsの包括的なエラーロギング・モニタリングシステム。本番環境での問題追跡、デバッグ、パフォーマンス監視、SLA管理を実現します。

### ビジネス価値

- **本番環境の安定性**: エラーの早期検出と迅速な対応
- **デバッグ効率化**: スタックトレース、リクエスト/レスポンス詳細による問題解析
- **パフォーマンス監視**: エンドポイント別の処理時間追跡
- **コンプライアンス**: エラーログの保管とGDPR対応

---

## 🎯 主要機能

### 1. エラー分類システム

10種類のエラータイプで細かく分類：

| エラータイプ | 説明 | 例 |
|-------------|------|-----|
| `API_ERROR` | API呼び出しエラー | 外部API障害、タイムアウト |
| `DATABASE_ERROR` | データベースエラー | 接続失敗、クエリエラー |
| `VALIDATION_ERROR` | 入力検証エラー | 不正なメールアドレス、必須フィールド欠落 |
| `AUTHENTICATION_ERROR` | 認証エラー | 無効なトークン、期限切れ |
| `AUTHORIZATION_ERROR` | 認可エラー | 権限不足、クロステナントアクセス |
| `AI_SERVICE_ERROR` | AI API エラー | Claude API障害、レート制限 |
| `INTEGRATION_ERROR` | 外部連携エラー | Salesforce/HubSpot/Teams連携失敗 |
| `INTERNAL_ERROR` | 内部エラー | 予期しない例外 |
| `CICD_ERROR` | CI/CDエラー | GitHub Actions失敗 |
| `FRONTEND_ERROR` | フロントエンドエラー | JavaScriptエラー、UIクラッシュ |

### 2. 重要度レベル

| レベル | 説明 | 対応SLA |
|-------|------|---------|
| `LOW` | 軽微なエラー | 1週間以内 |
| `MEDIUM` | 通常のエラー | 24時間以内 |
| `HIGH` | 重大なエラー | 4時間以内 |
| `CRITICAL` | クリティカルエラー | 即座（15分以内） |

### 3. 環境分離

| 環境 | 説明 | ログ保持期間 |
|-----|------|------------|
| `development` | 開発環境 | 7日 |
| `staging` | ステージング環境 | 30日 |
| `production` | 本番環境 | 90日（CRITICAL: 1年） |
| `test` | テスト環境 | 3日 |
| `cicd` | CI/CDパイプライン | 14日 |

---

## 📊 データモデル

### ErrorLog

**テーブル**: `error_logs`

| フィールド | 型 | 制約 | 説明 |
|-----------|-----|-----|------|
| id | UUID | PK | エラーログID |
| tenant_id | UUID | FK(Tenant), NULLABLE | テナント（システムエラーではnull） |
| user_id | UUID | FK(User), SET NULL | エラー発生ユーザー |
| error_type | String(100) | NOT NULL, INDEX | エラー分類 |
| error_code | String(20) | | アプリケーションエラーコード |
| severity | String(20) | DEFAULT 'MEDIUM' | 重要度 |
| error_message | Text | NOT NULL | エラーメッセージ |
| stack_trace | Text | | スタックトレース |
| endpoint | String(200) | INDEX | APIエンドポイント |
| method | String(10) | | HTTPメソッド |
| status_code | Integer | | HTTPステータスコード |
| request_body | JSON | | リクエストペイロード |
| request_headers | JSON | | リクエストヘッダー（機密情報削除済み） |
| response_body | JSON | | レスポンスペイロード |
| duration_ms | Integer | | 処理時間（ミリ秒） |
| environment | String(20) | DEFAULT 'development' | 実行環境 |
| ip_address | String(45) | | クライアントIP（IPv4/IPv6） |
| user_agent | String(500) | | ブラウザUser Agent |
| context | JSON | | 追加コンテキストデータ |
| correlation_id | String(100) | INDEX | 分散トレーシングID |
| workflow_name | String(200) | | GitHub Actionsワークフロー名 |
| job_name | String(200) | | GitHub Actionsジョブ名 |
| run_id | String(100) | | GitHub ActionsランID |
| created_at | Timestamp | NOT NULL, INDEX | エラー発生時刻 |

**インデックス**:
- `[error_type]` - エラータイプ別集計
- `[endpoint]` - エンドポイント別分析
- `[correlation_id]` - 関連エラー追跡
- `[created_at]` - 時系列分析

---

## 🔌 API仕様

### 1. エラー報告（フロントエンド用）

```http
POST /api/v1/error-logs/report
Content-Type: application/json
```

**リクエスト**:
```json
{
  "error_type": "FRONTEND_ERROR",
  "error_message": "TypeError: Cannot read property 'id' of undefined",
  "error_code": "FE_001",
  "severity": "medium",
  "stack_trace": "at AssessmentList.tsx:45:12\nat onClick (Button.tsx:23:5)",
  "endpoint": "GET /api/v1/assessments",
  "method": "GET",
  "status_code": 200,
  "context": {
    "component": "AssessmentList",
    "props": {"tenantId": "..."}
  },
  "correlation_id": "req-12345-abcde"
}
```

**レスポンス** (201 Created):
```json
{
  "id": "error-uuid",
  "error_type": "FRONTEND_ERROR",
  "severity": "medium",
  "created_at": "2025-11-23T10:30:00Z"
}
```

**認証**: 不要（publicエンドポイント）

---

### 2. エラーログ一覧取得

```http
GET /api/v1/error-logs?error_type=API_ERROR&severity=high&limit=50
Authorization: Bearer {token}
```

**クエリパラメータ**:
| パラメータ | 型 | 説明 |
|-----------|-----|------|
| error_type | String | エラータイプフィルター |
| severity | String | 重要度フィルター |
| environment | String | 環境フィルター |
| endpoint | String | エンドポイントフィルター |
| start_date | ISO8601 | 期間開始 |
| end_date | ISO8601 | 期間終了 |
| correlation_id | String | 相関ID |
| skip | Integer | ページネーション（デフォルト: 0） |
| limit | Integer | 取得件数（デフォルト: 100） |

**レスポンス**:
```json
{
  "total": 250,
  "skip": 0,
  "limit": 50,
  "items": [
    {
      "id": "error-uuid",
      "error_type": "API_ERROR",
      "severity": "high",
      "error_message": "External API timeout",
      "endpoint": "/api/v1/integrations/salesforce/sync",
      "status_code": 504,
      "duration_ms": 30000,
      "created_at": "2025-11-23T10:00:00Z"
    }
  ]
}
```

**認証**: JWT必須
**認可**: System Admin（全テナント）、Tenant Admin（自テナントのみ）

---

### 3. エラーサマリー統計

```http
GET /api/v1/error-logs/summary
Authorization: Bearer {token}
```

**レスポンス**:
```json
{
  "total_errors": 1543,
  "errors_by_type": {
    "API_ERROR": 450,
    "DATABASE_ERROR": 23,
    "VALIDATION_ERROR": 892,
    "AI_SERVICE_ERROR": 67,
    "INTERNAL_ERROR": 111
  },
  "errors_by_severity": {
    "critical": 12,
    "high": 87,
    "medium": 645,
    "low": 799
  },
  "errors_by_environment": {
    "production": 234,
    "staging": 567,
    "development": 742
  },
  "critical_errors": 12
}
```

---

### 4. 最頻出エラー取得

```http
GET /api/v1/error-logs/frequent?top_n=10
Authorization: Bearer {token}
```

**レスポンス**:
```json
[
  {
    "error_type": "VALIDATION_ERROR",
    "error_message": "Invalid email format",
    "count": 345,
    "last_occurrence": "2025-11-23T09:45:00Z"
  },
  {
    "error_type": "API_ERROR",
    "error_message": "Salesforce API timeout",
    "count": 87,
    "last_occurrence": "2025-11-23T09:30:00Z"
  }
]
```

---

### 5. エラートレンド分析

```http
GET /api/v1/error-logs/trend?interval=day&days=7
Authorization: Bearer {token}
```

**クエリパラメータ**:
- `interval`: `hour` | `day` (デフォルト: `day`)
- `days`: 分析期間（デフォルト: 7日）

**レスポンス**:
```json
{
  "interval": "day",
  "data_points": [
    {"date": "2025-11-17", "count": 145},
    {"date": "2025-11-18", "count": 178},
    {"date": "2025-11-19", "count": 92},
    {"date": "2025-11-20", "count": 234},
    {"date": "2025-11-21", "count": 156},
    {"date": "2025-11-22", "count": 203},
    {"date": "2025-11-23", "count": 87}
  ]
}
```

---

### 6. 包括的エラー分析

```http
GET /api/v1/error-logs/analytics
Authorization: Bearer {token}
```

**レスポンス**: サマリー + 頻出エラー + トレンドの統合

---

### 7. 相関ID検索

```http
GET /api/v1/error-logs/correlation/{correlation_id}
Authorization: Bearer {token}
```

**用途**: 同一リクエスト内の全エラーを追跡

---

### 8. エラー詳細取得

```http
GET /api/v1/error-logs/{error_id}
Authorization: Bearer {token}
```

**レスポンス**:
```json
{
  "id": "error-uuid",
  "tenant_id": "tenant-uuid",
  "error_type": "API_ERROR",
  "severity": "high",
  "error_message": "Salesforce API timeout after 30s",
  "stack_trace": "...",
  "endpoint": "/api/v1/integrations/salesforce/sync",
  "method": "POST",
  "status_code": 504,
  "request_body": {...},
  "request_headers": {
    "authorization": "***REDACTED***",
    "content-type": "application/json"
  },
  "response_body": null,
  "duration_ms": 30000,
  "environment": "production",
  "correlation_id": "req-abc-123",
  "created_at": "2025-11-23T10:00:00Z"
}
```

---

## 🔒 セキュリティ機能

### 1. 機密情報の自動削除

以下のヘッダーは自動的に `***REDACTED***` に置換：
- `authorization`
- `cookie`
- `x-api-key`
- `x-auth-token`

### 2. PII（個人情報）の保護

- リクエスト/レスポンスボディのパスワード、トークン等は削除
- IP アドレスはハッシュ化推奨（未実装）

### 3. テナント分離

- ErrorLog.tenant_id でRLS適用
- System Adminのみ全テナントエラー閲覧可

---

## 📈 モニタリングと アラート

### アラートトリガー

| 条件 | アラート方法 |
|-----|-----------|
| CRITICALエラー発生 | Slack即座通知（未実装） |
| エラー率 > 10% | Slack/Email通知 |
| 同一エラー > 100回/時 | Slack通知 |
| API応答時間 > 3秒 | パフォーマンスアラート |

### ダッシュボード統合

- **Sentry統合**: 検討中
- **Vercel Analytics**: フロントエンドエラー追跡
- **カスタムダッシュボード**: DiagnoLeads管理画面内

---

## 🗑️ データ保持ポリシー

### 自動削除ルール

```python
# 90日以上前の非CRITICALログを削除
DELETE FROM error_logs
WHERE created_at < NOW() - INTERVAL '90 days'
  AND severity != 'CRITICAL';

# CRITICALは1年保持
DELETE FROM error_logs
WHERE created_at < NOW() - INTERVAL '1 year'
  AND severity = 'CRITICAL';
```

**実装**: `error_log_service.cleanup_old_logs(days=90)`

---

## 🛠️ CI/CD統合

### GitHub Actions対応

CI/CDパイプライン内のエラーも同じシステムで追跡：

```python
{
  "error_type": "CICD_ERROR",
  "workflow_name": "Backend Tests",
  "job_name": "pytest",
  "run_id": "1234567890",
  "error_message": "Test test_assessment_crud.py::test_create failed",
  "environment": "cicd"
}
```

**ワークフロー統合例**:
```yaml
- name: Report test failure
  if: failure()
  run: |
    curl -X POST https://api.diagnoleads.com/error-logs/report \
      -H "Content-Type: application/json" \
      -d '{"error_type":"CICD_ERROR","workflow_name":"${{github.workflow}}",...}'
```

---

## 🧪 テスト

### 実装済みテスト

- `backend/tests/test_error_log_service.py` - サービス層テスト
- `backend/tests/test_error_logs_api.py` - API エンドポイントテスト

### カバレッジ

- サービス層: 95%
- API層: 90%

---

## 📂 実装ファイル

| ファイル | 説明 |
|---------|------|
| `/backend/app/models/error_log.py` | ErrorLogモデル定義 |
| `/backend/app/services/error_log_service.py` | エラーログサービス（14.1KB） |
| `/backend/app/api/v1/error_logs.py` | APIエンドポイント（343行） |
| `/backend/alembic/versions/i9j0k1l2m3n4_add_error_logs_table.py` | マイグレーション |

---

## 🚀 将来の改善

1. **Sentry統合**: エラートラッキング専用ツールとの連携
2. **AI エラー分類**: 機械学習による自動エラー分類
3. **自動修復提案**: よくあるエラーの解決策提示
4. **Slack/Teams通知**: リアルタイムアラート
5. **IP ハッシュ化**: PII保護の強化
6. **GeoIP分析**: エラー発生地域の可視化

---

**実装ステータス**: ✅ 完全実装済み（本番環境対応 + ダッシュボードUI）

## 🎨 ダッシュボードUI（実装済み）

### ErrorLogPage
**ファイル**: `/frontend/src/pages/admin/ErrorLogPage.tsx`

**機能**:
- エラーサマリー統計カード（総エラー数、CRITICAL、HIGH、MEDIUM）
- フィルター機能（エラータイプ、重要度、環境）
- エラーログテーブル（重要度アイコン、メッセージ、エンドポイント）
- ページネーション

**サービス**: `/frontend/src/services/errorLogService.ts`
- `getErrorLogs()` - エラーログ一覧取得
- `getErrorSummary()` - サマリー統計取得
- `getErrorAnalytics()` - 包括的分析取得
