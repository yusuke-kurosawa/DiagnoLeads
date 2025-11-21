# CICD パイプライン・エラーログ管理 現状調査報告書

調査日時: 2025-11-19
対象: DiagnoLeads プロジェクト

---

## 1. 現在のCICD設定の概要

### 1.1 GitHub Actions ワークフロー構成

| ワークフロー | ファイル | 目的 | トリガー |
|---|---|---|---|
| **CI/CD Pipeline** | `.github/workflows/ci.yml` | 統合的なテスト・ビルド | main, develop へのpush/PR |
| **Backend CI** | `.github/workflows/backend-ci.yml` | バックエンドのテスト・リント | backend/ パス変更 |
| **Frontend CI** | `.github/workflows/frontend-ci.yml` | フロントエンドビルド・リント | frontend/ パス変更 |
| **Security Scan** | `.github/workflows/security-scan.yml` | Trivy脆弱性スキャン | push/PR/週1実行 |
| **Cancel Old Pipelines** | `.github/workflows/cancel-old-pipelines.yml` | 古いワークフロー削除 | 手動実行 |

### 1.2 ci.yml の詳細ステップ

```yaml
openapi-validation:
  └─ OpenAPI spec検証 + TypeScript型生成

backend-test:
  ├─ Python 3.11 セットアップ
  ├─ Ruff リント
  ├─ MyPy 型チェック
  ├─ アルメビックマイグレーション
  ├─ pytest テスト実行 (カバレッジ出力)
  └─ Codecov にカバレッジアップロード

frontend-test:
  ├─ Node 20 セットアップ
  ├─ ESLint リント
  ├─ TypeScript 型チェック
  ├─ npm run build
  └─ Vitest テスト (無効化中 - CI環境での hang問題)

docker-build:
  ├─ Backend Docker イメージビルドテスト
  └─ Frontend Docker イメージビルドテスト (無効化中)
```

### 1.3 エラーハンドリングの課題

**現在のパイプラインの問題点:**
- ❌ ワークフロー失敗時の詳細ログが保存されていない
- ❌ テスト失敗の根本原因分析がない
- ❌ パイプラインエラー間のパターン認識がない
- ❌ Vitest テスト無効化（CI環境のhang問題が未解決）
- ⚠️ Frontend Docker ビルド無効化（Dockerfile未作成）

---

## 2. エラーログ管理の現状

### 2.1 バックエンド側のログ管理

#### ロギング設定
**ファイル**: `backend/app/core/logging_config.py`
```python
def setup_logging(level: str = "INFO", json_format: bool = False):
    """
    - レベル: DEBUG, INFO, WARNING, ERROR, CRITICAL
    - 出力先: stdout のみ
    - JSON形式: 未実装
    """
```

**問題点:**
- ローカルファイル保存なし
- JSON形式ロギング未実装（本番環境では必須）
- リモート送信（Sentry等）なし
- ロギング集約がない

#### データベースベースの監視

**1. 監査ログ** (`backend/app/models/audit_log.py`)
```python
AuditLog(
    tenant_id,
    entity_type: TENANT, USER, TOPIC, INDUSTRY
    action: CREATE, UPDATE, DELETE
    entity_name, old_values, new_values
    ip_address, user_agent
    created_at
)
```
- 機能: マスターデータ変更の履歴記録
- スコープ: アカウント管理のみ
- エラーログ: **非対応**

**2. AI使用ログ** (`backend/app/models/ai_usage.py`)
```python
AIUsageLog(
    operation: generate_assessment, analyze_lead_insights, ...
    model, input_tokens, output_tokens, total_tokens
    cost_usd, duration_ms
    success: success, failure
)
```
- 機能: AI API呼び出しの追跡
- エラー情報: limited（success/failure のみ）
- スタックトレース: **非保存**

### 2.2 フロントエンド側のログ管理

**ファイル**: `frontend/src/hooks/useErrorLogger.ts`
```typescript
logError(error: unknown, context?: string)
  └─ console.error() に出力

logApiCall(method, url, data)
  └─ API呼び出しをロギング

logApiResponse(method, url, status, data)
  └─ レスポンスをロギング
```

**問題点:**
- ❌ ブラウザのコンソールログのみ（永続化なし）
- ❌ サーバー側への送信がない
- ❌ エラーサンプリングなし
- ❌ ユーザーセッション追跡なし

**ErrorBoundary** (`frontend/src/components/ErrorBoundary.tsx`)
```typescript
componentDidCatch(error, errorInfo)
  ├─ console.error() 出力
  └─ ユーザーにUIで通知
```
- 機能: React コンポーネントエラーの処理
- ロギング先: console のみ
- エラー報告: **マニュアル（サポートへ問い合わせ）**

### 2.3 API 層のエラーハンドリング

**例**: `backend/app/api/v1/ai.py`
```python
try:
    result = await ai_service.generate_assessment(...)
except Exception as e:
    raise HTTPException(
        status_code=500,
        detail=f"Assessment generation failed: {str(e)}"
    )
```

**問題点:**
- ❌ エラー内容が簡略化（スタックトレース非表示）
- ❌ エラーの詳細な分類がない
- ❌ 自動リトライがない（retry_helper は存在するが一部でしか使用）

### 2.4 AI サービスレベルのエラー処理

**ファイル**: `backend/app/services/ai/exceptions.py`
```python
class AIServiceError(Exception): pass  # Base
class AIAPIError(AIServiceError): pass
class AIRateLimitError(AIServiceError): pass
class AIValidationError(AIServiceError): pass
class AIJSONParseError(AIServiceError): pass
class AIPromptInjectionError(AIServiceError): pass
```

**リトライロジック** (`backend/app/services/ai/retry_helper.py`)
```python
async def retry_with_backoff(
    func, max_retries=3, initial_delay=1.0, backoff_factor=2.0
)
```
- 指数バックオフによるリトライ実装済み
- ログ出力: ✅ logger.warning/info
- しかし、全API呼び出しで使用されていない

---

## 3. 既存のログ解析機能

### 3.1 監査サービス (`backend/app/services/audit_service.py`)

```python
get_audit_logs(tenant_id, entity_type, action, date_range, ...)
  └─ フィルタリング・ページネーション対応

get_user_activity(tenant_id, user_id, days=30)
  └─ ユーザーアクティビティ履歴

get_entity_history(tenant_id, entity_type, entity_id)
  └─ エンティティの変更履歴

cleanup_old_logs(days=90)
  └─ 古いログの削除
```

**限界:**
- マスターデータ変更のみ（エラーログ非対応）
- API エラーを記録していない
- パフォーマンスメトリクスなし

### 3.2 レポートサービス (`backend/app/services/report_service.py`)

```python
execute_report(report_type):
  ├─ lead_analysis
  ├─ assessment_performance
  └─ custom_report

Report metrics:
  ├─ Lead: leads_total, average_score, conversion_rate, hot_leads
  └─ Assessment: assessments_total, published_count, ai_generated_count
```

**機能:**
- ✅ ビジネス指標の集約
- ✅ カスタム日付範囲フィルタリング
- ✅ グループ化・集計

**エラー分析:**
- ❌ 非対応

### 3.3 外部統合

**Google Analytics** (`backend/app/services/google_analytics_service.py`)
- ✅ ユーザー行動追跡
- ✅ コンバージョン測定
- ❌ エラー追跡なし

---

## 4. パイプライン関連のコード分析

### 4.1 バックエンド関連ファイル

| ファイル | エラーハンドリング | ロギング | スコープ |
|---|---|---|---|
| `core/logging_config.py` | ⚠️ 基本的 | ❌ stdout のみ | 全体 |
| `core/middleware.py` | ✅ JWT検証 | ❌ ログ出力不足 | 認証 |
| `models/audit_log.py` | N/A | ✅ DB記録 | マスターデータ |
| `models/ai_usage.py` | ⚠️ limited | ✅ DB記録 | AI API |
| `services/ai/exceptions.py` | ✅ カスタム | ⚠️ 定義のみ | AI |
| `services/ai/retry_helper.py` | ✅ リトライ | ✅ logger使用 | AI呼び出し |
| `api/v1/ai.py` | ⚠️ HTTPException | ❌ 詳細ログなし | エンドポイント |

### 4.2 フロントエンド関連ファイル

| ファイル | エラーハンドリング | ロギング | スコープ |
|---|---|---|---|
| `hooks/useErrorLogger.ts` | ✅ 構造化 | ❌ console のみ | ユーティリティ |
| `components/ErrorBoundary.tsx` | ✅ 実装 | ❌ console のみ | React |
| `services/api.ts` | ⚠️ basic | ❌ ログなし | HTTP |

### 4.3 必要な依存関係

**requirements.txt から:**
```
fastapi==0.104.1           # ✅ HTTP例外対応
sqlalchemy[asyncio]==2.0.23 # ✅ DB操作
structlog==23.2.0          # ⚠️ インストール済みだが未使用
anthropic>=0.34.0          # ✅ AI API
pytest==7.4.3              # ✅ テスト
```

**missing:**
- ❌ `sentry-sdk` - エラー監視
- ❌ `python-json-logger` - JSON ロギング
- ❌ `datadog` - ロギング集約
- ❌ `elasticsearch` - ログストレージ

---

## 5. 修正・追加すべきファイル リスト

### 5.1 **優先度: 高** - エラーログ基盤構築

#### A. エラーログ用DBモデル追加
**新規作成**: `backend/app/models/error_log.py`
```python
class ErrorLog(Base):
    id, tenant_id, user_id
    error_type (APIError, DatabaseError, ValidationError, etc.)
    error_message, error_code
    stack_trace, context (request/response)
    status_code, endpoint
    duration_ms
    environment (dev/staging/prod)
    created_at
```

#### B. エラーログサービス追加
**新規作成**: `backend/app/services/error_log_service.py`
```python
class ErrorLogService:
    - log_error(...)
    - get_error_logs(filters)
    - get_error_summary(date_range)
    - get_frequent_errors(top_n)
    - get_error_trend(date_range)
```

#### C. グローバルエラーハンドラ追加
**修正**: `backend/app/main.py`
```python
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    # ErrorLogService に記録
    # スタックトレース保存
    # 本番環境では詳細非表示
```

#### D. ロギング設定の強化
**修正**: `backend/app/core/logging_config.py`
```python
def setup_logging():
    - JSON形式対応
    - ファイルハンドラ追加（ローテーション）
    - リモート送信（Sentry対応）
    - コンテキスト情報埋め込み
```

### 5.2 **優先度: 高** - CICD エラー追跡

#### E. GitHub Actions エラーロギングステップ
**修正**: `.github/workflows/ci.yml`
```yaml
- name: Capture CI/CD Logs
  if: failure()
  run: |
    # エラーログをアーティファクトとして保存
    # GitHub API でエラーコメント追加
    
- name: Analyze Test Failures
  if: failure()
  run: pytest --tb=short > test-errors.log
```

### 5.3 **優先度: 中** - API ロギング強化

#### F. APIミドルウェア・ロギング
**新規作成**: `backend/app/core/logging_middleware.py`
```python
class LoggingMiddleware(BaseHTTPMiddleware):
    - リクエスト・レスポンス記録
    - 実行時間測定
    - エラーハンドリング統合
```

#### G. API エンドポイント修正
**修正**: `backend/app/api/v1/*.py`
```python
# すべての except Exception を改善
try:
    ...
except SpecificException as e:
    logger.error("...", exc_info=True)
    await error_log_service.log_error(...)
```

### 5.4 **優先度: 中** - フロントエンド ログ送信

#### H. エラー送信サービス追加
**新規作成**: `frontend/src/services/errorReportService.ts`
```typescript
export async function reportError(error, context) {
    // バックエンドのエラーログAPIに送信
    await api.post('/api/v1/errors', {
        error_type: error.name,
        message: error.message,
        stack: error.stack,
        context,
        timestamp
    })
}
```

#### I. ErrorBoundary修正
**修正**: `frontend/src/components/ErrorBoundary.tsx`
```typescript
componentDidCatch(error, errorInfo) {
    // reportError() 呼び出し
    // Sentry連携
}
```

#### J. useErrorLogger 強化
**修正**: `frontend/src/hooks/useErrorLogger.ts`
```typescript
const logError = async (error, context) => {
    // コンソール出力
    // バックエンド送信
    // セッション情報埋め込み
}
```

### 5.5 **優先度: 中** - ダッシュボード追加

#### K. エラーログビューエンドポイント
**新規作成**: `backend/app/api/v1/error_logs.py`
```python
@router.get("/tenants/{tenant_id}/error-logs")
@router.get("/tenants/{tenant_id}/error-analytics")
@router.get("/tenants/{tenant_id}/error-trends")
```

#### L. エラー分析フロントエンド
**新規作成**: `frontend/src/pages/admin/ErrorAnalyticsPage.tsx`
- エラー一覧表
- エラー種別別グラフ
- 時系列トレンド
- スタックトレース詳細表示

### 5.6 **優先度: 低** - 外部連携

#### M. Sentry 統合
**新規ファイル**: `backend/app/integrations/sentry.py`
```python
import sentry_sdk

sentry_sdk.init(dsn=settings.SENTRY_DSN)
```

#### N. requirements.txt 更新
```
sentry-sdk>=1.39.0
python-json-logger>=2.0.7
```

---

## 6. データベーススキーマ追加案

### error_logs テーブル定義

```sql
CREATE TABLE error_logs (
    id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    user_id UUID REFERENCES users(id),
    
    -- エラー情報
    error_type VARCHAR(100) NOT NULL,
    error_code VARCHAR(20),
    error_message TEXT NOT NULL,
    stack_trace TEXT,
    
    -- コンテキスト
    endpoint VARCHAR(200),
    method VARCHAR(10),
    status_code INTEGER,
    
    -- リクエスト情報
    request_body JSONB,
    request_headers JSONB,
    
    -- レスポンス情報
    response_body JSONB,
    
    -- パフォーマンス
    duration_ms INTEGER,
    
    -- メタデータ
    environment VARCHAR(20),
    ip_address VARCHAR(45),
    user_agent VARCHAR(500),
    
    -- 時刻
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- インデックス
    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE,
    INDEX idx_tenant_created (tenant_id, created_at),
    INDEX idx_error_type (error_type, created_at),
    INDEX idx_endpoint (endpoint, created_at)
);
```

---

## 7. 推奨される実装順序

### Phase 1 (即座 - 1週間)
1. ✅ error_log モデル + サービス作成
2. ✅ グローバルエラーハンドラ実装
3. ✅ ロギング設定の JSON 形式対応
4. ✅ CICD ワークフロー改善（ログキャプチャ）

### Phase 2 (短期 - 2週間)
5. ✅ フロントエンド エラー送信機能
6. ✅ APIミドルウェア・ロギング
7. ✅ エラーログAPIエンドポイント

### Phase 3 (中期 - 4週間)
8. ✅ エラー分析ダッシュボード
9. ✅ Sentry 連携
10. ✅ ドキュメント・テスト

---

## 8. 参照ファイル位置一覧

### バックエンド
- `/home/user/DiagnoLeads/backend/app/core/logging_config.py`
- `/home/user/DiagnoLeads/backend/app/models/audit_log.py`
- `/home/user/DiagnoLeads/backend/app/models/ai_usage.py`
- `/home/user/DiagnoLeads/backend/app/services/audit_service.py`
- `/home/user/DiagnoLeads/backend/app/services/ai/exceptions.py`
- `/home/user/DiagnoLeads/backend/app/services/ai/retry_helper.py`
- `/home/user/DiagnoLeads/backend/app/main.py`
- `/home/user/DiagnoLeads/backend/app/core/middleware.py`

### フロントエンド
- `/home/user/DiagnoLeads/frontend/src/hooks/useErrorLogger.ts`
- `/home/user/DiagnoLeads/frontend/src/components/ErrorBoundary.tsx`
- `/home/user/DiagnoLeads/frontend/src/services/api.ts`

### CICD
- `/home/user/DiagnoLeads/.github/workflows/ci.yml`
- `/home/user/DiagnoLeads/.github/workflows/backend-ci.yml`
- `/home/user/DiagnoLeads/.github/workflows/frontend-ci.yml`
- `/home/user/DiagnoLeads/.github/workflows/security-scan.yml`

### 設定
- `/home/user/DiagnoLeads/backend/requirements.txt`
- `/home/user/DiagnoLeads/docker-compose.yml`

---

## 9. まとめ

### 現状
- ✅ 基本的なロギングフレームワーク存在
- ✅ AI API 呼び出しの記録機構
- ✅ 監査ログ実装済み
- ❌ エラーログ統一的な管理なし
- ❌ CICD パイプラインエラー追跡なし
- ❌ リアルタイムエラー通知なし

### 改善効果
実装後のメリット:
1. **運用効率化**: エラーの迅速な特定・解決
2. **品質向上**: 潜在的なバグの早期発見
3. **ユーザー体験**: エラー時の自動復旧・ロールバック
4. **コンプライアンス**: エラーの監査証跡
5. **開発効率**: テスト・デバッグ情報の充実

---

**作成者**: Claude Code  
**調査完了日**: 2025-11-19
