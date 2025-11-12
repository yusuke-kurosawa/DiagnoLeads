# OpenSpec ER Diagram Format Specification

**Version**: 1.0  
**Last Updated**: 2025-11-12  
**Status**: Published

---

## 📋 Overview

This specification defines how to represent Entity-Relationship diagrams in OpenSpec Markdown format. It enables automatic generation of ER diagrams in multiple formats (Mermaid, PlantUML, JSON).

### Goal

```
OpenSpec Markdown ER Definition
           ↓
ER Diagram Generator (Python)
           ↓
Multiple Output Formats:
├─ Mermaid (SVG)
├─ PlantUML (UML)
└─ JSON (Metadata)
```

---

## 🏗️ ER Diagram Format

### Structure

```markdown
# Data Model: [System Name]

**Description**: Brief description of the data model

**Version**: 1.0  
**Last Updated**: YYYY-MM-DD

## Entities

### [Entity Name]
**Table**: `[table_name]`  
**Description**: Entity description

| Field | Type | Constraint | Description |
|-------|------|-----------|------------|
| id | UUID | PK | Primary key |
| field1 | String | NOT NULL, UNIQUE | Field description |
| field2 | Integer | FK(OtherEntity) | Foreign key |
| created_at | Timestamp | DEFAULT now() | Audit field |

### [Another Entity]
...

## Relationships

- [EntityA]::[EntityB] = 1:N
  - Reference: EntityA.id → EntityB.entity_a_id
  - On Delete: Cascade
  - Description: A to B relationship

- [EntityC]::[EntityD] = N:N
  - Reference: [junction_table]
  - Description: Many-to-many relationship

## Constraints

- Unique Constraints:
  - [Entity].[field1, field2]

- Check Constraints:
  - [Entity].[field] > 0

- Indexes:
  - [Entity].[field1, field2] (for queries)
```

---

## 📐 Entity Definition

### Syntax

```markdown
### [Entity Name]
**Table**: `[table_name]`  
**Description**: What this entity represents

| Field | Type | Constraint | Description |
|-------|------|-----------|------------|
| id | UUID | PK | Unique identifier |
| created_by | UUID | FK(User) | Reference to User |
| status | String | NOT NULL, Enum | Status value |
```

### Field Types

| Type | PostgreSQL | Description |
|------|------------|-------------|
| UUID | uuid | Unique identifier |
| String | varchar | Text (default 255) |
| Integer | integer | Whole number |
| Decimal | numeric | Decimal number |
| Boolean | boolean | True/False |
| Timestamp | timestamp | Date and time |
| JSON | jsonb | JSON data |
| Array | array | Array type |
| Enum | enum | Enumerated type |
| Text | text | Large text |

### Constraints

| Constraint | Meaning | Example |
|-----------|---------|---------|
| PK | Primary Key | `id: UUID \| PK` |
| FK(Entity) | Foreign Key | `tenant_id: UUID \| FK(Tenant)` |
| NOT NULL | Required field | `email: String \| NOT NULL` |
| UNIQUE | Unique value | `slug: String \| UNIQUE` |
| DEFAULT value | Default value | `created_at: Timestamp \| DEFAULT now()` |
| Enum | Enumerated values | `role: String \| Enum(admin, user)` |
| CHECK expr | Validation | `age: Integer \| CHECK > 0` |

---

## 🔗 Relationships

### One-to-Many (1:N)

```markdown
- Parent::Child = 1:N
  - Reference: Parent.id → Child.parent_id
  - On Delete: Cascade
  - Description: One parent has many children
```

### Many-to-Many (N:N)

```markdown
- Table1::Table2 = N:N
  - Reference: [table1_table2] (junction table)
  - On Delete: Cascade
  - Description: Many-to-many relationship
```

### One-to-One (1:1)

```markdown
- Profile::User = 1:1
  - Reference: Profile.user_id → User.id
  - On Delete: Cascade
  - Description: User has one profile
```

---

## 📊 Complete Example: DiagnoLeads Data Model

```markdown
# Data Model: DiagnoLeads

**Description**: Multi-tenant B2B assessment platform data model

**Version**: 1.0  
**Last Updated**: 2025-11-12

## Entities

### Tenant
**Table**: `tenants`  
**Description**: Organization/company account

| Field | Type | Constraint | Description |
|-------|------|-----------|------------|
| id | UUID | PK | Tenant ID |
| name | String(255) | NOT NULL | Company name |
| slug | String(100) | UNIQUE, NOT NULL | URL slug |
| plan | String | NOT NULL, Enum | Subscription plan |
| settings | JSON | DEFAULT {} | Configuration |
| created_at | Timestamp | DEFAULT now() | Created date |
| updated_at | Timestamp | DEFAULT now() | Updated date |

### User
**Table**: `users`  
**Description**: Tenant users (members)

| Field | Type | Constraint | Description |
|-------|------|-----------|------------|
| id | UUID | PK | User ID |
| tenant_id | UUID | FK(Tenant), NOT NULL | Multi-tenant reference |
| email | String | UNIQUE, NOT NULL | Email address |
| password_hash | String | NOT NULL | Hashed password |
| name | String | NOT NULL | Full name |
| role | String | NOT NULL, Enum | admin, user, viewer |
| created_at | Timestamp | DEFAULT now() | Created date |

### Assessment
**Table**: `assessments`  
**Description**: Diagnostic questionnaire

| Field | Type | Constraint | Description |
|-------|------|-----------|------------|
| id | UUID | PK | Assessment ID |
| tenant_id | UUID | FK(Tenant), NOT NULL | Tenant ownership |
| created_by | UUID | FK(User) | Author |
| title | String | NOT NULL | Assessment title |
| description | Text | | Description |
| status | String | Enum | draft, published, archived |
| created_at | Timestamp | DEFAULT now() | Created date |

### Question
**Table**: `questions`  
**Description**: Questions in assessments

| Field | Type | Constraint | Description |
|-------|------|-----------|------------|
| id | UUID | PK | Question ID |
| assessment_id | UUID | FK(Assessment), NOT NULL | Parent assessment |
| text | Text | NOT NULL | Question text |
| type | String | Enum | single_choice, multiple_choice, text |
| order | Integer | NOT NULL | Display order |

### Response
**Table**: `responses`  
**Description**: User assessment responses

| Field | Type | Constraint | Description |
|-------|------|-----------|------------|
| id | UUID | PK | Response ID |
| assessment_id | UUID | FK(Assessment), NOT NULL | Assessment taken |
| user_id | UUID | FK(User) | User who responded |
| answers | JSON | NOT NULL | Answers data |
| completed_at | Timestamp | | Completion time |

### Lead
**Table**: `leads`  
**Description**: Qualified leads from assessments

| Field | Type | Constraint | Description |
|-------|------|-----------|------------|
| id | UUID | PK | Lead ID |
| tenant_id | UUID | FK(Tenant), NOT NULL | Tenant ownership |
| email | String | NOT NULL | Lead email |
| name | String | NOT NULL | Lead name |
| score | Integer | DEFAULT 0 | Lead score |
| status | String | Enum | new, contacted, qualified, lost |
| created_at | Timestamp | DEFAULT now() | Created date |

## Relationships

- Tenant::User = 1:N
  - Reference: Tenant.id → User.tenant_id
  - On Delete: Cascade
  - Description: One tenant has many users

- Tenant::Assessment = 1:N
  - Reference: Tenant.id → Assessment.tenant_id
  - On Delete: Cascade
  - Description: One tenant has many assessments

- Tenant::Lead = 1:N
  - Reference: Tenant.id → Lead.tenant_id
  - On Delete: Cascade
  - Description: One tenant has many leads

- Assessment::Question = 1:N
  - Reference: Assessment.id → Question.assessment_id
  - On Delete: Cascade
  - Description: Assessment has many questions

- Assessment::Response = 1:N
  - Reference: Assessment.id → Response.assessment_id
  - On Delete: Cascade
  - Description: Assessment has many responses

- User::Response = 1:N
  - Reference: User.id → Response.user_id
  - On Delete: Set NULL
  - Description: User has many responses

- User::Assessment = 1:N
  - Reference: User.id → Assessment.created_by
  - On Delete: Set NULL
  - Description: User created many assessments

## Constraints

- Unique Constraints:
  - Tenant: [slug]
  - User: [email]
  - Lead: [tenant_id, email]

- Indexes:
  - User: [tenant_id, email] (for multi-tenant queries)
  - Assessment: [tenant_id, status] (for listing)
  - Response: [assessment_id, created_at] (for analytics)
  - Lead: [tenant_id, score] (for lead scoring)
```

---

## 🔄 Auto-Generation Rules

### Mermaid Output

```
1. Each entity → erDiagram entity
2. Each FK → erDiagram relationship
3. Cardinality: PK (1), FK (N)
4. Visual format: entity block + relationships
```

### PlantUML Output

```
1. Each entity → @startuml class
2. Each field → class attribute
3. Each relationship → UML association
4. Cardinality: *, 1, N
```

### JSON Output

```
{
  "entities": [{"name": "...", "fields": [...]}],
  "relationships": [{"from": "...", "to": "...", "cardinality": "1:N"}]
}
```

---

## 📋 Usage Example

### 1. Define in OpenSpec

Create `openspec/specs/database/diagnoleads-data-model.md` with above format

### 2. Generate ER Diagram

```bash
python scripts/generate_er_diagram.py \
  openspec/specs/database/diagnoleads-data-model.md \
  --format mermaid \
  --output diagrams/er_diagram.md
```

### 3. Outputs Generated

```
diagrams/
├── er_diagram.md          # Mermaid ER
├── er_diagram.pu          # PlantUML
├── er_diagram.json        # JSON Metadata
└── er_diagram.svg         # SVG (rendered)
```

---

## ✅ Validation Rules

1. **Primary Keys**: Every entity must have `id: UUID | PK`
2. **Foreign Keys**: FK references must match entity names
3. **Relationships**: Cardinality must be defined (1:N, N:N, 1:1)
4. **Unique Constraints**: Duplicate fields not allowed
5. **Circular References**: Detect and handle (e.g., Tree structures)

---

## 🎯 Best Practices

### DO ✅

- Keep entity names singular (User, not Users)
- Use UUID for all primary keys
- Document relationships clearly
- Include descriptions for clarity
- Version your data model
- Update diagram after schema changes

### DON'T ❌

- Mix table and entity names
- Use ambiguous field names
- Skip relationship definitions
- Create circular dependencies without planning
- Leave outdated ER diagrams

---

## 🔗 Related Specs

- [Database Schema Design](./database-schema-design.md)
- [Multi-Tenant Architecture](../architecture/multi-tenant.md)
- [API Design](../api/api-design.md)

---

**This specification enables automatic generation of ER diagrams from OpenSpec definitions, ensuring documentation stays in sync with code.** 📊
