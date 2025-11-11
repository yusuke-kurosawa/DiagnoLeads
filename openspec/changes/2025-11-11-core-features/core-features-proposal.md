# Change Proposal: Core Features Specification

**Date**: 2025-11-11  
**Type**: Feature Specification  
**Status**: Proposal  
**Priority**: Critical

---

## Overview

DiagnoLeadsのコア機能（システム共通、診断管理、リード管理）の包括的な機能仕様を定義します。

**背景**: 
- 現在、診断作成・リード管理への画面遷移ができない
- ルーティング、ナビゲーション、UI/UXの詳細仕様が不足
- 実装とOpenSpec仕様の乖離

**目的**:
1. ナビゲーション・ルーティングの完全な仕様化
2. 診断機能（CRUD、ビルダー、公開フロー）の詳細仕様
3. リード管理機能（一覧、詳細、フィルタリング）の詳細仕様

---

## Scope

この変更提案には以下の3つの詳細仕様が含まれます：

1. **System Core Features** (`system-core.md`)
   - ナビゲーション
   - ルーティング
   - レイアウト
   - 認証フロー

2. **Assessment Features** (`assessment-features.md`)
   - 診断一覧
   - 診断作成・編集
   - 診断ビルダー
   - 公開・非公開管理

3. **Lead Management Features** (`lead-management-features.md`)
   - リード一覧
   - リード詳細
   - フィルタリング・検索
   - ステータス管理

---

## Goals

### Business Goals
- ユーザーが診断を作成・管理できるようにする
- ユーザーがリードを効率的に管理できるようにする
- 直感的なナビゲーションでユーザー体験を向上

### Technical Goals
- 完全なルーティング定義
- コンポーネント構造の明確化
- 状態管理の標準化
- API連携の明確化

### Quality Goals
- すべての画面に遷移可能
- ページロード時間 < 1秒
- レスポンシブ対応（モバイル・タブレット・デスクトップ）

---

## User Stories

### システム共通機能

**US-1: ナビゲーション**
- ユーザーとして、サイドバーから各機能に簡単にアクセスしたい
- ユーザーとして、現在どのページにいるか視覚的に分かりたい
- ユーザーとして、パンくずリストで階層構造を理解したい

**US-2: 認証フロー**
- ユーザーとして、ログインしていない状態で保護されたページにアクセスしようとしたらログインページにリダイレクトされたい
- ユーザーとして、ログイン状態が保持されていてほしい
- ユーザーとして、ログアウトしたら安全にセッションが終了してほしい

### 診断機能

**US-3: 診断一覧**
- テナント管理者として、自分のテナントの診断一覧を見たい
- テナント管理者として、診断のステータス（公開/非公開、下書き）を一目で確認したい
- テナント管理者として、診断を検索・フィルタリングしたい

**US-4: 診断作成**
- テナント管理者として、新しい診断を作成したい
- テナント管理者として、診断の基本情報（タイトル、説明）を入力したい
- テナント管理者として、質問と回答選択肢を追加したい

**US-5: 診断編集**
- テナント管理者として、既存の診断を編集したい
- テナント管理者として、編集中の変更を保存/破棄できるようにしたい
- テナント管理者として、下書き保存機能がほしい

### リード管理機能

**US-6: リード一覧**
- 営業担当者として、獲得したリードの一覧を見たい
- 営業担当者として、ホットリード（スコアが高い）を優先的に確認したい
- 営業担当者として、リードをステータスでフィルタリングしたい

**US-7: リード詳細**
- 営業担当者として、リードの詳細情報を確認したい
- 営業担当者として、リードがどの診断を完了したか知りたい
- 営業担当者として、リードのスコア内訳を理解したい

**US-8: リードアクション**
- 営業担当者として、リードのステータスを更新したい
- 営業担当者として、リードにメモを追加したい
- 営業担当者として、リードを担当者にアサインしたい

---

## Success Criteria

### Acceptance Criteria

**システム共通機能:**
- [ ] サイドバーナビゲーションからすべてのメインページにアクセス可能
- [ ] ログイン/ログアウトが正常に動作
- [ ] パンくずリストが正しく表示
- [ ] レスポンシブデザイン対応

**診断機能:**
- [ ] 診断一覧ページで診断が表示される
- [ ] 「新規作成」ボタンから診断作成ページに遷移できる
- [ ] 診断作成フォームが動作する
- [ ] 診断を保存できる
- [ ] 保存した診断が一覧に表示される

**リード管理機能:**
- [ ] リード一覧ページでリードが表示される
- [ ] リードをクリックして詳細ページに遷移できる
- [ ] フィルタリング（ステータス、スコア）が動作する
- [ ] リードステータスを更新できる

### Performance Criteria
- ページ遷移時間 < 500ms
- 初回ロード時間 < 2秒
- APIレスポンス時間 < 200ms (p95)

---

## Technical Design

### Routing Structure

```typescript
// frontend/src/App.tsx
<Routes>
  {/* Public */}
  <Route path="/login" element={<Login />} />
  <Route path="/register" element={<Register />} />
  
  {/* Protected - Dashboard */}
  <Route path="/dashboard" element={<Dashboard />} />
  
  {/* Protected - Assessments */}
  <Route path="/tenants/:tenantId/assessments" element={<AssessmentsPage />} />
  <Route path="/tenants/:tenantId/assessments/create" element={<CreateAssessmentPage />} />
  <Route path="/tenants/:tenantId/assessments/:assessmentId" element={<AssessmentDetailPage />} />
  <Route path="/tenants/:tenantId/assessments/:assessmentId/edit" element={<EditAssessmentPage />} />
  
  {/* Protected - Leads */}
  <Route path="/tenants/:tenantId/leads" element={<LeadsPage />} />
  <Route path="/tenants/:tenantId/leads/create" element={<CreateLeadPage />} />
  <Route path="/tenants/:tenantId/leads/:leadId" element={<LeadDetailPage />} />
  <Route path="/tenants/:tenantId/leads/:leadId/edit" element={<EditLeadPage />} />
  
  {/* Protected - Analytics */}
  <Route path="/tenants/:tenantId/analytics" element={<AnalyticsPage />} />
  
  {/* Protected - Settings */}
  <Route path="/tenants/:tenantId/settings" element={<SettingsPage />} />
</Routes>
```

### Navigation Component

```typescript
// Sidebar Navigation
const navigationItems = [
  { icon: HomeIcon, label: 'ダッシュボード', path: '/dashboard' },
  { icon: FileTextIcon, label: '診断管理', path: '/tenants/:tenantId/assessments' },
  { icon: UsersIcon, label: 'リード管理', path: '/tenants/:tenantId/leads' },
  { icon: BarChartIcon, label: '分析', path: '/tenants/:tenantId/analytics' },
  { icon: SettingsIcon, label: '設定', path: '/tenants/:tenantId/settings' },
];
```

---

## Implementation Plan

### Phase 1: System Core (Week 1)
1. Layout component with sidebar navigation
2. Routing structure完全化
3. Breadcrumbs component
4. Protected route enhancement

### Phase 2: Assessment Features (Week 2-3)
1. Assessment list page enhancement
2. Assessment creation flow
3. Assessment builder UI
4. Publish/unpublish flow

### Phase 3: Lead Management Features (Week 4)
1. Lead list page enhancement
2. Lead detail page
3. Filtering and search
4. Status management UI

---

## Testing Strategy

### Unit Tests
- Navigation component rendering
- Route protection logic
- Form validation

### Integration Tests
- Full navigation flow
- Assessment creation flow
- Lead management flow

### E2E Tests
- Login → Navigate to Assessments → Create → Save
- Login → Navigate to Leads → View details → Update status

---

## Related Specs

This proposal will generate:
- [System Core Features](../../specs/features/system-core.md)
- [Assessment Features](../../specs/features/assessment-features.md)
- [Lead Management Features](../../specs/features/lead-management-features.md)

Existing related specs:
- [Authentication](../../specs/auth/authentication.md)
- [Multi-Tenant](../../specs/auth/multi-tenant.md)
- [Assessment CRUD](../../specs/features/assessment-crud.md)

---

## Next Steps

1. ✅ Create this proposal
2. ⏳ Create 3 detailed feature specs
3. ⏳ Review and approve
4. ⏳ Implement based on specs
5. ⏳ Test and verify
6. ⏳ Archive after completion

---

**Author**: Droid  
**Reviewers**: Product Owner, Tech Lead  
**Estimated Effort**: 4 weeks  
**Dependencies**: None (standalone features)
