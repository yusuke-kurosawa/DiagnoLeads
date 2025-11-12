# Data Model: DiagnoLeads

**Description**: Multi-tenant B2B assessment platform complete data model

**Version**: 1.0  
**Last Updated**: 2025-11-12  
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

### QRCode Relationships

- **QRCode::QRCodeScan** = 1:N
  - Reference: QRCode.id → QRCodeScan.qr_code_id
  - On Delete: Cascade
  - Description: QRCode has many scans

---

## 📊 Constraints

### Unique Constraints

- **Tenant**: [slug]
- **User**: [email]
- **QRCode**: [code]

### Indexes (for Performance)

- **User**: [tenant_id, email] - Multi-tenant queries
- **Assessment**: [tenant_id, status] - Listing by status
- **Response**: [assessment_id, completed_at] - Analytics
- **Lead**: [tenant_id, lead_score] - Lead scoring
- **Lead**: [tenant_id, status] - Status filtering
- **QRCode**: [tenant_id, code] - Quick lookup
- **Integration**: [tenant_id, service_type] - Integration lookup

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

---

## 🔄 Migration Notes

- RLS policies implemented in migration `f5a2c3d8e9b1_add_row_level_security.py`
- Authentication enhancements in migration `f7e1c2d9b3a4_add_authentication_enhancements.py`
- All migrations use parametrized queries for security

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
