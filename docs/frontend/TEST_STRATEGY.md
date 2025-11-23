# テスト戦略ガイド

## 概要

DiagnoLeadsでは、全フロントエンドプロジェクト（`frontend/` と `marketing/`）で統一されたテスト戦略を採用しています。

## 統一テスト戦略

```json
{
  "ユニット・統合テスト": "Vitest + Testing Library",
  "E2Eテスト": "Playwright",
  "ビジュアルリグレッション": "Playwright + Percy（オプション）"
}
```

### なぜこの構成か？

| 項目 | 理由 |
|-----|------|
| **Vitest** | ⚡ 超高速（Jest比5-10倍）、ViteエコシステムとシームレスAPI、Next.jsでも使用可能 |
| **Testing Library** | ユーザー視点のテスト、フレームワーク非依存、ベストプラクティス推奨 |
| **Playwright** | 🚀 高速・安定、マルチブラウザ対応、並列実行ネイティブサポート |
| **Percy** | 🎨 ビジュアル差分検出、レスポンシブ対応、CI/CD統合 |

---

## プロジェクト別テスト構成

### 1. frontend/（React Router - 管理画面）

#### ディレクトリ構成

```
frontend/
├── vitest.config.ts          # Vitest設定
├── playwright.config.ts      # Playwright設定
├── src/
│   ├── components/
│   │   └── Button.test.tsx   # コンポーネントテスト
│   ├── hooks/
│   │   └── useAuth.test.ts   # カスタムフックテスト
│   ├── utils/
│   │   └── format.test.ts    # ユーティリティテスト
│   └── stores/
│       └── authStore.test.ts # 状態管理テスト
└── test/
    ├── setup.ts              # テスト共通設定
    └── e2e/
        ├── auth.spec.ts      # 認証フロー
        ├── leads.spec.ts     # リード管理
        └── dashboard.spec.ts # ダッシュボード
```

#### Vitest設定

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './test/setup.ts',
    css: true,
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'test/',
        '**/*.test.{ts,tsx}',
        '**/*.spec.{ts,tsx}',
      ]
    }
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  }
})
```

#### テストセットアップ

```typescript
// test/setup.ts
import '@testing-library/jest-dom'
import { cleanup } from '@testing-library/react'
import { afterEach, vi } from 'vitest'

// 各テスト後にクリーンアップ
afterEach(() => {
  cleanup()
})

// グローバルモック
global.ResizeObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}))

// matchMediaのモック
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
})
```

---

### 2. marketing/（Next.js - マーケティング・公開ページ）

#### ディレクトリ構成

```
marketing/
├── vitest.config.ts          # Vitest設定
├── playwright.config.ts      # Playwright設定
├── app/
│   ├── components/
│   │   └── Hero.test.tsx     # コンポーネントテスト
│   ├── assessments/
│   │   └── [slug]/page.test.tsx  # ページコンポーネントテスト
│   └── actions/
│       └── createLead.test.ts    # Server Actionsテスト
└── test/
    ├── setup.ts
    └── e2e/
        ├── public-assessment.spec.ts  # 公開診断
        ├── embed-widget.spec.ts       # 埋め込みウィジェット
        └── seo.spec.ts                # SEO検証
```

#### Vitest設定（Next.js用）

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './test/setup.ts',
    css: true,
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'test/',
        '.next/',
        '**/*.test.{ts,tsx}',
        '**/*.spec.{ts,tsx}',
      ]
    }
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './app')
    }
  }
})
```

---

## ユニット・統合テスト（Vitest + Testing Library）

### 1. コンポーネントテスト

#### シンプルなコンポーネント

```typescript
// src/components/Button.test.tsx
import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { Button } from './Button'

describe('Button', () => {
  it('renders button with text', () => {
    render(<Button>クリック</Button>)
    expect(screen.getByRole('button', { name: 'クリック' })).toBeInTheDocument()
  })

  it('calls onClick when clicked', () => {
    const handleClick = vi.fn()
    render(<Button onClick={handleClick}>クリック</Button>)

    fireEvent.click(screen.getByRole('button'))
    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  it('disables button when disabled prop is true', () => {
    render(<Button disabled>クリック</Button>)
    expect(screen.getByRole('button')).toBeDisabled()
  })
})
```

#### 非同期コンポーネント

```typescript
// src/components/LeadList.test.tsx
import { render, screen, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { describe, it, expect, vi } from 'vitest'
import { LeadList } from './LeadList'
import * as leadService from '@/services/leadService'

// leadServiceをモック
vi.mock('@/services/leadService')

describe('LeadList', () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false }
    }
  })

  const wrapper = ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  )

  it('displays leads when data is loaded', async () => {
    // モックデータ
    vi.mocked(leadService.list).mockResolvedValue([
      { id: '1', name: 'John Doe', email: 'john@example.com', score: 85 }
    ])

    render(<LeadList tenantId="tenant-123" />, { wrapper })

    // ローディング状態
    expect(screen.getByText(/loading/i)).toBeInTheDocument()

    // データ表示待機
    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument()
    })

    expect(screen.getByText('john@example.com')).toBeInTheDocument()
  })

  it('displays error message when fetch fails', async () => {
    vi.mocked(leadService.list).mockRejectedValue(new Error('Network error'))

    render(<LeadList tenantId="tenant-123" />, { wrapper })

    await waitFor(() => {
      expect(screen.getByText(/error/i)).toBeInTheDocument()
    })
  })
})
```

### 2. カスタムフックテスト

```typescript
// src/hooks/useAuth.test.ts
import { renderHook, waitFor } from '@testing-library/react'
import { describe, it, expect, beforeEach } from 'vitest'
import { useAuth } from './useAuth'
import { useAuthStore } from '@/stores/authStore'

describe('useAuth', () => {
  beforeEach(() => {
    // ストアをリセット
    useAuthStore.setState({ user: null, isAuthenticated: false })
  })

  it('returns authenticated state', () => {
    useAuthStore.setState({
      user: { id: '1', email: 'test@example.com' },
      isAuthenticated: true
    })

    const { result } = renderHook(() => useAuth())

    expect(result.current.isAuthenticated).toBe(true)
    expect(result.current.user?.email).toBe('test@example.com')
  })

  it('handles login', async () => {
    const { result } = renderHook(() => useAuth())

    await result.current.login('test@example.com', 'password')

    await waitFor(() => {
      expect(result.current.isAuthenticated).toBe(true)
    })
  })
})
```

### 3. 状態管理テスト（Zustand）

```typescript
// src/stores/authStore.test.ts
import { describe, it, expect, beforeEach } from 'vitest'
import { useAuthStore } from './authStore'

describe('authStore', () => {
  beforeEach(() => {
    useAuthStore.setState({ user: null, isAuthenticated: false })
  })

  it('sets user on login', () => {
    const user = { id: '1', email: 'test@example.com', tenant_id: 'tenant-1' }

    useAuthStore.getState().setUser(user)

    expect(useAuthStore.getState().user).toEqual(user)
    expect(useAuthStore.getState().isAuthenticated).toBe(true)
  })

  it('clears user on logout', () => {
    useAuthStore.setState({
      user: { id: '1', email: 'test@example.com', tenant_id: 'tenant-1' },
      isAuthenticated: true
    })

    useAuthStore.getState().logout()

    expect(useAuthStore.getState().user).toBeNull()
    expect(useAuthStore.getState().isAuthenticated).toBe(false)
  })
})
```

### 4. ユーティリティ関数テスト

```typescript
// src/utils/format.test.ts
import { describe, it, expect } from 'vitest'
import { formatCurrency, formatDate, formatScore } from './format'

describe('format utilities', () => {
  describe('formatCurrency', () => {
    it('formats JPY currency', () => {
      expect(formatCurrency(1000)).toBe('¥1,000')
      expect(formatCurrency(1234567)).toBe('¥1,234,567')
    })
  })

  describe('formatDate', () => {
    it('formats date in Japanese locale', () => {
      const date = new Date('2024-01-15T10:30:00Z')
      expect(formatDate(date)).toBe('2024年1月15日')
    })
  })

  describe('formatScore', () => {
    it('formats score with percentage', () => {
      expect(formatScore(85)).toBe('85%')
      expect(formatScore(100)).toBe('100%')
    })

    it('handles edge cases', () => {
      expect(formatScore(0)).toBe('0%')
      expect(formatScore(null)).toBe('N/A')
    })
  })
})
```

---

## E2Eテスト（Playwright）

### Playwright設定

```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './test/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',

  use: {
    baseURL: 'http://localhost:5173',  // frontend/
    // baseURL: 'http://localhost:3000',  // marketing/
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    // モバイル
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] },
    },
  ],

  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:5173',
    reuseExistingServer: !process.env.CI,
  },
})
```

### E2Eテスト例

#### 1. 認証フロー

```typescript
// test/e2e/auth.spec.ts
import { test, expect } from '@playwright/test'

test.describe('Authentication', () => {
  test('user can login successfully', async ({ page }) => {
    await page.goto('/login')

    // フォーム入力
    await page.fill('input[name="email"]', 'test@example.com')
    await page.fill('input[name="password"]', 'password123')
    await page.click('button[type="submit"]')

    // ダッシュボードにリダイレクト
    await expect(page).toHaveURL(/\/dashboard/)
    await expect(page.locator('h1')).toContainText('ダッシュボード')
  })

  test('shows error for invalid credentials', async ({ page }) => {
    await page.goto('/login')

    await page.fill('input[name="email"]', 'wrong@example.com')
    await page.fill('input[name="password"]', 'wrongpassword')
    await page.click('button[type="submit"]')

    // エラーメッセージ表示
    await expect(page.locator('[role="alert"]')).toContainText('ログインに失敗')
  })

  test('user can logout', async ({ page }) => {
    // ログイン済みの状態でテスト開始
    await page.goto('/dashboard')

    // ヘッダーのメニューを開く
    await page.click('[aria-label="User menu"]')
    await page.click('text=ログアウト')

    // ログインページにリダイレクト
    await expect(page).toHaveURL('/login')
  })
})
```

#### 2. リード管理フロー

```typescript
// test/e2e/leads.spec.ts
import { test, expect } from '@playwright/test'

test.describe('Lead Management', () => {
  test.beforeEach(async ({ page }) => {
    // 各テスト前にログイン
    await page.goto('/login')
    await page.fill('input[name="email"]', 'test@example.com')
    await page.fill('input[name="password"]', 'password123')
    await page.click('button[type="submit"]')
    await page.waitForURL(/\/dashboard/)
  })

  test('displays lead list', async ({ page }) => {
    await page.goto('/tenants/tenant-123/leads')

    // リストが表示される
    await expect(page.locator('h2')).toContainText('リード管理')
    await expect(page.locator('table tbody tr')).toHaveCount.greaterThan(0)
  })

  test('can create new lead', async ({ page }) => {
    await page.goto('/tenants/tenant-123/leads')
    await page.click('text=新規リード')

    // フォーム入力
    await page.fill('input[name="name"]', '山田太郎')
    await page.fill('input[name="email"]', 'yamada@example.com')
    await page.fill('input[name="company"]', '株式会社テスト')
    await page.selectOption('select[name="status"]', 'qualified')

    await page.click('button[type="submit"]')

    // リスト画面に戻る
    await expect(page).toHaveURL(/\/tenants\/.*\/leads$/)
    await expect(page.locator('table')).toContainText('山田太郎')
  })

  test('can filter leads by status', async ({ page }) => {
    await page.goto('/tenants/tenant-123/leads')

    // フィルターを適用
    await page.check('input[value="qualified"]')

    // URLパラメータが更新される（nuqs）
    await expect(page).toHaveURL(/status=qualified/)

    // フィルター結果が表示される
    const rows = page.locator('table tbody tr')
    await expect(rows).toHaveCount.greaterThan(0)
  })

  test('can search leads', async ({ page }) => {
    await page.goto('/tenants/tenant-123/leads')

    // 検索
    await page.fill('input[placeholder*="検索"]', '山田')

    // URLパラメータが更新される
    await expect(page).toHaveURL(/search=山田/)

    // 検索結果が表示される
    await expect(page.locator('table')).toContainText('山田')
  })
})
```

#### 3. 公開診断ページ（Next.js）

```typescript
// marketing/test/e2e/public-assessment.spec.ts
import { test, expect } from '@playwright/test'

test.describe('Public Assessment Page', () => {
  test('displays assessment with SEO metadata', async ({ page }) => {
    await page.goto('/assessments/business-health-check')

    // ページタイトル
    await expect(page).toHaveTitle(/ビジネス健康診断/)

    // OGPメタタグ
    const ogTitle = await page.locator('meta[property="og:title"]').getAttribute('content')
    expect(ogTitle).toContain('ビジネス健康診断')

    // 構造化データ
    const ldJson = await page.locator('script[type="application/ld+json"]').textContent()
    expect(ldJson).toContain('Quiz')
  })

  test('user can complete assessment', async ({ page }) => {
    await page.goto('/assessments/business-health-check')

    // 診断開始
    await page.click('text=診断を開始')

    // 質問に回答
    for (let i = 1; i <= 5; i++) {
      await page.click(`input[name="question-${i}"]`)
      await page.click('text=次へ')
    }

    // リード情報入力
    await page.fill('input[name="name"]', 'テストユーザー')
    await page.fill('input[name="email"]', 'test@example.com')
    await page.click('button[type="submit"]')

    // 結果ページ表示
    await expect(page.locator('h1')).toContainText('診断結果')
    await expect(page.locator('[data-testid="score"]')).toBeVisible()
  })

  test('works on mobile devices', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 })
    await page.goto('/assessments/business-health-check')

    // モバイルレイアウトの確認
    await expect(page.locator('h1')).toBeVisible()
    await page.click('text=診断を開始')
    await expect(page.locator('form')).toBeVisible()
  })
})
```

---

## ビジュアルリグレッションテスト（Playwright + Percy）

### Percy設定

```typescript
// percy.config.yml
version: 2
snapshot:
  widths:
    - 375   # Mobile
    - 768   # Tablet
    - 1280  # Desktop
  min-height: 1024
  percy-css: |
    /* 動的コンテンツを非表示 */
    [data-percy-hide] {
      display: none !important;
    }
```

### ビジュアルテスト例

```typescript
// test/e2e/visual.spec.ts
import { test } from '@playwright/test'
import percySnapshot from '@percy/playwright'

test.describe('Visual Regression', () => {
  test('dashboard page', async ({ page }) => {
    await page.goto('/dashboard')
    await percySnapshot(page, 'Dashboard')
  })

  test('lead list page', async ({ page }) => {
    await page.goto('/tenants/tenant-123/leads')
    await percySnapshot(page, 'Lead List')
  })

  test('public assessment page', async ({ page }) => {
    await page.goto('/assessments/business-health-check')
    await percySnapshot(page, 'Public Assessment - Landing')

    await page.click('text=診断を開始')
    await percySnapshot(page, 'Public Assessment - Question')
  })

  test('responsive design', async ({ page }) => {
    // モバイル
    await page.setViewportSize({ width: 375, height: 667 })
    await page.goto('/dashboard')
    await percySnapshot(page, 'Dashboard - Mobile')

    // タブレット
    await page.setViewportSize({ width: 768, height: 1024 })
    await percySnapshot(page, 'Dashboard - Tablet')

    // デスクトップ
    await page.setViewportSize({ width: 1280, height: 800 })
    await percySnapshot(page, 'Dashboard - Desktop')
  })
})
```

---

## テスト実行コマンド

### frontend/（React Router）

```bash
# ユニット・統合テスト
npm test                    # Vitest（watch mode）
npm run test:coverage       # カバレッジ付き
npm run test:ui             # UIモード

# E2Eテスト
npm run test:e2e            # Playwright
npm run test:e2e:headed     # ヘッドあり（ブラウザ表示）
npm run test:e2e:debug      # デバッグモード
```

### marketing/（Next.js）

```bash
# ユニット・統合テスト
npm test                    # Vitest（watch mode）
npm run test:coverage       # カバレッジ付き

# E2Eテスト
npm run test:e2e            # Playwright
npm run test:e2e:visual     # ビジュアルリグレッション（Percy）
```

---

## CI/CD統合

### GitHub Actions

```yaml
# .github/workflows/test.yml
name: Test

on: [push, pull_request]

jobs:
  unit-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '20'

      - name: Install dependencies
        run: npm ci

      - name: Run unit tests
        run: npm run test:coverage

      - name: Upload coverage
        uses: codecov/codecov-action@v3

  e2e-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3

      - name: Install dependencies
        run: npm ci

      - name: Install Playwright
        run: npx playwright install --with-deps

      - name: Run E2E tests
        run: npm run test:e2e

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report
          path: playwright-report/

  visual-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3

      - name: Run visual regression tests
        run: npm run test:e2e:visual
        env:
          PERCY_TOKEN: ${{ secrets.PERCY_TOKEN }}
```

---

## ベストプラクティス

### 1. テストの命名規則

```typescript
// ❌ 悪い例
test('test1', () => { ... })
test('it works', () => { ... })

// ✅ 良い例
test('displays error message when login fails', () => { ... })
test('filters leads by status when checkbox is selected', () => { ... })
```

### 2. Arrange-Act-Assert パターン

```typescript
test('creates new lead', async () => {
  // Arrange - テストデータの準備
  const leadData = { name: 'Test Lead', email: 'test@example.com' }

  // Act - アクション実行
  const result = await createLead(leadData)

  // Assert - 結果検証
  expect(result.name).toBe('Test Lead')
  expect(result.email).toBe('test@example.com')
})
```

### 3. テストの独立性

```typescript
// ❌ 悪い例 - テストが相互依存
let sharedData: any

test('test 1', () => {
  sharedData = { id: 1 }
})

test('test 2', () => {
  expect(sharedData.id).toBe(1)  // test 1に依存
})

// ✅ 良い例 - 各テストが独立
test('test 1', () => {
  const data = { id: 1 }
  expect(data.id).toBe(1)
})

test('test 2', () => {
  const data = { id: 2 }
  expect(data.id).toBe(2)
})
```

### 4. モックの適切な使用

```typescript
// ✅ 外部APIはモック
vi.mock('@/services/api', () => ({
  fetchLeads: vi.fn().mockResolvedValue([...mockLeads])
}))

// ✅ ユーティリティ関数は実際のコードを使用
import { formatDate } from '@/utils/format'  // モックしない
```

---

## まとめ

DiagnoLeadsのテスト戦略は：

- ✅ **統一されたツールチェーン**（Vitest + Playwright）
- ✅ **高速な開発サイクル**
- ✅ **信頼性の高いテスト**
- ✅ **継続的な品質保証**

この戦略により、高品質なコードを維持しながら、迅速な開発が可能になります。
