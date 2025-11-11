# Feature Specification: System Core Features

**Version**: 1.0  
**Status**: Proposal  
**Last Updated**: 2025-11-11  
**Related Proposal**: [core-features-proposal.md](./core-features-proposal.md)

---

## Overview

DiagnoLeadsのシステム共通機能を定義します。全ページで共有されるレイアウト、ナビゲーション、ルーティング、認証フローを含みます。

---

## User Stories

### US-CORE-1: サイドバーナビゲーション
**As a** テナントユーザー  
**I want to** サイドバーから各機能に簡単にアクセスできる  
**So that** 効率的にシステムを利用できる

**Acceptance Criteria:**
- [ ] サイドバーにメニュー項目が表示される（ダッシュボード、診断管理、リード管理、分析、設定）
- [ ] 現在のページがハイライト表示される
- [ ] アイコン + ラベルで視覚的に分かりやすい
- [ ] ホバー時にツールチップ表示
- [ ] モバイルではハンバーガーメニュー

### US-CORE-2: パンくずリスト
**As a** ユーザー  
**I want to** 現在のページの階層構造を理解できる  
**So that** 迷わずに上位ページに戻れる

**Acceptance Criteria:**
- [ ] すべてのページにパンくずリスト表示
- [ ] クリック可能なリンク
- [ ] 階層構造を正しく表示（例: ダッシュボード > 診断管理 > 診断編集）

### US-CORE-3: 認証保護
**As a** システム管理者  
**I want to** 未認証ユーザーが保護されたページにアクセスできないようにしたい  
**So that** セキュリティを確保できる

**Acceptance Criteria:**
- [ ] ログインしていない状態で保護されたページにアクセスしようとすると `/login` にリダイレクト
- [ ] ログイン後、元のページにリダイレクト
- [ ] ログイン状態がリフレッシュ後も保持される
- [ ] ログアウト後、すべてのセッション情報がクリアされる

### US-CORE-4: テナント切り替え
**As a** マルチテナント管理者  
**I want to** 管理対象のテナントを切り替えられる  
**So that** 複数のテナントを効率的に管理できる

**Acceptance Criteria:**
- [ ] ヘッダーにテナント切り替えドロップダウン表示
- [ ] テナント切り替え時、URLと表示内容が更新される
- [ ] 切り替えたテナントが次回ログイン時もデフォルトになる

---

## Functional Requirements

### FR-CORE-1: Layout Structure

**レイアウト構造:**
```
┌────────────────────────────────────────────────┐
│  Header (Logo, Tenant Switcher, User Menu)   │
├─────────┬──────────────────────────────────────┤
│         │  Breadcrumbs                         │
│ Sidebar │──────────────────────────────────────│
│         │                                      │
│ - Home  │  Main Content Area                  │
│ - 診断   │                                      │
│ - リード │                                      │
│ - 分析   │                                      │
│ - 設定   │                                      │
│         │                                      │
└─────────┴──────────────────────────────────────┘
```

**Responsive Behavior:**
- **Desktop (>= 1024px)**: Sidebar常時表示
- **Tablet (768px - 1023px)**: Sidebar折りたたみ可能
- **Mobile (< 768px)**: Sidebarはハンバーガーメニュー

### FR-CORE-2: Navigation Items

| アイコン | ラベル | パス | 説明 |
|---------|-------|------|------|
| 🏠 | ダッシュボード | `/dashboard` | 概要ダッシュボード |
| 📋 | 診断管理 | `/tenants/:tenantId/assessments` | 診断の作成・編集 |
| 👥 | リード管理 | `/tenants/:tenantId/leads` | リード一覧・管理 |
| 📊 | 分析 | `/tenants/:tenantId/analytics` | 分析ダッシュボード |
| ⚙️ | 設定 | `/tenants/:tenantId/settings` | テナント設定 |

### FR-CORE-3: Route Protection

**Public Routes (認証不要):**
- `/login`
- `/register`
- `/forgot-password`

**Protected Routes (認証必須):**
- すべての `/tenants/:tenantId/*` パス
- `/dashboard`

**Route Guards:**
```typescript
// Middleware logic
if (!isAuthenticated && isProtectedRoute) {
  redirect(`/login?returnUrl=${currentPath}`);
}

if (isAuthenticated && isPublicRoute) {
  redirect('/dashboard');
}
```

### FR-CORE-4: Breadcrumbs Generation

**動的生成ルール:**
```typescript
// 例: /tenants/abc123/assessments/xyz789/edit
Breadcrumbs: [
  { label: 'ダッシュボード', path: '/dashboard' },
  { label: '診断管理', path: '/tenants/abc123/assessments' },
  { label: '診断名', path: '/tenants/abc123/assessments/xyz789' },
  { label: '編集', path: null }, // 現在ページはリンクなし
]
```

---

## Non-Functional Requirements

### NFR-CORE-1: Performance
- 初回ページロード < 2秒
- ページ遷移 < 500ms
- ナビゲーションクリック応答 < 100ms

### NFR-CORE-2: Accessibility
- WCAG 2.1 AA準拠
- キーボードナビゲーション対応
- スクリーンリーダー対応
- ARIAラベル適用

### NFR-CORE-3: Browser Support
- Chrome (最新2バージョン)
- Firefox (最新2バージョン)
- Safari (最新2バージョン)
- Edge (最新2バージョン)

### NFR-CORE-4: Security
- XSS対策（Reactのデフォルトエスケープ）
- CSRF対策（JWT認証）
- セキュアなセッション管理
- HTTPSのみ許可（本番環境）

---

## API Integration

### Auth Check API
```
GET /api/v1/auth/me
Response: {
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "ユーザー名",
    "role": "tenant_admin",
    "tenant_id": "uuid"
  }
}
```

### Tenant List API (for multi-tenant users)
```
GET /api/v1/users/me/tenants
Response: {
  "tenants": [
    {
      "id": "uuid",
      "name": "テナント名",
      "slug": "tenant-slug"
    }
  ]
}
```

---

## UI/UX Design

### Sidebar Design

**Desktop:**
- Width: 256px
- Background: `bg-gray-900`
- Active item: `bg-blue-600 text-white`
- Hover: `bg-gray-800`

**Mobile:**
- Overlay modal
- Full screen width
- Close button (X) in top-right
- Backdrop click to close

### Header Design
- Height: 64px
- Logo + Tenant Switcher (left)
- User menu (right)
  - User name
  - Dropdown: Profile, Settings, Logout

### Breadcrumbs Design
- Font size: 14px
- Separator: `/`
- Current page: Bold, not clickable
- Previous pages: Clickable links

---

## Component Structure

### Layout Component
```typescript
// frontend/src/components/layout/Layout.tsx
interface LayoutProps {
  children: React.ReactNode;
}

export function Layout({ children }: LayoutProps) {
  return (
    <div className="min-h-screen flex">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <Header />
        <Breadcrumbs />
        <main className="flex-1 p-6">
          {children}
        </main>
      </div>
    </div>
  );
}
```

### Sidebar Component
```typescript
// frontend/src/components/layout/Sidebar.tsx
interface NavigationItem {
  icon: React.ComponentType;
  label: string;
  path: string;
  badge?: number; // Optional notification badge
}

export function Sidebar() {
  const items: NavigationItem[] = [
    { icon: HomeIcon, label: 'ダッシュボード', path: '/dashboard' },
    // ... more items
  ];
  
  return (
    <aside className="w-64 bg-gray-900 text-white">
      {items.map(item => (
        <NavLink key={item.path} to={item.path}>
          <item.icon />
          <span>{item.label}</span>
          {item.badge && <Badge>{item.badge}</Badge>}
        </NavLink>
      ))}
    </aside>
  );
}
```

### Breadcrumbs Component
```typescript
// frontend/src/components/layout/Breadcrumbs.tsx
interface BreadcrumbItem {
  label: string;
  path: string | null;
}

export function Breadcrumbs() {
  const breadcrumbs = useBreadcrumbs(); // Custom hook
  
  return (
    <nav className="flex items-center space-x-2 text-sm">
      {breadcrumbs.map((item, index) => (
        <React.Fragment key={index}>
          {item.path ? (
            <Link to={item.path}>{item.label}</Link>
          ) : (
            <span className="font-bold">{item.label}</span>
          )}
          {index < breadcrumbs.length - 1 && <span>/</span>}
        </React.Fragment>
      ))}
    </nav>
  );
}
```

---

## State Management

### Auth State (Zustand)
```typescript
// frontend/src/store/authStore.ts
interface AuthState {
  user: User | null;
  tenant: Tenant | null;
  isAuthenticated: boolean;
  login: (credentials: Credentials) => Promise<void>;
  logout: () => void;
  switchTenant: (tenantId: string) => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  tenant: null,
  isAuthenticated: false,
  
  login: async (credentials) => {
    const response = await authService.login(credentials);
    set({
      user: response.user,
      tenant: response.user.tenant,
      isAuthenticated: true,
    });
  },
  
  logout: () => {
    authService.logout();
    set({ user: null, tenant: null, isAuthenticated: false });
  },
  
  switchTenant: (tenantId) => {
    // Load tenant data and update state
  },
}));
```

---

## Business Logic

### Authentication Flow

**Login Flow:**
1. User enters credentials
2. POST `/api/v1/auth/login`
3. Receive JWT token
4. Store token in localStorage
5. Fetch user data (GET `/api/v1/auth/me`)
6. Update auth store
7. Redirect to dashboard or returnUrl

**Session Persistence:**
1. On app load, check localStorage for token
2. If token exists, verify with GET `/api/v1/auth/me`
3. If valid, restore auth state
4. If invalid, clear token and redirect to login

**Logout Flow:**
1. User clicks logout
2. Clear token from localStorage
3. Reset auth store
4. Redirect to `/login`

### Tenant Switching Logic
1. User selects tenant from dropdown
2. Update current tenant in store
3. Update URL with new tenantId
4. Refresh data for new tenant

---

## Testing Strategy

### Unit Tests

**Sidebar Component:**
- [ ] Renders all navigation items
- [ ] Highlights current active page
- [ ] Renders badges when provided
- [ ] Handles mobile toggle correctly

**Breadcrumbs Component:**
- [ ] Generates correct breadcrumb trail
- [ ] Renders clickable links for previous pages
- [ ] Renders non-clickable text for current page

**Auth Store:**
- [ ] Login updates state correctly
- [ ] Logout clears state
- [ ] Tenant switching updates state

### Integration Tests

**Protected Route:**
- [ ] Unauthenticated user redirected to login
- [ ] Authenticated user can access protected pages
- [ ] ReturnUrl works correctly

**Navigation Flow:**
- [ ] Click sidebar item navigates to correct page
- [ ] Active page highlighted
- [ ] Breadcrumbs update on navigation

### E2E Tests

**Full Auth Flow:**
1. Visit protected page → Redirected to login
2. Login with valid credentials
3. Redirected to dashboard
4. Navigate via sidebar to assessments
5. Breadcrumbs show correct path
6. Logout
7. Redirected to login

---

## Implementation Notes

### Critical Considerations

**1. Tenant Context:**
- すべてのAPI呼び出しにtenantIdを含める
- URLに`:tenantId`を含めることでテナントスコープを明確化
- テナント切り替え時、すべてのデータをリフレッシュ

**2. Route Protection:**
- `ProtectedRoute` wrapperでJWT検証
- 無効なトークンは自動ログアウト
- API 401エラーも自動ログアウト

**3. Mobile Responsiveness:**
- Sidebarは`useMediaQuery`でデバイス判定
- ハンバーガーメニューはアクセシビリティ対応（ARIA）

**4. Performance Optimization:**
- Layout componentは`React.memo`で最適化
- Sidebarの再レンダリングを最小化
- Code splittingでページ別にバンドル

---

## Related Specifications

- [Authentication](../../specs/auth/authentication.md)
- [Multi-Tenant Architecture](../../specs/auth/multi-tenant.md)
- [Assessment Features](./assessment-features.md)
- [Lead Management Features](./lead-management-features.md)

---

## Changelog

| Date | Version | Changes |
|------|---------|---------|
| 2025-11-11 | 1.0 | Initial specification |

---

**Status**: ✅ Ready for Review  
**Next Steps**: Review → Approve → Implement
