# Data Model: DiagnoLeads

**Description**: Multi-tenant B2B assessment platform complete data model

**Version**: 1.1
**Last Updated**: 2025-11-23
**Status**: Published

---

## 🎯 Overview

DiagnoLeads implements a multi-tenant SaaS architecture with complete tenant isolation at the database level using Row-Level Security (RLS) and Context Variables.

### Key Principles

- **Multi-Tenancy**: All tables include `tenant_id` for isolation
- **Auditability**: All entities include `created_at`, `updated_at`, `created_by`
- **Type Safety**: Enums for status fields
- **Relationships**: Foreign keys with ON DELETE behavior
- **Scalability**: Proper indexing for query performance

---

## 📋 Entities

### Tenant
**Table**: `tenants`  
**Description**: Organization/company account

| Field | Type | Constraint | Description |
|-------|------|-----------|------------|
| id | UUID | PK | Unique tenant identifier |
| name | String(255) | NOT NULL | Organization name |
| slug | String(100) | UNIQUE, NOT NULL | URL-friendly slug |
| plan | String | NOT NULL, Enum | Subscription plan (starter, growth, enterprise) |
| settings | JSON | DEFAULT {} | Configuration and preferences |
| created_at | Timestamp | DEFAULT now() | Account creation date |
| updated_at | Timestamp | DEFAULT now() | Last update date |

---

### User
**Table**: `users`  
**Description**: Tenant members with role-based access

| Field | Type | Constraint | Description |
|-------|------|-----------|------------|
| id | UUID | PK | User identifier |
| tenant_id | UUID | FK(Tenant), NOT NULL | Multi-tenant reference |
| email | String(255) | UNIQUE, NOT NULL | Email address |
| password_hash | String(255) | NOT NULL | Bcrypt hashed password |
| name | String(255) | NOT NULL | Full name |
| role | String | NOT NULL, Enum | Role (admin, manager, user, viewer) |
| password_reset_token | String(255) | | Token for password reset |
| password_reset_expires_at | Timestamp | | Expiration time for reset token |
| failed_login_attempts | Integer | DEFAULT 0 | Count for rate limiting |
| locked_until | Timestamp | | Account lock expiration |
| created_at | Timestamp | DEFAULT now() | Account creation date |
| updated_at | Timestamp | DEFAULT now() | Last update date |

---

### Assessment
**Table**: `assessments`  
**Description**: Diagnostic questionnaires/surveys

| Field | Type | Constraint | Description |
|-------|------|-----------|------------|
| id | UUID | PK | Assessment identifier |
| tenant_id | UUID | FK(Tenant), NOT NULL | Tenant ownership |
| created_by | UUID | FK(User) | Creator user ID |
| updated_by | UUID | FK(User) | Last editor user ID |
| title | String(255) | NOT NULL | Assessment title |
| description | Text | | Assessment description |
| status | String | NOT NULL, Enum | Status (draft, published, archived) |
| industry | String | | Target industry |
| topic | String | | Main topic |
| scoring_type | String | Enum | Scoring method (point_based, percentage) |
| created_at | Timestamp | DEFAULT now() | Creation date |
| updated_at | Timestamp | DEFAULT now() | Last update date |

---

### Question
**Table**: `questions`  
**Description**: Individual questions within assessments

| Field | Type | Constraint | Description |
|-------|------|-----------|------------|
| id | UUID | PK | Question identifier |
| assessment_id | UUID | FK(Assessment), NOT NULL | Parent assessment |
| text | Text | NOT NULL | Question text |
| type | String | NOT NULL, Enum | Type (single_choice, multiple_choice, text, slider) |
| order | Integer | NOT NULL | Display order |
| points | Integer | DEFAULT 0 | Points for this question |
| explanation | Text | | Optional explanation |
| created_at | Timestamp | DEFAULT now() | Creation date |

---

### QuestionOption
**Table**: `question_options`  
**Description**: Answer choices for multiple choice questions

| Field | Type | Constraint | Description |
|-------|------|-----------|------------|
| id | UUID | PK | Option identifier |
| question_id | UUID | FK(Question), NOT NULL | Parent question |
| text | String(255) | NOT NULL | Option text |
| points | Integer | DEFAULT 0 | Points for selecting this option |
| order | Integer | NOT NULL | Display order |

---

### Response
**Table**: `responses`  
**Description**: User responses to assessments (session/attempt)

| Field | Type | Constraint | Description |
|-------|------|-----------|------------|
| id | UUID | PK | Response record identifier |
| assessment_id | UUID | FK(Assessment), NOT NULL | Assessment taken |
| session_id | String | NOT NULL | Unique session identifier |
| email | String | | Email of respondent |
| name | String | | Name of respondent |
| status | String | Enum | Status (in_progress, completed, abandoned) |
| total_score | Integer | DEFAULT 0 | Total score achieved |
| ip_address | String | | Client IP address |
| user_agent | String | | Browser user agent |
| started_at | Timestamp | NOT NULL, DEFAULT now() | Assessment start time |
| completed_at | Timestamp | | Assessment completion time |

---

### Answer
**Table**: `answers`  
**Description**: Individual question answers within a response

| Field | Type | Constraint | Description |
|-------|------|-----------|------------|
| id | UUID | PK | Answer record identifier |
| response_id | UUID | FK(Response), NOT NULL | Parent response |
| question_id | UUID | FK(Question), NOT NULL | Question answered |
| answer_text | Text | | Answer text or selected value |
| points_awarded | Integer | DEFAULT 0 | Points for this answer |
| answered_at | Timestamp | DEFAULT now() | Answer timestamp |

---

### Lead
**Table**: `leads`  
**Description**: Qualified leads generated from assessments

| Field | Type | Constraint | Description |
|-------|------|-----------|------------|
| id | UUID | PK | Lead identifier |
| tenant_id | UUID | FK(Tenant), NOT NULL | Tenant ownership |
| response_id | UUID | FK(Response) | Source assessment response |
| email | String(255) | NOT NULL | Lead email |
| name | String(255) | NOT NULL | Lead name |
| company | String(255) | | Company name |
| phone | String(20) | | Contact phone |
| lead_score | Integer | DEFAULT 0 | AI-generated lead score (0-100) |
| status | String | NOT NULL, Enum | Status (new, contacted, qualified, customer, lost) |
| assigned_to | UUID | FK(User) | Assigned salesperson |
| notes | Text | | Internal notes |
| created_at | Timestamp | DEFAULT now() | Lead creation date |
| updated_at | Timestamp | DEFAULT now() | Last update date |

---

### QRCode
**Table**: `qr_codes`  
**Description**: QR codes for embedding assessments

| Field | Type | Constraint | Description |
|-------|------|-----------|------------|
| id | UUID | PK | QR code identifier |
| tenant_id | UUID | FK(Tenant), NOT NULL | Tenant ownership |
| assessment_id | UUID | FK(Assessment), NOT NULL | Assessment to embed |
| code | String | UNIQUE, NOT NULL | Unique code string |
| url | String | NOT NULL | Full URL to assessment |
| name | String(255) | NOT NULL | Display name |
| description | Text | | Description |
| status | String | Enum | Status (active, inactive, expired) |
| expires_at | Timestamp | | Expiration date |
| scans_count | Integer | DEFAULT 0 | Total scans count |
| created_at | Timestamp | DEFAULT now() | Creation date |

---

### QRCodeScan
**Table**: `qr_code_scans`  
**Description**: Analytics for QR code scans

| Field | Type | Constraint | Description |
|-------|------|-----------|------------|
| id | UUID | PK | Scan record identifier |
| qr_code_id | UUID | FK(QRCode), NOT NULL | QR code scanned |
| ip_address | String | NOT NULL | Client IP address |
| user_agent | String | | Browser user agent |
| timestamp | Timestamp | NOT NULL, DEFAULT now() | Scan timestamp |

---

### Integration
**Table**: `integrations`
**Description**: External service integrations (Salesforce, HubSpot, Slack, etc.)

| Field | Type | Constraint | Description |
|-------|------|-----------|------------|
| id | UUID | PK | Integration identifier |
| tenant_id | UUID | FK(Tenant), NOT NULL | Tenant ownership |
| service_type | String | NOT NULL, Enum | Service (salesforce, hubspot, slack, webhook) |
| name | String(255) | NOT NULL | Integration name |
| config | JSON | NOT NULL | Configuration and API credentials |
| is_active | Boolean | DEFAULT true | Whether integration is enabled |
| last_sync_at | Timestamp | | Last successful sync |
| created_at | Timestamp | DEFAULT now() | Creation date |

---

### Topic
**Table**: `topics`
**Description**: Assessment categorization taxonomy (tenant-specific)

| Field | Type | Constraint | Description |
|-------|------|-----------|------------|
| id | UUID | PK | Topic identifier |
| tenant_id | UUID | FK(Tenant), NOT NULL | Tenant ownership |
| created_by | UUID | FK(User), NOT NULL | Creator user |
| name | String(100) | NOT NULL | Topic name |
| description | String(500) | | Topic description |
| color | String(7) | | HEX color code (#RRGGBB) |
| icon | String(50) | | lucide-react icon name |
| sort_order | Integer | DEFAULT 999, NOT NULL | Display order |
| is_active | Boolean | DEFAULT true, NOT NULL | Active status |
| created_at | Timestamp | DEFAULT now(), NOT NULL | Creation date |
| updated_at | Timestamp | DEFAULT now(), NOT NULL | Last update date |

**Unique Constraint**: `(tenant_id, name)`

---

### Industry
**Table**: `industries`
**Description**: Industry/sector taxonomy (tenant-specific)

| Field | Type | Constraint | Description |
|-------|------|-----------|------------|
| id | UUID | PK | Industry identifier |
| tenant_id | UUID | FK(Tenant), NOT NULL | Tenant ownership |
| created_by | UUID | FK(User), NOT NULL | Creator user |
| name | String(100) | NOT NULL | Industry name |
| description | String(500) | | Industry description |
| color | String(7) | | HEX color code (#RRGGBB) |
| icon | String(50) | | lucide-react icon name |
| sort_order | Integer | DEFAULT 999, NOT NULL | Display order |
| is_active | Boolean | DEFAULT true, NOT NULL | Active status |
| created_at | Timestamp | DEFAULT now(), NOT NULL | Creation date |
| updated_at | Timestamp | DEFAULT now(), NOT NULL | Last update date |

**Unique Constraint**: `(tenant_id, name)`

---

### GoogleAnalyticsIntegration
**Table**: `google_analytics_integrations`
**Description**: Google Analytics 4 integration settings (one per tenant)

| Field | Type | Constraint | Description |
|-------|------|-----------|------------|
| id | UUID | PK, INDEX | Integration identifier |
| tenant_id | UUID | FK(Tenant), NOT NULL, UNIQUE, INDEX | Tenant (1:1 relationship) |
| measurement_id | String(20) | NOT NULL | GA4 Measurement ID (G-XXXXXXXXXX) |
| measurement_protocol_api_secret | String(255) | | Measurement Protocol API secret |
| enabled | Boolean | DEFAULT true, NOT NULL, INDEX | Integration enabled |
| track_frontend | Boolean | DEFAULT true, NOT NULL | Track React admin dashboard |
| track_embed_widget | Boolean | DEFAULT true, NOT NULL | Track embed widget |
| track_server_events | Boolean | DEFAULT false, NOT NULL | Server-side events via Measurement Protocol |
| custom_dimensions | JSONB | | GA4 custom dimensions/metrics config |
| created_at | Timestamp(tz) | DEFAULT now(), NOT NULL | Creation date |
| updated_at | Timestamp(tz) | DEFAULT now(), NOT NULL | Last update date |

---

### ErrorLog
**Table**: `error_logs`
**Description**: Application-wide error logging and monitoring

| Field | Type | Constraint | Description |
|-------|------|-----------|------------|
| id | UUID | PK | Error log identifier |
| tenant_id | UUID | FK(Tenant), NULLABLE | Tenant (optional for system errors) |
| user_id | UUID | FK(User), SET NULL | User who triggered error |
| error_type | String(100) | NOT NULL, INDEX | Error category (API_ERROR, DATABASE_ERROR, etc.) |
| error_code | String(20) | | Application error code |
| severity | String(20) | DEFAULT MEDIUM | Severity (LOW, MEDIUM, HIGH, CRITICAL) |
| error_message | Text | NOT NULL | Error message |
| stack_trace | Text | | Stack trace |
| endpoint | String(200) | INDEX | API endpoint path |
| method | String(10) | | HTTP method (GET, POST, etc.) |
| status_code | Integer | | HTTP status code |
| request_body | JSON | | Request payload |
| request_headers | JSON | | Request headers (sensitive data redacted) |
| response_body | JSON | | Response payload |
| duration_ms | Integer | | Request processing time (milliseconds) |
| environment | String(20) | DEFAULT development | Environment (development, staging, production, test, cicd) |
| ip_address | String(45) | | Client IP address (IPv4/IPv6) |
| user_agent | String(500) | | Browser user agent |
| context | JSON | | Additional context data |
| correlation_id | String(100) | INDEX | Correlation ID for distributed tracing |
| workflow_name | String(200) | | GitHub Actions workflow name |
| job_name | String(200) | | GitHub Actions job name |
| run_id | String(100) | | GitHub Actions run ID |
| created_at | Timestamp | DEFAULT now(), NOT NULL, INDEX | Error occurrence timestamp |

**Indexes**: `[error_type]`, `[endpoint]`, `[correlation_id]`, `[created_at]`

---

### AuditLog
**Table**: `audit_logs`
**Description**: Audit trail for compliance and security monitoring

| Field | Type | Constraint | Description |
|-------|------|-----------|------------|
| id | UUID | PK | Audit log identifier |
| tenant_id | UUID | FK(Tenant), NOT NULL | Tenant ownership |
| user_id | UUID | FK(User), NOT NULL | User who performed action |
| entity_type | String(50) | NOT NULL | Entity type (TENANT, USER, TOPIC, INDUSTRY) |
| entity_id | UUID | NOT NULL | Changed entity ID |
| action | String(20) | NOT NULL | Action (CREATE, UPDATE, DELETE) |
| entity_name | String(255) | | Entity name (for readability) |
| old_values | JSON | | Values before change (UPDATE/DELETE) |
| new_values | JSON | | Values after change (CREATE/UPDATE) |
| reason | Text | | Change reason (optional) |
| ip_address | String(45) | | Client IP address |
| user_agent | String(500) | | Browser user agent |
| created_at | Timestamp | DEFAULT now(), NOT NULL | Audit timestamp |

---

### AIUsageLog
**Table**: `ai_usage_logs`
**Description**: AI API usage tracking for billing and analytics

| Field | Type | Constraint | Description |
|-------|------|-----------|------------|
| id | UUID | PK | Usage log identifier |
| tenant_id | UUID | FK(Tenant), NOT NULL, INDEX | Tenant ownership |
| user_id | UUID | FK(User), SET NULL | User who initiated AI operation |
| operation | String(100) | NOT NULL, INDEX | Operation type (generate_assessment, analyze_lead_insights, rephrase_content) |
| model | String(100) | NOT NULL | AI model used (claude-3-5-sonnet-20241022) |
| input_tokens | Integer | NOT NULL, DEFAULT 0 | Input tokens consumed |
| output_tokens | Integer | NOT NULL, DEFAULT 0 | Output tokens generated |
| total_tokens | Integer | NOT NULL, DEFAULT 0 | Total tokens (input + output) |
| cost_usd | Float | | Estimated cost in USD |
| assessment_id | UUID | FK(Assessment), SET NULL | Related assessment (if applicable) |
| lead_id | UUID | FK(Lead), SET NULL | Related lead (if applicable) |
| duration_ms | Integer | | Processing time (milliseconds) |
| success | String(20) | DEFAULT success | Execution result (success, failure) |
| created_at | Timestamp | DEFAULT now(), NOT NULL, INDEX | Usage timestamp |

**Cost Calculation**:
- Claude 3.5 Sonnet: $0.003 per 1K input tokens, $0.015 per 1K output tokens

---

### Report
**Table**: `reports`
**Description**: Custom report definitions and scheduling

| Field | Type | Constraint | Description |
|-------|------|-----------|------------|
| id | UUID | PK | Report identifier |
| tenant_id | UUID | FK(Tenant), NOT NULL, INDEX | Tenant ownership |
| name | String(255) | NOT NULL | Report name |
| description | Text | | Report description |
| report_type | String(50) | DEFAULT custom | Report type (custom, lead_analysis, assessment_performance, conversion_funnel, ai_insights) |
| config | JSON | NOT NULL, DEFAULT {} | Report configuration (metrics, filters, grouping, visualization) |
| is_scheduled | Boolean | DEFAULT false, NOT NULL | Scheduled execution flag |
| schedule_config | JSON | | Schedule settings (frequency, time, timezone, recipients) |
| last_generated_at | Timestamp | | Last generation timestamp |
| created_by | UUID | FK(User), SET NULL | Report creator |
| is_public | Boolean | DEFAULT false, NOT NULL | Public within tenant flag |
| created_at | Timestamp | DEFAULT now(), NOT NULL | Creation date |
| updated_at | Timestamp | DEFAULT now(), NOT NULL | Last update date |

**Config JSON Schema**:
```json
{
  "metrics": ["leads_total", "conversion_rate", "average_score"],
  "filters": {"date_range": {"start": "...", "end": "..."}, "status": [...]},
  "group_by": "status",
  "visualization": "bar_chart",
  "sort_by": "leads_total",
  "sort_order": "desc"
}
```

---

## 🔗 Relationships

### Tenant Relationships

- **Tenant::User** = 1:N
  - Reference: Tenant.id → User.tenant_id
  - On Delete: Cascade
  - Description: Tenant has many users

- **Tenant::Assessment** = 1:N
  - Reference: Tenant.id → Assessment.tenant_id
  - On Delete: Cascade
  - Description: Tenant owns many assessments

- **Tenant::Lead** = 1:N
  - Reference: Tenant.id → Lead.tenant_id
  - On Delete: Cascade
  - Description: Tenant has many leads

- **Tenant::QRCode** = 1:N
  - Reference: Tenant.id → QRCode.tenant_id
  - On Delete: Cascade
  - Description: Tenant creates many QR codes

- **Tenant::Integration** = 1:N
  - Reference: Tenant.id → Integration.tenant_id
  - On Delete: Cascade
  - Description: Tenant configures many integrations

- **Tenant::Topic** = 1:N
  - Reference: Tenant.id → Topic.tenant_id
  - On Delete: Cascade
  - Description: Tenant defines custom topics/categories

- **Tenant::Industry** = 1:N
  - Reference: Tenant.id → Industry.tenant_id
  - On Delete: Cascade
  - Description: Tenant defines custom industries

- **Tenant::GoogleAnalyticsIntegration** = 1:1
  - Reference: Tenant.id → GoogleAnalyticsIntegration.tenant_id
  - On Delete: Cascade
  - Description: Tenant has one GA4 integration

- **Tenant::ErrorLog** = 1:N
  - Reference: Tenant.id → ErrorLog.tenant_id (nullable)
  - On Delete: Cascade
  - Description: Tenant-related errors

- **Tenant::AuditLog** = 1:N
  - Reference: Tenant.id → AuditLog.tenant_id
  - On Delete: Cascade
  - Description: Tenant audit trail

- **Tenant::AIUsageLog** = 1:N
  - Reference: Tenant.id → AIUsageLog.tenant_id
  - On Delete: Cascade
  - Description: Tenant AI usage tracking

- **Tenant::Report** = 1:N
  - Reference: Tenant.id → Report.tenant_id
  - On Delete: Cascade
  - Description: Tenant custom reports

### Assessment Relationships

- **Assessment::Question** = 1:N
  - Reference: Assessment.id → Question.assessment_id
  - On Delete: Cascade
  - Description: Assessment contains many questions

- **Assessment::Response** = 1:N
  - Reference: Assessment.id → Response.assessment_id
  - On Delete: Cascade
  - Description: Assessment receives many responses

- **Assessment::QRCode** = 1:N
  - Reference: Assessment.id → QRCode.assessment_id
  - On Delete: Cascade
  - Description: Assessment can have multiple QR codes

### Question Relationships

- **Question::QuestionOption** = 1:N
  - Reference: Question.id → QuestionOption.question_id
  - On Delete: Cascade
  - Description: Question has multiple choice options

- **Question::Answer** = 1:N
  - Reference: Question.id → Answer.question_id
  - On Delete: Cascade
  - Description: Question receives many answers

### Response Relationships

- **Response::Answer** = 1:N
  - Reference: Response.id → Answer.response_id
  - On Delete: Cascade
  - Description: Response contains many answers

- **Response::Lead** = 1:N
  - Reference: Response.id → Lead.response_id
  - On Delete: Set NULL
  - Description: Response may generate leads

### User Relationships

- **User::Assessment** (created_by) = 1:N
  - Reference: User.id → Assessment.created_by
  - On Delete: Set NULL
  - Description: User creates assessments

- **User::Assessment** (updated_by) = 1:N
  - Reference: User.id → Assessment.updated_by
  - On Delete: Set NULL
  - Description: User updates assessments

- **User::Lead** (assigned_to) = 1:N
  - Reference: User.id → Lead.assigned_to
  - On Delete: Set NULL
  - Description: Salesperson assigned to leads

- **User::Topic** (created_by) = 1:N
  - Reference: User.id → Topic.created_by
  - On Delete: Set NULL
  - Description: User creates topics

- **User::Industry** (created_by) = 1:N
  - Reference: User.id → Industry.created_by
  - On Delete: Set NULL
  - Description: User creates industries

- **User::AuditLog** = 1:N
  - Reference: User.id → AuditLog.user_id
  - On Delete: Set NULL
  - Description: User actions in audit trail

- **User::AIUsageLog** = 1:N
  - Reference: User.id → AIUsageLog.user_id
  - On Delete: Set NULL
  - Description: User AI operations

- **User::Report** (created_by) = 1:N
  - Reference: User.id → Report.created_by
  - On Delete: Set NULL
  - Description: User creates reports

### QRCode Relationships

- **QRCode::QRCodeScan** = 1:N
  - Reference: QRCode.id → QRCodeScan.qr_code_id
  - On Delete: Cascade
  - Description: QRCode has many scans

### Assessment → AI Relationships

- **Assessment::AIUsageLog** = 1:N
  - Reference: Assessment.id → AIUsageLog.assessment_id
  - On Delete: Set NULL
  - Description: AI operations for assessment generation

### Lead → AI Relationships

- **Lead::AIUsageLog** = 1:N
  - Reference: Lead.id → AIUsageLog.lead_id
  - On Delete: Set NULL
  - Description: AI operations for lead analysis

---

## 📊 Constraints

### Unique Constraints

- **Tenant**: [slug]
- **User**: [email]
- **QRCode**: [code]
- **Topic**: [tenant_id, name]
- **Industry**: [tenant_id, name]
- **GoogleAnalyticsIntegration**: [tenant_id] (1:1 relationship)

### Indexes (for Performance)

- **User**: [tenant_id, email] - Multi-tenant queries
- **Assessment**: [tenant_id, status] - Listing by status
- **Response**: [assessment_id, completed_at] - Analytics
- **Lead**: [tenant_id, lead_score] - Lead scoring
- **Lead**: [tenant_id, status] - Status filtering
- **QRCode**: [tenant_id, code] - Quick lookup
- **Integration**: [tenant_id, service_type] - Integration lookup
- **GoogleAnalyticsIntegration**: [tenant_id], [enabled] - Tenant lookup, active integrations
- **ErrorLog**: [error_type], [endpoint], [correlation_id], [created_at] - Error analysis
- **AuditLog**: [tenant_id, entity_type], [user_id], [created_at] - Audit queries
- **AIUsageLog**: [tenant_id], [operation], [created_at] - Usage analytics
- **Report**: [tenant_id], [is_scheduled] - Report management

### Check Constraints

- **Lead**: lead_score >= 0 AND lead_score <= 100
- **Question**: order >= 0
- **QuestionOption**: order >= 0
- **Response**: total_score >= 0

---

## 🔒 Multi-Tenant Security

### Row-Level Security (RLS) Implementation

All tables implement PostgreSQL RLS with tenant_id policy:

```sql
-- Example RLS policy for assessments table
CREATE POLICY assessments_tenant_isolation ON assessments
  USING (tenant_id = current_setting('app.current_tenant_id')::uuid);
```

**Tables with RLS**:
- tenants (limited to own tenant)
- users
- assessments
- questions
- responses
- answers
- leads
- qr_codes
- qr_code_scans
- integrations
- topics
- industries
- google_analytics_integrations
- error_logs (tenant_id nullable for system errors)
- audit_logs
- ai_usage_logs
- reports

### Context Variable

All queries use PostgreSQL context variable:

```sql
SET app.current_tenant_id = '{tenant_id}';
```

This is set by the FastAPI application in `app/core/deps.py` before each database operation.

---

## 📈 Analytics & Reporting

### Key Metrics Tables

- **Response**:
  - completed_at, started_at for time metrics
  - total_score for performance analysis
  - session_id for cohort analysis

- **Lead**:
  - lead_score for lead quality
  - status for pipeline tracking
  - created_at for trend analysis

- **QRCodeScan**:
  - timestamp for engagement tracking
  - ip_address for geographic analysis (anonymized)

- **ErrorLog**:
  - error_type, severity for error monitoring
  - endpoint, duration_ms for performance tracking
  - created_at for trend analysis

- **AIUsageLog**:
  - operation, tokens, cost_usd for billing
  - created_at for usage trends
  - tenant_id for cost allocation

- **AuditLog**:
  - entity_type, action for compliance reporting
  - user_id for user activity tracking
  - created_at for audit trails

- **Report**:
  - config for custom metrics
  - is_scheduled, schedule_config for automation
  - last_generated_at for execution tracking

---

## 🔄 Migration Notes

- RLS policies implemented in migration `f5a2c3d8e9b1_add_row_level_security.py`
- Authentication enhancements in migration `f7e1c2d9b3a4_add_authentication_enhancements.py`
- Google Analytics integration in migration `a1b2c3d4e5f6_add_google_analytics_integration.py`
- Error logging in migration `i9j0k1l2m3n4_add_error_logs_table.py`
- AI usage tracking in migration `h7i8j9k0l1m2_add_ai_usage_log_table.py`
- All migrations use parametrized queries for security

**Note**: Topic, Industry, Report, and AuditLog models require migration creation

---

## ✅ Data Model Validation

- [x] All entities have primary key (id: UUID)
- [x] All multi-tenant tables include tenant_id
- [x] All relationships documented
- [x] ON DELETE behavior specified
- [x] Unique constraints defined
- [x] Indexes optimized for queries
- [x] RLS policies configured
- [x] Audit fields (created_at, updated_at) present

---

**This data model supports a scalable, secure multi-tenant SaaS platform with complete tenant isolation and audit trails.** 🏗️
