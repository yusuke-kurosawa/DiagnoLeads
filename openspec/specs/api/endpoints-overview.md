# API Endpoints Overview (Draft)

Status: Proposed
Created: 2025-11-10

## Assessments
- POST   /api/v1/tenants/{tenant_id}/assessments
- PATCH  /api/v1/tenants/{tenant_id}/assessments/{id}
- POST   /api/v1/tenants/{tenant_id}/assessments/{id}/publish
- POST   /api/v1/tenants/{tenant_id}/assessments/{id}/rollback

## AI
- POST /api/v1/tenants/{tenant_id}/ai/assessments
- POST /api/v1/tenants/{tenant_id}/ai/insights
- POST /api/v1/tenants/{tenant_id}/ai/rephrase

## Embed (Public)
- GET  /embed/assessments/{public_id}.js
- POST /api/v1/public/assessments/{public_id}/responses

## Leads
- GET    /api/v1/tenants/{tenant_id}/leads?segment=hot&page=1
- PATCH  /api/v1/tenants/{tenant_id}/leads/{id}
- POST   /api/v1/tenants/{tenant_id}/segments

## Analytics
- GET /api/v1/tenants/{tenant_id}/analytics/overview?range=30d
- GET /api/v1/tenants/{tenant_id}/analytics/funnel?range=30d

## Integrations
- POST /api/v1/tenants/{tenant_id}/integrations/{provider}/connect
- POST /api/v1/tenants/{tenant_id}/integrations/{provider}/sync

## Security
- すべての private エンドポイントは JWT 必須 + tenant_id 検証
- Public は署名付き public_id のみアクセス可能
