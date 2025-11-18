# API Endpoints Overview

**Status**: Approved  
**Version**: 2.0  
**Last Updated**: 2025-11-10

Complete API reference for DiagnoLeads platform, including core features and innovative extensions.

---

## Core APIs

### Assessments
```
POST   /api/v1/tenants/{tenant_id}/assessments
PATCH  /api/v1/tenants/{tenant_id}/assessments/{id}
POST   /api/v1/tenants/{tenant_id}/assessments/{id}/publish
POST   /api/v1/tenants/{tenant_id}/assessments/{id}/rollback
```

### AI Generation
```
POST   /api/v1/tenants/{tenant_id}/ai/assessments
POST   /api/v1/tenants/{tenant_id}/ai/insights
POST   /api/v1/tenants/{tenant_id}/ai/rephrase
```

### Embed Widget (Public)
```
GET    /embed/assessments/{public_id}.js
POST   /api/v1/public/assessments/{public_id}/responses
```

### Leads Management
```
GET    /api/v1/tenants/{tenant_id}/leads?segment=hot&page=1
PATCH  /api/v1/tenants/{tenant_id}/leads/{id}
POST   /api/v1/tenants/{tenant_id}/segments
```

### Analytics
```
GET    /api/v1/tenants/{tenant_id}/analytics/overview?range=30d
GET    /api/v1/tenants/{tenant_id}/analytics/funnel?range=30d
```

### Base Integrations
```
POST   /api/v1/tenants/{tenant_id}/integrations/{provider}/connect
POST   /api/v1/tenants/{tenant_id}/integrations/{provider}/sync
```

---

## Microsoft 365 Integration APIs

### Microsoft Teams
```
POST   /api/v1/integrations/teams/install
GET    /api/v1/integrations/teams
DELETE /api/v1/integrations/teams/{integration_id}
GET    /api/v1/integrations/teams/channels
POST   /api/v1/integrations/teams/send-assessment
POST   /api/v1/integrations/teams/send-dm
POST   /api/v1/integrations/teams/notify-lead
POST   /api/v1/integrations/teams/notify-bulk
POST   /api/v1/integrations/teams/bot/webhook
GET    /api/v1/integrations/teams/bot/sessions/{user_id}
```

### Microsoft Dynamics 365
```
POST   /api/v1/integrations/dynamics/install
POST   /api/v1/integrations/dynamics/sync-lead
GET    /api/v1/integrations/dynamics/mapping
PUT    /api/v1/integrations/dynamics/mapping
```

### Microsoft Outlook & Calendar
```
POST   /api/v1/integrations/outlook/add-to-calendar
POST   /api/v1/integrations/outlook/send-email
GET    /api/v1/integrations/outlook/signature-template
```

---

## Multi-Channel Distribution APIs

### LINE Official Account
```
POST   /api/v1/channels/line/install
POST   /api/v1/channels/line/send
POST   /api/v1/channels/line/webhook
GET    /api/v1/channels/line/friends
```

### SMS (Twilio)
```
POST   /api/v1/channels/sms/send
POST   /api/v1/channels/sms/send-bulk
GET    /api/v1/channels/sms/delivery-status/{campaign_id}
```

### Email Campaigns
```
POST   /api/v1/channels/email/send
GET    /api/v1/channels/email/templates
POST   /api/v1/channels/email/preview
```

### QR Code & NFC
```
GET    /api/v1/channels/qr-code/{assessment_id}
GET    /api/v1/channels/qr-code/{assessment_id}/poster
GET    /api/v1/channels/qr-code/{assessment_id}/stats
GET    /api/v1/channels/nfc/{assessment_id}/ndef
```

### WhatsApp Business
```
POST   /api/v1/channels/whatsapp/install
POST   /api/v1/channels/whatsapp/send
POST   /api/v1/channels/whatsapp/webhook
```

### Channel Analytics
```
GET    /api/v1/channels/analytics
```

---

## AI Optimization Engine APIs

### A/B Testing
```
POST   /api/v1/optimization/ab-tests
GET    /api/v1/optimization/ab-tests/{test_id}
POST   /api/v1/optimization/ab-tests/{test_id}/declare-winner
DELETE /api/v1/optimization/ab-tests/{test_id}
```

### AI Copywriting
```
POST   /api/v1/optimization/ai-copywriting/improve-question
POST   /api/v1/optimization/ai-copywriting/analyze-readability
POST   /api/v1/optimization/ai-copywriting/generate-variants
```

### Predictive Analytics
```
POST   /api/v1/optimization/predictions/train
GET    /api/v1/optimization/predictions/conversion-rate
GET    /api/v1/optimization/predictions/lead-quality/{lead_id}
GET    /api/v1/optimization/insights
```

---

## Real-time Collaboration APIs

### Session Management
```
POST   /api/v1/collaboration/sessions/{assessment_id}/join
POST   /api/v1/collaboration/sessions/{assessment_id}/leave
GET    /api/v1/collaboration/sessions/{assessment_id}/presences
```

### Locking
```
POST   /api/v1/collaboration/locks/{assessment_id}/{question_id}/acquire
POST   /api/v1/collaboration/locks/{assessment_id}/{question_id}/release
```

### Change Tracking
```
POST   /api/v1/collaboration/changes/{assessment_id}
GET    /api/v1/collaboration/history/{assessment_id}
POST   /api/v1/collaboration/history/{assessment_id}/revert
```

### Comments
```
POST   /api/v1/collaboration/comments
GET    /api/v1/collaboration/comments/{assessment_id}
PUT    /api/v1/collaboration/comments/{comment_id}
DELETE /api/v1/collaboration/comments/{comment_id}
POST   /api/v1/collaboration/comments/{comment_id}/resolve
```

---

## Advanced Features APIs

### Gamification
```
GET    /api/v1/gamification/badges
POST   /api/v1/gamification/badges/award
GET    /api/v1/gamification/leaderboard
GET    /api/v1/gamification/user-progress/{session_id}
```

### Assessment Marketplace
```
GET    /api/v1/marketplace/templates
GET    /api/v1/marketplace/templates/{id}
POST   /api/v1/marketplace/templates/{id}/purchase
POST   /api/v1/marketplace/templates/{id}/review
GET    /api/v1/marketplace/categories
POST   /api/v1/marketplace/templates/publish
```

### Video & Voice Assessments
```
POST   /api/v1/assessments/{id}/media/upload-video
POST   /api/v1/assessments/{id}/voice/transcribe
GET    /api/v1/assessments/{id}/voice/tts
```

### Assessment Chains (Funnel)
```
POST   /api/v1/assessments/{id}/chains
GET    /api/v1/assessments/{id}/chains
PUT    /api/v1/assessments/{id}/chains/{chain_id}
DELETE /api/v1/assessments/{id}/chains/{chain_id}
```

### White-Label
```
POST   /api/v1/white-label/domain
POST   /api/v1/white-label/branding
PUT    /api/v1/white-label/email-sender
GET    /api/v1/white-label/ssl-status
```

---

## Compliance & Security APIs

### GDPR Compliance
```
POST   /api/v1/compliance/gdpr/export-data
POST   /api/v1/compliance/gdpr/delete-data
GET    /api/v1/compliance/gdpr/consent-log
POST   /api/v1/compliance/gdpr/cookie-consent
```

### Security
```
GET    /api/v1/security/audit-logs
POST   /api/v1/security/2fa/enable
POST   /api/v1/security/2fa/verify
POST   /api/v1/security/sso/saml/login
GET    /api/v1/security/ip-whitelist
POST   /api/v1/security/ip-whitelist/add
```

---

## Webhooks & API-First

### Webhook Management
```
POST   /api/v1/webhooks
GET    /api/v1/webhooks
PUT    /api/v1/webhooks/{id}
DELETE /api/v1/webhooks/{id}
GET    /api/v1/webhooks/{id}/logs
POST   /api/v1/webhooks/{id}/test
```

### GraphQL Endpoint
```
POST   /graphql
```

---

## Authentication & Authorization

### Authentication
- **JWT Bearer Token**: Required for all private endpoints
- **API Keys**: Available for server-to-server integrations
- **OAuth 2.0**: Supported for third-party apps
- **SSO**: SAML 2.0 for enterprise

### Authorization
- **Tenant Isolation**: すべてのエンドポイントでtenant_idを検証
- **Role-Based Access Control (RBAC)**: Admin, Editor, Viewer
- **Resource-Level Permissions**: 診断、リード単位での権限管理

---

## Rate Limiting

| Tier | Rate Limit | Burst |
|------|-----------|-------|
| Free | 100 req/min | 120 |
| Pro | 1,000 req/min | 1,200 |
| Enterprise | 10,000 req/min | 12,000 |
| Public APIs | 60 req/min | 100 |

---

## Versioning

- **Current Version**: v1
- **Deprecation Policy**: 6ヶ月前に通知、12ヶ月サポート
- **Breaking Changes**: メジャーバージョンアップ時のみ

---

## SDKs & Client Libraries

- **Python**: `diagno-leads-python`
- **Node.js**: `@diagno-leads/sdk`
- **Ruby**: `diagno_leads`
- **PHP**: `diagno-leads/php-sdk`

---

## OpenAPI Specification

Full OpenAPI 3.1 spec: `https://api.diagnoleads.com/openapi.json`

---

## Related Documentation

- [Microsoft Teams Integration](../features/microsoft-teams-integration.md)
- [Multi-Channel Distribution](../features/multi-channel-distribution.md)
- [AI Optimization Engine](../features/ai-optimization-engine.md)
- [Real-time Collaboration](../features/realtime-collaboration.md)
- [QR Code Distribution](../features/qr-code-distribution.md)
- [Google Analytics Integration](../features/google-analytics-integration.md)
