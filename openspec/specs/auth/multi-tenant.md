# Multi-Tenant Architecture Specification

## Feature: Multi-Tenant Data Isolation

### Requirement: Tenant-scoped data access

すべてのデータアクセスはテナントスコープで制限される。

#### Scenario: User accesses data within their tenant

**GIVEN** ユーザー "user@tenant-a.com" がテナントAに属している
**AND** 診断データがテナントAに10件存在する
**WHEN** ユーザーが診断一覧をリクエストする
**THEN** システムはテナントAの診断10件のみを返す
**AND** 他のテナントのデータは含まれない

**Technical Requirements:**
- すべてのクエリに `WHERE tenant_id = current_tenant_id` が自動的に適用される SHALL
- JWTトークンに `tenant_id` クレームが含まれる SHALL
- ミドルウェアがリクエストごとにテナントIDを検証する SHALL

#### Scenario: User attempts to access data from another tenant

**GIVEN** ユーザーがテナントAに属している
**WHEN** ユーザーがテナントBのデータIDを指定してアクセスを試みる
**THEN** システムは404エラーを返す
**AND** データは返されない
**AND** 不正アクセス試行をログに記録する

### Requirement: Tenant creation and initialization

新規テナントの作成時に必要なリソースが初期化される。

#### Scenario: Create new tenant during user registration

**GIVEN** 新規ユーザーが登録フォームを送信した
**WHEN** システムが新しいテナントを作成する
**THEN** 以下を実行する:
  - テナントレコードを作成（UUID、名前、作成日時）
  - デフォルト設定を作成（JSONB）
  - 初回ユーザーをテナント管理者として作成
  - サンプル診断を作成（オプション）

**Technical Requirements:**
- テナント作成はトランザクション内で完了する SHALL
- 作成失敗時はロールバックする SHALL
- テナントIDはUUIDv4形式 SHALL

#### Scenario: Tenant settings initialization

**GIVEN** 新しいテナントが作成された
**THEN** 以下のデフォルト設定が作成される:
```json
{
  "branding": {
    "primary_color": "#6366f1",
    "logo_url": null
  },
  "features": {
    "ai_generation_enabled": true,
    "external_integrations_enabled": false
  },
  "limits": {
    "max_assessments": 10,
    "max_leads_per_month": 1000,
    "max_users": 5
  },
  "notifications": {
    "email_on_new_lead": true,
    "slack_webhook_url": null
  }
}
```

### Requirement: Tenant switching (for system admins)

システム管理者は異なるテナント間を切り替えられる。

#### Scenario: System admin switches tenant context

**GIVEN** ユーザーがシステム管理者権限を持っている
**WHEN** 管理者がテナント切り替えUIを使用する
**AND** テナントBを選択する
**THEN** 新しいJWTトークンが発行される
**AND** トークンの `tenant_id` クレームがテナントBに更新される
**AND** すべてのデータアクセスがテナントBスコープになる

**Technical Requirements:**
- テナント切り替えはシステム管理者のみ可能 SHALL
- 切り替え操作は監査ログに記録される SHALL

### Requirement: Row-Level Security (RLS) enforcement

PostgreSQLのRow-Level Securityでテナント分離を強制する。

#### Scenario: Database enforces tenant isolation

**GIVEN** PostgreSQLのRLSポリシーが有効化されている
**WHEN** アプリケーションがクエリを実行する
**THEN** データベースが自動的にテナントフィルタを適用する
**AND** SQLインジェクションでも他テナントのデータにアクセスできない

**Technical Implementation:**
```sql
-- Enable RLS on all tenant-scoped tables
ALTER TABLE assessments ENABLE ROW LEVEL SECURITY;
ALTER TABLE leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE questions ENABLE ROW LEVEL SECURITY;

-- Create policy for tenant isolation
CREATE POLICY tenant_isolation_policy ON assessments
  FOR ALL
  USING (tenant_id = current_setting('app.current_tenant_id')::uuid);

-- Set tenant context before each query
SET app.current_tenant_id = '<tenant-uuid>';
```

### Requirement: Tenant billing and plan limits

テナントごとにプランと利用制限が管理される。

#### Scenario: Check tenant plan limits

**GIVEN** テナントが無料プランを使用している
**AND** 無料プランの診断作成上限は10件である
**AND** テナントが既に10件の診断を作成している
**WHEN** ユーザーが新しい診断を作成しようとする
**THEN** エラーメッセージ "プランの上限に達しました。アップグレードしてください" を表示する
**AND** 診断作成を拒否する

**Technical Requirements:**
- プラン制限チェックは各操作前に実行される SHALL
- 制限値は `tenants.settings.limits` から取得する SHALL

#### Scenario: Upgrade tenant plan

**GIVEN** テナントが無料プランを使用している
**WHEN** テナント管理者がプロプランにアップグレードする
**THEN** `tenants.plan` を "pro" に更新する
**AND** 制限値を以下に更新する:
  - `max_assessments`: 50
  - `max_leads_per_month`: 10000
  - `max_users`: 20

---

## Database Schema

### tenants table
```sql
CREATE TABLE tenants (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  slug VARCHAR(100) UNIQUE NOT NULL,
  plan VARCHAR(50) DEFAULT 'free',
  settings JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_tenants_slug ON tenants(slug);
```

### users table
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  name VARCHAR(255) NOT NULL,
  role VARCHAR(50) DEFAULT 'user',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_users_tenant ON users(tenant_id);
CREATE INDEX idx_users_email ON users(email);
```

### assessments table (example tenant-scoped table)
```sql
CREATE TABLE assessments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  title VARCHAR(255) NOT NULL,
  description TEXT,
  questions JSONB NOT NULL,
  scoring_logic JSONB NOT NULL,
  status VARCHAR(50) DEFAULT 'draft',
  created_by UUID REFERENCES users(id),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_assessments_tenant ON assessments(tenant_id, created_at DESC);

-- Enable RLS
ALTER TABLE assessments ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation ON assessments
  FOR ALL
  USING (tenant_id = current_setting('app.current_tenant_id')::uuid);
```

---

## Middleware Implementation (FastAPI)

### Tenant Context Middleware

```python
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import jwt
from app.core.config import settings

class TenantMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip for public endpoints
        if request.url.path in ["/health", "/api/v1/auth/login", "/api/v1/auth/register"]:
            return await call_next(request)

        # Extract JWT token
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing authentication token")

        token = auth_header.split(" ")[1]

        try:
            # Decode JWT and extract tenant_id
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            tenant_id = payload.get("tenant_id")
            user_id = payload.get("user_id")

            if not tenant_id:
                raise HTTPException(status_code=401, detail="Invalid token: missing tenant_id")

            # Attach to request state
            request.state.tenant_id = tenant_id
            request.state.user_id = user_id

        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")

        response = await call_next(request)
        return response
```

### Database Session with Tenant Context

```python
from sqlalchemy.orm import Session
from fastapi import Depends, Request
from app.core.database import get_db

async def get_tenant_db(request: Request, db: Session = Depends(get_db)) -> Session:
    """
    Get database session with tenant context set
    """
    tenant_id = request.state.tenant_id

    # Set PostgreSQL session variable for RLS
    db.execute(f"SET app.current_tenant_id = '{tenant_id}'")

    return db
```

---

## Security Considerations

### Preventing Tenant Data Leakage

1. **Automatic Filtering**: すべてのORMクエリに自動的にテナントフィルタを適用
2. **RLS Enforcement**: データベースレベルで強制的にフィルタリング
3. **JWT Validation**: すべてのリクエストでテナントIDを検証
4. **Audit Logging**: テナント間のアクセス試行をログ記録

### Performance Optimization

1. **Indexing**: `(tenant_id, created_at)` の複合インデックス
2. **Connection Pooling**: テナントごとではなく共有接続プール
3. **Caching**: テナント設定をRedisにキャッシュ

### Backup Strategy

1. **Full Backup**: すべてのテナントデータを含む日次バックアップ
2. **Point-in-Time Recovery**: 7日間のWALログ保持
3. **Tenant-Specific Backup**: 大口顧客向けの個別バックアップオプション
