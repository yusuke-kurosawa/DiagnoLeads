# DiagnoLeads - Implementation Roadmap

**Last Updated**: 2025-11-23
**Planning Horizon**: 12 months
**Current Implementation**: 92% Complete

---

## 🎯 Roadmap Overview

このロードマップは、DiagnoLeadsの未実装機能を優先度別に整理し、段階的な実装計画を提示します。

### Roadmap Phases

| Phase | Timeline | Focus | Features |
|-------|----------|-------|----------|
| **Phase A** | Week 1-2 | Quick Wins | 4 features |
| **Phase B** | Month 1-2 | Core Enhancements | 8 features |
| **Phase C** | Month 3-6 | Advanced Features | 12 features |
| **Phase D** | Month 7-12 | Innovation | 8 features |

---

## 📊 Prioritization Framework

### Priority Calculation

```
Priority Score = (Business Value × 0.4) + (User Impact × 0.3) + (Technical Urgency × 0.2) - (Effort × 0.1)
```

**Business Value** (0-10):
- Revenue impact
- Customer retention
- Competitive advantage

**User Impact** (0-10):
- Number of users affected
- Frequency of use
- Critical user journey

**Technical Urgency** (0-10):
- Technical debt reduction
- Security improvements
- Performance impact

**Effort** (1-10):
- Development time
- Complexity
- Dependencies

---

## 🚀 Phase A: Quick Wins (Week 1-2)

**Goal**: Complete high-impact, low-effort features to reach 95%+ implementation

### A1. PDF Export Completion ⭐⭐⭐

**Specification**: `report-export-formats.md`

**Priority Score**: 8.5
- Business Value: 8/10 (complete export functionality)
- User Impact: 7/10 (used weekly by admins)
- Technical Urgency: 3/10
- Effort: 3/10 (2-3 days)

**Implementation**:
```python
# Option 1: ReportLab (more control)
def export_to_pdf(self, report_name, data_points, summary):
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Table, Paragraph

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    # ...

# Option 2: WeasyPrint (HTML → PDF, easier styling)
def export_to_pdf_weasyprint(self, html_template):
    from weasyprint import HTML
    return HTML(string=html_template).write_pdf()
```

**Success Criteria**:
- [ ] PDF generation with table and summary
- [ ] Branding (logo, colors)
- [ ] File size < 5MB for 1000 rows
- [ ] Test coverage > 80%

**Dependencies**: None

---

### A2. Email Template Engine ⭐⭐ ✅ COMPLETED

**Specification**: `email-service.md`

**Priority Score**: 7.2
- Business Value: 6/10
- User Impact: 5/10
- Technical Urgency: 2/10
- Effort: 2/10 (1 day)

**Implementation**:
```python
from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader('templates/email'))

# Password reset email
template = env.get_template('password_reset.html')
html_content = template.render(
    user_name=user_name,
    reset_link=reset_link,
    company_logo=settings.COMPANY_LOGO_URL,
)
```

**Success Criteria**:
- [x] Jinja2 integration
- [x] 3 base templates (password reset, welcome, lead notification)
- [x] Template variables documentation
- [x] Fallback to inline HTML if template missing

**Completed**: 2025-11-23
**Commit**: feat(email): Add Jinja2 template engine for customizable emails

---

### A3. Dashboard UI Skeleton ⭐⭐ ✅ COMPLETED

**Specification**: `error-logging-monitoring.md`, `audit-logging.md`, `usage-tracking-billing.md`

**Priority Score**: 7.0
- Business Value: 7/10 (visibility)
- User Impact: 6/10
- Technical Urgency: 2/10
- Effort: 3/10 (3-5 days)

**Implementation**:
```tsx
// /frontend/src/pages/admin/ErrorLogPage.tsx - Error log dashboard
// /frontend/src/pages/admin/AuditLogPage.tsx - Audit log dashboard (already existed)
// /frontend/src/pages/admin/AIUsagePage.tsx - AI usage dashboard
```

**Success Criteria**:
- [x] Error log dashboard (stats + table)
- [x] Audit log dashboard (activity timeline) - Already existed
- [x] AI Usage tracking dashboard (cost breakdown)
- [x] Responsive design (mobile-friendly)
- [x] Services created (errorLogService.ts, aiUsageService.ts)

**Completed**: 2025-11-23
**Files Created**:
- `/frontend/src/services/errorLogService.ts` - Error log API service
- `/frontend/src/services/aiUsageService.ts` - AI usage API service
- `/frontend/src/pages/admin/ErrorLogPage.tsx` - Error log dashboard UI
- `/frontend/src/pages/admin/AIUsagePage.tsx` - AI usage dashboard UI

---

### A4. QR Code Preview ⭐ ✅ COMPLETED

**Specification**: `qr-code-distribution.md`

**Priority Score**: 6.5
- Business Value: 5/10
- User Impact: 6/10
- Technical Urgency: 1/10
- Effort: 1/10 (1 day)

**Implementation**:
```python
@router.post("/qr-codes/preview")
async def preview_qr_code(preview_data: QRCodePreviewRequest):
    """Generate QR code preview without saving"""
    # Generate QR code image
    qr_img = service.generate_qr_image(...)
    png_bytes = service.qr_image_to_bytes(qr_img, format="PNG")

    return Response(content=png_bytes, media_type="image/png")

@router.get("/{tenant_id}/qr-codes/{qr_code_id}/download")
async def download_qr_code(qr_code_id: UUID):
    """Download existing QR code as PNG"""
    # Regenerate image on-the-fly
    qr_img = service.generate_qr_image(...)
    return Response(content=png_bytes, media_type="image/png")
```

**Success Criteria**:
- [x] Preview endpoint (POST /qr-codes/preview)
- [x] Download endpoint (GET /{tenant_id}/qr-codes/{qr_code_id}/download)
- [x] QRCodePreviewRequest schema
- [x] Specification updated

**Completed**: 2025-11-23
**Commit**: feat(qr-codes): Add QR code preview and download functionality

---

## 📈 Phase B: Core Enhancements (Month 1-2)

**Goal**: Add high-value features to improve user experience and sales efficiency

### B1. Custom Tenant Templates ⭐⭐⭐

**Specification**: `industry-templates.md`

**Priority Score**: 8.2
- Business Value: 9/10 (differentiation)
- User Impact: 7/10
- Technical Urgency: 2/10
- Effort: 5/10 (1-2 weeks)

**Implementation**:
```python
class TenantIndustryTemplate(Base):
    __tablename__ = "tenant_industry_templates"

    tenant_id = Column(UUID, ForeignKey("tenants.id"))
    industry_key = Column(String(100))
    name = Column(String(200))
    common_pain_points = Column(JSON)
    # ...

# Usage
template = get_industry_template(industry, tenant_id=tenant_id)
```

**Success Criteria**:
- [ ] Database model
- [ ] CRUD API
- [ ] UI for template creation/editing
- [ ] Fallback to global templates
- [ ] Migration for existing tenants

**Dependencies**: None

---

### B2. CRM Integration (Salesforce/HubSpot) ⭐⭐⭐ 🔨 IN PROGRESS

**Specification**: `crm-integration.md`, External Integrations

**Priority Score**: 9.0
- Business Value: 10/10 (sales efficiency)
- User Impact: 9/10
- Technical Urgency: 3/10
- Effort: 7/10 (3-4 weeks)

**Phase 1 Implementation** (Week 1 - ✅ COMPLETED):
```python
# /backend/app/integrations/crm/base.py - Abstract CRM client
# /backend/app/integrations/crm/salesforce_client.py - Salesforce implementation
# /backend/app/integrations/crm/hubspot_client.py - HubSpot implementation
```

**Success Criteria**:
- [x] **Phase 1**: CRM base class with abstract methods
- [x] **Phase 1**: Salesforce client (create/update/get/delete lead)
- [x] **Phase 1**: HubSpot client (create/update/get/delete contact)
- [x] **Phase 1**: Field mapping logic (DiagnoLeads → CRM)
- [x] **Phase 1**: Retry policy integration
- [x] **Phase 1**: Detailed specification document
- [ ] **Phase 2**: OAuth authentication flow (Salesforce + HubSpot)
- [ ] **Phase 2**: Token refresh & encryption
- [ ] **Phase 3**: Bi-directional sync (DiagnoLeads ↔ CRM)
- [ ] **Phase 3**: Field mapping UI
- [ ] **Phase 3**: Webhook for real-time sync
- [ ] **Phase 4**: Comprehensive error handling & monitoring

**Progress**: Phase 1 Complete (25% of total effort)
**Started**: 2025-11-23
**Next Phase**: OAuth authentication (Week 2)

**Dependencies**: Trigger.dev for async jobs

---

### B3. Auto Status Transitions ⭐⭐

**Specification**: `lead-status-transition.md`

**Priority Score**: 7.8
- Business Value: 8/10
- User Impact: 7/10
- Technical Urgency: 2/10
- Effort: 4/10 (1-2 weeks)

**Implementation**:
```python
class AutoStatusTransition:
    def check_transitions(self):
        """定期実行（毎時）でステータス自動更新"""
        # new → contacted (24時間経過 + メール開封)
        leads = db.query(Lead).filter(
            Lead.status == "new",
            Lead.created_at < now() - timedelta(hours=24),
            Lead.email_opened == True,
        ).all()

        for lead in leads:
            lead.status = "contacted"
            db.commit()

            # Slack通知
            await slack_service.notify_status_change(lead)
```

**Success Criteria**:
- [ ] Email open tracking
- [ ] Auto transition rules
- [ ] Scheduled job (Trigger.dev)
- [ ] Notification on transition
- [ ] Manual override option

**Dependencies**: Email tracking, Trigger.dev

---

### B4. Dynamic Lead Scoring ⭐⭐

**Specification**: `lead-search-scoring.md`

**Priority Score**: 7.5
- Business Value: 8/10
- User Impact: 6/10
- Technical Urgency: 2/10
- Effort: 4/10 (1-2 weeks)

**Implementation**:
```python
class DynamicScoringService:
    SCORE_DELTA = {
        "email_opened": +5,
        "link_clicked": +10,
        "document_downloaded": +15,
        "demo_requested": +30,
        "pricing_page_viewed": +20,
    }

    def update_score(self, lead_id: UUID, event: str):
        lead = db.query(Lead).get(lead_id)
        lead.score += self.SCORE_DELTA.get(event, 0)
        lead.score = min(100, lead.score)
        db.commit()

        # Hot Lead になったら通知
        if lead.score >= 61 and old_score < 61:
            await slack_service.notify_hot_lead(lead)
```

**Success Criteria**:
- [ ] Event tracking (email, clicks, page views)
- [ ] Score update logic
- [ ] Hot Lead threshold notification
- [ ] Score history tracking

**Dependencies**: Email tracking, Analytics events

---

### B5-B8. Other Enhancements

| # | Feature | Priority | Effort | Timeline |
|---|---------|----------|--------|----------|
| B5 | Real-time Slack Alerts | 7.0 | 2 days | Week 3 |
| B6 | SendGrid/AWS SES Integration | 6.8 | 3 days | Week 4 |
| B7 | SLA Tracking for Leads | 6.5 | 1 week | Week 5-6 |
| B8 | Scheduled Report Exports | 6.2 | 1 week | Week 7-8 |

---

## 🧠 Phase C: Advanced Features (Month 3-6)

**Goal**: Add AI/ML capabilities and advanced analytics

### C1. ML-Based Conversion Prediction ⭐⭐⭐

**Specification**: `lead-search-scoring.md`

**Priority Score**: 8.5
- Business Value: 9/10 (predictive sales)
- User Impact: 8/10
- Technical Urgency: 2/10
- Effort: 8/10 (4-6 weeks)

**Implementation**:
```python
from sklearn.ensemble import RandomForestClassifier

class ConversionPredictionModel:
    def train(self, historical_leads):
        X = [[
            lead.score,
            lead.email_open_rate,
            lead.days_since_created,
            lead.interaction_count,
            self._encode_industry(lead.industry),
        ] for lead in historical_leads]

        y = [1 if lead.status == "converted" else 0
             for lead in historical_leads]

        self.model = RandomForestClassifier(n_estimators=100)
        self.model.fit(X, y)

    def predict_probability(self, lead):
        return self.model.predict_proba(...)[0][1]
```

**Success Criteria**:
- [ ] Model training pipeline
- [ ] Prediction API
- [ ] Daily model retraining
- [ ] Conversion probability displayed in UI
- [ ] A/B test vs manual scoring

**Dependencies**: Historical lead data (>500 samples)

---

### C2. A/B Testing Framework ⭐⭐

**Specification**: `industry-templates.md`, `lead-analysis-actions.md`

**Priority Score**: 7.5
- Business Value: 8/10
- User Impact: 6/10
- Technical Urgency: 1/10
- Effort: 6/10 (2-3 weeks)

**Implementation**:
```python
class ABTestService:
    def get_variant(self, tenant_id, test_id):
        """ランダムにバリアントを選択"""
        hash_value = hashlib.md5(f"{tenant_id}{test_id}".encode()).hexdigest()
        variant_idx = int(hash_value, 16) % 2
        return "A" if variant_idx == 0 else "B"

    def track_conversion(self, test_id, variant, converted):
        """コンバージョン記録"""
        ABTestResult(
            test_id=test_id,
            variant=variant,
            converted=converted,
        )
```

**Success Criteria**:
- [ ] Variant assignment
- [ ] Conversion tracking
- [ ] Statistical significance calculation
- [ ] Dashboard for results
- [ ] Auto winner selection

**Dependencies**: Analytics infrastructure

---

### C3-C12. Other Advanced Features

| # | Feature | Priority | Effort | Business Value |
|---|---------|----------|--------|----------------|
| C3 | Circuit Breaker Pattern | 7.2 | 1 week | Reliability |
| C4 | Fuzzy Search | 7.0 | 1 week | UX |
| C5 | Custom Lead Statuses | 6.8 | 2 weeks | Flexibility |
| C6 | Email Open/Click Tracking | 6.5 | 1 week | Engagement |
| C7 | Multi-language Templates | 6.2 | 3 weeks | I18n |
| C8 | Advanced Filtering UI | 6.0 | 2 weeks | UX |
| C9 | Webhook Integration | 5.8 | 2 weeks | Extensibility |
| C10 | Tag-based Search | 5.5 | 1 week | Organization |
| C11 | SIEM Integration | 5.0 | 2 weeks | Security |
| C12 | Rate Limiting Dashboard | 4.8 | 1 week | Monitoring |

---

## 🔬 Phase D: Innovation (Month 7-12)

**Goal**: Cutting-edge features for competitive differentiation

### D1. AI-Powered Assessment Generator V2 ⭐⭐⭐

**Specification**: New - Enhanced AI Support

**Priority Score**: 8.0
- Business Value: 9/10 (differentiation)
- User Impact: 7/10
- Technical Urgency: 1/10
- Effort: 8/10 (6-8 weeks)

**Features**:
- Natural language assessment creation ("Create a marketing assessment for SaaS companies")
- Auto-improvement based on completion rates
- Multi-lingual assessment generation
- Industry-specific question banks

---

### D2. Predictive Lead Nurturing ⭐⭐

**Priority Score**: 7.5

**Features**:
- AI recommends optimal follow-up timing
- Personalized email content generation
- Multi-channel nurturing (email, LinkedIn, Slack)
- Success prediction per channel

---

### D3-D8. Other Innovation Features

| # | Feature | Priority | Description |
|---|---------|----------|-------------|
| D3 | Real-time Collaboration | 7.0 | Multi-user assessment editing |
| D4 | Voice-based Assessments | 6.5 | Voice UI integration |
| D5 | Assessment Recommendation Engine | 6.2 | Suggest assessments to create |
| D6 | Competitive Intelligence | 6.0 | Benchmark against industry |
| D7 | White-label Platform | 5.8 | Tenant-branded sub-domains |
| D8 | Mobile App (React Native) | 5.5 | iOS/Android native apps |

---

## 📅 Timeline Gantt Chart

```
Month 1-2 (Quick Wins + Core Enhancements):
Week 1-2:  [A1 PDF][A2 Template][A3 Dashboard][A4 QR]
Week 3-4:  [B1 Custom Templates────────────────]
Week 5-6:  [B2 CRM Integration──────────────────]
Week 7-8:  [B3 Auto Status][B4 Dynamic Score]

Month 3-6 (Advanced Features):
Month 3:   [C1 ML Prediction──────────][C2 A/B Testing──]
Month 4:   [C3 Circuit][C4 Fuzzy][C5 Custom Status───]
Month 5:   [C6 Tracking][C7 i18n──────────────]
Month 6:   [C8 Filter UI][C9 Webhook][C10 Tags]

Month 7-12 (Innovation):
Month 7-9:  [D1 AI Generator V2─────────────────────]
Month 10-11:[D2 Predictive Nurturing────────────]
Month 12:   [D3 Collaboration][D4 Voice][D5 Recommend]
```

---

## 📊 Resource Allocation

### Team Composition (Recommended)

| Role | Allocation | Phase A | Phase B | Phase C | Phase D |
|------|-----------|---------|---------|---------|---------|
| **Backend Engineer** | 1.0 FTE | 60% | 70% | 80% | 60% |
| **Frontend Engineer** | 1.0 FTE | 40% | 60% | 50% | 40% |
| **ML Engineer** | 0.5 FTE | 0% | 0% | 80% | 100% |
| **DevOps** | 0.3 FTE | 20% | 30% | 40% | 30% |
| **QA** | 0.5 FTE | 50% | 60% | 70% | 60% |

---

## 💰 ROI Estimation

### Phase A (Quick Wins)
- **Investment**: 2 weeks × 2.5 FTE = 5 person-weeks
- **ROI**: +10% user satisfaction, +5% retention
- **Payback**: 1 month

### Phase B (Core Enhancements)
- **Investment**: 2 months × 3 FTE = 24 person-weeks
- **ROI**: +30% sales efficiency, +15% conversion rate
- **Payback**: 3 months

### Phase C (Advanced Features)
- **Investment**: 4 months × 3.5 FTE = 56 person-weeks
- **ROI**: +50% lead quality, +20% LTV
- **Payback**: 6 months

### Phase D (Innovation)
- **Investment**: 6 months × 3 FTE = 72 person-weeks
- **ROI**: Competitive moat, premium pricing (+30%)
- **Payback**: 12 months

---

## 🎯 Success Metrics

### Key Performance Indicators

| Metric | Current | Phase A | Phase B | Phase C | Phase D |
|--------|---------|---------|---------|---------|---------|
| **Implementation %** | 92% | 95% | 98% | 99% | 100% |
| **Test Coverage** | 73% | 75% | 80% | 85% | 90% |
| **User NPS** | - | 40 | 50 | 60 | 70 |
| **Lead Conversion Rate** | 5% | 5.5% | 6.5% | 7.5% | 9% |
| **Sales Cycle Days** | 30 | 28 | 25 | 20 | 15 |
| **Monthly Active Tenants** | 10 | 15 | 30 | 60 | 100 |

---

## 🚧 Risks & Mitigation

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| **ML model accuracy low** | Medium | High | Collect more training data, A/B test |
| **CRM integration complexity** | High | High | Start with Salesforce only, then expand |
| **Performance degradation** | Medium | Medium | Load testing, caching strategy |
| **Scope creep** | High | Medium | Strict sprint planning, weekly review |
| **Team capacity** | Medium | High | Hire contractors for Phase C/D |

---

## 📝 Next Steps

### Immediate Actions (This Week)

1. **Review and Approve Roadmap** with stakeholders
2. **Create Jira/Linear Tickets** for Phase A features
3. **Assign Owners** for each Phase A feature
4. **Set Up Weekly Sync** for roadmap tracking
5. **Begin Phase A.1** (PDF Export) immediately

### Monthly Review Process

- **Week 1 of each month**: Roadmap review & adjustments
- **Week 2**: Sprint planning based on roadmap
- **Week 3**: Mid-sprint check-in
- **Week 4**: Sprint retrospective & next month planning

---

**Last Updated**: 2025-11-23
**Next Review**: 2025-12-01
**Owner**: Engineering Team Lead
