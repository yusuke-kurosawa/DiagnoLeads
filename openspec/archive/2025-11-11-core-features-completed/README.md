# Core Features Specification - Change Proposal

**Date Created**: 2025-11-11  
**Status**: 📋 Proposal (Ready for Review)  
**Priority**: 🔴 Critical  
**Estimated Effort**: 4 weeks

---

## 🎯 Purpose

DiagnoLeadsのコア機能（システム共通、診断管理、リード管理）の包括的な機能仕様を定義し、現在のナビゲーション・ルーティングの問題を解決します。

## 🔍 Problem Statement

**現状の問題:**
- ✗ 診断作成ページに遷移できない（ルート未定義）
- ✗ リード管理ページのナビゲーションが不完全
- ✗ システム共通機能（ナビゲーション、パンくず等）の仕様が不明確
- ✗ 実装とOpenSpec仕様の乖離

**影響:**
- ユーザーが基本的な機能を使用できない
- 開発チームが実装の指針を持てない
- テストの基準が不明確

## 📦 Deliverables

この変更提案には4つの詳細仕様ドキュメントが含まれます：

### 1. Core Features Proposal
**File**: `core-features-proposal.md` (8.7KB)  
**Purpose**: 全体の変更提案、目標、実装計画

**内容:**
- プロジェクト概要
- 8つのUser Stories
- 成功基準
- 4週間の実装計画
- テスト戦略

### 2. System Core Features
**File**: `system-core.md` (12.7KB)  
**Purpose**: システム共通機能の詳細仕様

**内容:**
- ナビゲーション構造
- ルーティング定義
- レイアウトコンポーネント
- 認証フロー
- パンくずリスト
- テナント切り替え

**主要仕様:**
- レスポンシブサイドバーナビゲーション
- 保護されたルート管理
- パンくずリストの自動生成
- アクセシビリティ対応（WCAG 2.1 AA）

### 3. Assessment Features
**File**: `assessment-features.md` (18.7KB)  
**Purpose**: 診断機能の完全仕様

**内容:**
- 診断CRUD操作
- ビジュアルアセスメントビルダー
- 質問タイプ（単一/複数選択、テキスト、スライダー）
- スコアリングルール
- 公開/非公開ワークフロー
- オートセーブ機能

**主要コンポーネント:**
```
- AssessmentsPage (一覧)
- CreateAssessmentPage (作成)
- EditAssessmentPage (編集)
- AssessmentBuilder (ビルダーUI)
  - QuestionList (ドラッグ&ドロップ)
  - QuestionEditor
  - SettingsPanel
```

### 4. Lead Management Features
**File**: `lead-management-features.md` (27.9KB)  
**Purpose**: リード管理機能の完全仕様

**内容:**
- リード一覧（フィルタリング・検索）
- ホットリード検出（スコア >= 80）
- リード詳細ページ
- ステータス管理ワークフロー
- アクティビティタイムライン
- Microsoft Teams通知連携

**主要機能:**
```
- Lead List with advanced filters
- Hot Lead highlighting (🔥 icon)
- Score breakdown display
- Status workflow (NEW → CONTACTED → QUALIFIED → NEGOTIATION → WON/LOST)
- Teams auto-notification for hot leads
```

---

## 📊 Specifications Summary

| Specification | Lines | Size | User Stories | Components | API Endpoints |
|--------------|-------|------|--------------|------------|---------------|
| Core Proposal | 269 | 8.7KB | 8 | - | - |
| System Core | 516 | 12.7KB | 4 | 6 | 2 |
| Assessment Features | 746 | 18.7KB | 5 | 8 | 7 |
| Lead Management | 895 | 27.9KB | 7 | 12 | 7 |
| **Total** | **2,426** | **68KB** | **24** | **26** | **16** |

---

## 🎯 Success Criteria

### System Core
- [ ] すべてのページにサイドバーナビゲーションからアクセス可能
- [ ] パンくずリストが正しく表示
- [ ] ログイン/ログアウトが正常動作
- [ ] レスポンシブデザイン対応（モバイル/タブレット/デスクトップ）

### Assessment Features
- [ ] 診断一覧ページで診断が表示される
- [ ] 診断作成フォームが動作する
- [ ] ビジュアルビルダーで質問を追加・編集できる
- [ ] ドラッグ&ドロップで質問を並び替えられる
- [ ] 公開/非公開を切り替えられる
- [ ] オートセーブが動作する（3秒おき）

### Lead Management
- [ ] リード一覧でリードが表示される
- [ ] ホットリード（スコア >= 80）がハイライト表示
- [ ] フィルタリング（ステータス、スコア、日付）が動作
- [ ] リード詳細ページでスコア内訳が表示される
- [ ] ステータスを更新できる
- [ ] ホットリード作成時にTeams通知が送信される

---

## 🚀 Implementation Plan

### Phase 1: System Core (Week 1)
**Goal**: 共通レイアウトとナビゲーションの実装

**Tasks:**
- [ ] Layout component with sidebar
- [ ] Navigation component with routing
- [ ] Breadcrumbs component
- [ ] Protected route enhancement
- [ ] Responsive design implementation

**Deliverables:**
- Working navigation across all pages
- Breadcrumbs on all pages
- Mobile-responsive sidebar

### Phase 2: Assessment Features (Week 2-3)
**Goal**: 診断機能の完全実装

**Tasks:**
- [ ] Assessment list page with filters
- [ ] Assessment creation flow
- [ ] Visual assessment builder
  - [ ] Question list (drag & drop)
  - [ ] Question editor
  - [ ] Settings panel
- [ ] Publish/unpublish workflow
- [ ] Auto-save functionality
- [ ] Preview mode

**Deliverables:**
- Functional assessment CRUD
- Working visual builder
- Published assessment URLs

### Phase 3: Lead Management (Week 4)
**Goal**: リード管理機能の完全実装

**Tasks:**
- [ ] Lead list page with filters
- [ ] Lead detail page
  - [ ] Basic info card
  - [ ] Score breakdown
  - [ ] Activity timeline
  - [ ] Notes section
- [ ] Status management workflow
- [ ] Hot lead highlighting
- [ ] Teams notification integration
- [ ] Manual lead creation

**Deliverables:**
- Functional lead management
- Hot lead detection & Teams notifications
- Complete status workflow

---

## 🧪 Testing Strategy

### Unit Tests
**Components:**
- [ ] Sidebar navigation
- [ ] Breadcrumbs generator
- [ ] AssessmentBuilder
- [ ] QuestionEditor
- [ ] LeadTable
- [ ] LeadFilters

**Services:**
- [ ] Auth store
- [ ] Assessment queries
- [ ] Lead queries
- [ ] Teams notification

### Integration Tests
**Flows:**
- [ ] Full navigation flow
- [ ] Assessment creation flow
- [ ] Lead management flow
- [ ] Status update flow

### E2E Tests
**Scenarios:**
- [ ] Login → Create Assessment → Publish
- [ ] Login → View Leads → Filter → Detail
- [ ] Create Hot Lead → Verify Teams Notification

---

## 📈 Performance Targets

| Metric | Target | Notes |
|--------|--------|-------|
| Page Load (Initial) | < 2s | First contentful paint |
| Page Transition | < 500ms | Route navigation |
| Filter Application | < 500ms | Real-time filtering |
| API Response | < 200ms (p95) | Backend response time |
| Auto-save Debounce | 3s | Prevent excessive saves |
| Teams Notification | < 2s | Async, non-blocking |

---

## 🔒 Security & Compliance

### Multi-Tenant Isolation
- すべてのAPIリクエストにtenantIdを含める
- Row-Level Security (RLS)で強制的にテナント分離
- URLに`:tenantId`を含めてスコープを明確化

### Authentication
- JWT-based authentication
- Protected route guards
- Automatic logout on token expiration
- Secure session management

### Data Privacy
- リードの個人情報を暗号化
- GDPR準拠（削除権、忘れられる権利）
- アクティビティログの監査証跡

---

## 📚 Related Documentation

### OpenSpec Guidelines
- [OPENSPEC_BEST_PRACTICES.md](../../../docs/OPENSPEC_BEST_PRACTICES.md)
- [OPENSPEC_QUICK_REFERENCE.md](../../../docs/OPENSPEC_QUICK_REFERENCE.md)
- [OPENSPEC_DROID_STRATEGY.md](../../../docs/OPENSPEC_DROID_STRATEGY.md)

### Existing Specifications
- [Authentication](../../specs/auth/authentication.md)
- [Multi-Tenant](../../specs/auth/multi-tenant.md)
- [Microsoft Teams Integration](../../specs/features/microsoft-teams-integration.md)
- [AI Support](../../specs/features/ai-support.md)

---

## 🎨 Design Assets

### Wireframes
- System Core: Sidebar, Header, Breadcrumbs layout
- Assessment Builder: 3-column layout (Questions, Editor, Settings)
- Lead Detail: Tabbed interface (Overview, Assessment, Activity)

### UI Components (shadcn/ui)
- Button, Card, Badge
- Table, Pagination
- Select, MultiSelect, DateRangePicker
- Dialog, Dropdown, Tooltip

---

## 👥 Review & Approval Process

### Reviewers
- **Product Owner**: Business requirements validation
- **Tech Lead**: Technical feasibility review
- **UX Designer**: UI/UX design review
- **QA Lead**: Test strategy review

### Review Checklist
- [ ] Business requirements clear and complete
- [ ] User stories cover all scenarios
- [ ] Technical design feasible
- [ ] API design consistent with existing patterns
- [ ] UI/UX mockups align with specifications
- [ ] Test strategy comprehensive
- [ ] Performance targets realistic
- [ ] Security considerations addressed

---

## 📝 Next Steps

### Immediate (This Week)
1. **Review**: Product Owner, Tech Lead, UX Designer review specifications
2. **Feedback**: Gather feedback and refine specifications
3. **Approval**: Get formal approval to proceed

### Implementation (Week 1-4)
1. **Week 1**: System Core implementation
2. **Week 2-3**: Assessment Features implementation
3. **Week 4**: Lead Management implementation

### Post-Implementation
1. **Testing**: Complete unit, integration, E2E tests
2. **Documentation**: Update user documentation
3. **Archive**: Move approved specs to `openspec/specs/`

---

## 🔗 Quick Links

- **GitHub Issue**: #TBD
- **Figma Design**: TBD
- **Project Board**: TBD
- **Slack Channel**: #diagnoleads-dev

---

## ✅ Approval

| Role | Name | Date | Status |
|------|------|------|--------|
| Product Owner | TBD | - | ⏳ Pending |
| Tech Lead | TBD | - | ⏳ Pending |
| UX Designer | TBD | - | ⏳ Pending |
| QA Lead | TBD | - | ⏳ Pending |

---

**Status**: 📋 Ready for Review  
**Created by**: Droid (Factory AI Assistant)  
**Date**: 2025-11-11

---

## 📞 Questions?

For questions about these specifications, please:
1. Review the individual spec files for detailed information
2. Check the related OpenSpec documentation
3. Contact the Product Owner or Tech Lead

**Let's build amazing features! 🚀**
