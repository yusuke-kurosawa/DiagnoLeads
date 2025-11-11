# Usability Guidelines Specification

## Overview

DiagnoLeadsのユーザビリティガイドライン。アクセシビリティ、レスポンシブデザイン、ユーザビリティベストプラクティスを定義し、すべてのユーザーにとって使いやすいプロダクトを実現します。

---

## Accessibility (a11y) Standards

### WCAG 2.1 AA Compliance

DiagnoLeadsはWCAG 2.1 AAレベルに準拠します。

#### 1. Perceivable (知覚可能)

**Color Contrast**
- テキストと背景のコントラスト比: 最低4.5:1
- 大きなテキスト(18pt+): 最低3:1
- ツール: [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)

```tsx
// ❌ Bad: Insufficient contrast
<p className="text-gray-400 bg-gray-100">読みにくいテキスト</p>

// ✅ Good: Sufficient contrast
<p className="text-gray-700 bg-white">読みやすいテキスト</p>
```

**Alternative Text**
- すべての画像に`alt`属性を提供
- 装飾的な画像には空の`alt=""`を使用

```tsx
// ✅ Good
<img src="/logo.png" alt="DiagnoLeads ロゴ" />
<img src="/decorative.png" alt="" role="presentation" />
```

**Text Alternatives for Non-Text Content**
- アイコンのみのボタンには`aria-label`を追加

```tsx
// ✅ Good
<Button variant="ghost" aria-label="設定を開く">
  <IconSettings />
</Button>
```

#### 2. Operable (操作可能)

**Keyboard Navigation**
- すべてのインタラクティブ要素にキーボードアクセス可能
- Tab順序が論理的
- フォーカスインジケーターを視覚的に明示

```tsx
// ✅ Good: Visible focus
<Button className="focus:ring-2 focus:ring-primary-600 focus:outline-none">
  クリック
</Button>
```

**Keyboard Shortcuts**
| Shortcut | Action |
|----------|--------|
| Tab | 次の要素にフォーカス |
| Shift + Tab | 前の要素にフォーカス |
| Enter / Space | ボタン・リンクをアクティブ化 |
| Esc | モーダル・ドロップダウンを閉じる |
| Arrow Keys | リスト・メニュー内を移動 |

**Skip Links**
- ページ上部にスキップリンクを提供

```tsx
<a 
  href="#main-content" 
  className="sr-only focus:not-sr-only focus:absolute focus:top-0 focus:left-0 focus:z-50 focus:p-4 focus:bg-white focus:text-primary-600"
>
  メインコンテンツへスキップ
</a>
```

#### 3. Understandable (理解可能)

**Clear Labels**
- フォームフィールドには明確なラベルを提供
- プレースホルダーのみに依存しない

```tsx
// ✅ Good
<FormField>
  <Label htmlFor="email">メールアドレス</Label>
  <Input 
    id="email" 
    type="email" 
    placeholder="you@example.com"
    aria-describedby="email-help"
  />
  <HelperText id="email-help">
    アカウント作成時に使用したメールアドレス
  </HelperText>
</FormField>
```

**Error Identification**
- エラーは明確に識別される
- エラーメッセージは具体的

```tsx
// ✅ Good
<FormField>
  <Label htmlFor="password">パスワード</Label>
  <Input 
    id="password" 
    type="password"
    error={!!errors.password}
    aria-invalid={!!errors.password}
    aria-describedby="password-error"
  />
  {errors.password && (
    <ErrorText id="password-error" role="alert">
      パスワードは8文字以上で、数字と記号を含む必要があります
    </ErrorText>
  )}
</FormField>
```

**Predictable Navigation**
- ナビゲーションは一貫した位置と順序
- リンクとボタンの動作は予測可能

#### 4. Robust (堅牢)

**Semantic HTML**
- 適切なHTML要素を使用

```tsx
// ❌ Bad: Div soup
<div onClick={handleClick}>クリック</div>

// ✅ Good: Semantic button
<button onClick={handleClick}>クリック</button>
```

**ARIA Attributes**
- 必要に応じてARIA属性を使用
- ネイティブHTMLで可能な場合はARIAを避ける

```tsx
// ✅ Good: ARIA for complex components
<div 
  role="dialog" 
  aria-modal="true"
  aria-labelledby="dialog-title"
  aria-describedby="dialog-description"
>
  <h2 id="dialog-title">確認</h2>
  <p id="dialog-description">この操作を実行しますか？</p>
</div>
```

---

## Responsive Design

### Breakpoint Strategy

**Mobile First Approach**
- 最小のビューポートから設計
- 段階的にエンハンスメント

```tsx
// ✅ Good: Mobile first
<div className="
  w-full          // Mobile: Full width
  md:w-1/2        // Tablet: Half width
  lg:w-1/3        // Desktop: Third width
">
  Content
</div>
```

### Responsive Patterns

**Navigation**
```tsx
// Mobile: Hamburger menu
// Desktop: Horizontal nav

<header>
  {/* Mobile */}
  <div className="lg:hidden">
    <Button variant="ghost" onClick={() => setMenuOpen(true)}>
      <IconMenu />
    </Button>
    <MobileMenu open={menuOpen} onClose={() => setMenuOpen(false)} />
  </div>
  
  {/* Desktop */}
  <nav className="hidden lg:flex gap-6">
    <NavLink to="/assessments">診断</NavLink>
    <NavLink to="/leads">リード</NavLink>
    <NavLink to="/analytics">分析</NavLink>
  </nav>
</header>
```

**Tables**
```tsx
// Mobile: Card layout
// Desktop: Table layout

<div className="lg:hidden">
  {data.map(item => (
    <Card key={item.id}>
      <CardHeader>
        <CardTitle>{item.name}</CardTitle>
      </CardHeader>
      <CardContent>
        <dl>
          <dt>メール</dt>
          <dd>{item.email}</dd>
          <dt>ステータス</dt>
          <dd><Badge>{item.status}</Badge></dd>
        </dl>
      </CardContent>
    </Card>
  ))}
</div>

<div className="hidden lg:block">
  <Table>
    {/* Standard table */}
  </Table>
</div>
```

**Typography Scale**
```tsx
// Responsive heading sizes
<h1 className="text-3xl md:text-4xl lg:text-5xl font-bold">
  ページタイトル
</h1>
```

### Touch Targets

**Minimum Size: 44x44px**
```css
/* Ensure touch targets are large enough */
button, a, input[type="checkbox"] {
  min-width: 44px;
  min-height: 44px;
}
```

**Spacing Between Targets**
- 最低8px以上の間隔

```tsx
<div className="flex gap-2">
  <Button>ボタン1</Button>
  <Button>ボタン2</Button>
</div>
```

---

## Form Design Best Practices

### Input Validation

**Real-time vs On Submit**
- リアルタイム: フォーマット検証（メール、電話番号）
- Submit時: 複雑な検証（重複チェック、API検証）

```tsx
// ✅ Good: Progressive validation
const { register, formState: { errors } } = useForm({
  mode: 'onBlur', // Validate on blur
});

<Input
  {...register('email', {
    required: '必須項目です',
    pattern: {
      value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
      message: '有効なメールアドレスを入力してください',
    },
  })}
  error={!!errors.email}
/>
```

### Error Messages

**Do's ✅**
- 具体的で行動可能
- ユーザーのミスを責めない
- 解決策を提示

```tsx
// ✅ Good
"パスワードは8文字以上で、数字と記号を含む必要があります"

// ❌ Bad
"無効な入力"
```

### Form Layout

**Vertical Stacking (Recommended)**
```tsx
<form className="space-y-6">
  <FormField>
    <Label>名前</Label>
    <Input />
  </FormField>
  
  <FormField>
    <Label>メール</Label>
    <Input />
  </FormField>
  
  <Button type="submit">送信</Button>
</form>
```

**Required Fields**
```tsx
// Visual indicator
<Label htmlFor="name">
  名前 <span className="text-error-600">*</span>
</Label>

// Screen reader
<Label htmlFor="name">
  名前 <span className="sr-only">(必須)</span>
</Label>
```

---

## Loading States

### Skeleton Loaders

**When to Use**
- 初回データ読み込み時
- コンテンツの形状が予測可能な場合

```tsx
{isLoading ? (
  <Card>
    <CardHeader>
      <Skeleton className="h-6 w-1/2" />
      <Skeleton className="h-4 w-full mt-2" />
    </CardHeader>
    <CardContent>
      <Skeleton className="h-40 w-full" />
    </CardContent>
  </Card>
) : (
  <Card>
    {/* Actual content */}
  </Card>
)}
```

### Spinners

**When to Use**
- ボタンアクション時
- 短時間の読み込み（<2秒）

```tsx
<Button loading={isSubmitting} disabled={isSubmitting}>
  {isSubmitting ? '保存中...' : '保存'}
</Button>
```

### Progress Indicators

**When to Use**
- 長時間処理（>5秒）
- ファイルアップロード

```tsx
<ProgressBar value={uploadProgress} max={100} />
<p className="text-sm text-gray-600">
  {uploadProgress}% 完了
</p>
```

---

## Empty States

### Guidelines

**Elements**
1. Icon / Illustration
2. Heading
3. Description
4. Primary Action (optional)

```tsx
<EmptyState
  icon={<IconInbox className="w-16 h-16 text-gray-400" />}
  title="診断がありません"
  description="まだ診断が作成されていません。最初の診断を作成して、リード獲得を開始しましょう。"
  action={
    <Button variant="primary" onClick={handleCreate}>
      診断を作成
    </Button>
  }
/>
```

### Types

**No Data Yet**
- 新規ユーザー、初期状態
- ポジティブなトーン
- CTAを明確に

**No Results Found**
- 検索・フィルタ結果が空
- 検索条件をクリアするアクション

```tsx
<EmptyState
  icon={<IconSearch />}
  title="検索結果が見つかりません"
  description='"{searchQuery}" に一致する診断が見つかりませんでした。'
  action={
    <Button variant="outline" onClick={handleClearSearch}>
      検索条件をクリア
    </Button>
  }
/>
```

**Error State**
- エラーが発生した場合
- リトライアクションを提供

```tsx
<EmptyState
  icon={<IconAlertTriangle className="text-error-600" />}
  title="データの読み込みに失敗しました"
  description="一時的なエラーが発生しました。もう一度お試しください。"
  action={
    <Button variant="primary" onClick={handleRetry}>
      再試行
    </Button>
  }
/>
```

---

## Error Handling

### Error Hierarchy

1. **Field-level Errors**: フォーム入力の検証エラー
2. **Form-level Errors**: フォーム全体のエラー（API エラー）
3. **Page-level Errors**: ページ読み込みエラー
4. **Application-level Errors**: 予期しないエラー

### User-Friendly Error Messages

**API Errors**
```tsx
// Transform backend errors to user-friendly messages
const getErrorMessage = (error: ApiError) => {
  switch (error.code) {
    case 'VALIDATION_ERROR':
      return '入力内容に誤りがあります。ご確認ください。';
    case 'UNAUTHORIZED':
      return 'セッションが期限切れです。再度ログインしてください。';
    case 'FORBIDDEN':
      return 'この操作を実行する権限がありません。';
    case 'NOT_FOUND':
      return '指定されたリソースが見つかりませんでした。';
    case 'RATE_LIMIT_EXCEEDED':
      return 'リクエストが多すぎます。しばらくしてから再試行してください。';
    default:
      return '予期しないエラーが発生しました。しばらくしてから再試行してください。';
  }
};
```

### Error Boundaries

```tsx
// Global error boundary
<ErrorBoundary
  fallback={
    <EmptyState
      icon={<IconAlertTriangle className="text-error-600" />}
      title="予期しないエラーが発生しました"
      description="ページを再読み込みしてください。問題が解決しない場合はサポートにお問い合わせください。"
      action={
        <Button variant="primary" onClick={() => window.location.reload()}>
          ページを再読み込み
        </Button>
      }
    />
  }
>
  <App />
</ErrorBoundary>
```

---

## Confirmation Dialogs

### When to Use

**Use for**:
- 破壊的なアクション（削除）
- 不可逆的な操作（公開）
- 重要な変更（ステータス変更）

**Don't use for**:
- 通常の保存操作
- キャンセル可能な操作
- 頻繁に行う操作

### Design Pattern

```tsx
<ConfirmDialog
  open={isOpen}
  onClose={() => setIsOpen(false)}
  onConfirm={handleDelete}
  variant="destructive" // or 'default'
  title="診断を削除しますか？"
  description="この操作は取り消せません。診断に関連するすべてのデータが削除されます。"
  confirmText="削除する"
  cancelText="キャンセル"
  confirmButtonVariant="destructive"
/>
```

---

## Search & Filtering

### Search Input

**Debounced Search**
```tsx
const [searchQuery, setSearchQuery] = useState('');
const debouncedSearch = useDebounce(searchQuery, 300);

useEffect(() => {
  if (debouncedSearch) {
    fetchResults(debouncedSearch);
  }
}, [debouncedSearch]);

<InputGroup>
  <InputLeftAddon>
    <IconSearch className="w-4 h-4 text-gray-500" />
  </InputLeftAddon>
  <Input
    placeholder="診断を検索..."
    value={searchQuery}
    onChange={(e) => setSearchQuery(e.target.value)}
  />
  {searchQuery && (
    <InputRightAddon>
      <Button
        variant="ghost"
        size="sm"
        onClick={() => setSearchQuery('')}
      >
        <IconX className="w-4 h-4" />
      </Button>
    </InputRightAddon>
  )}
</InputGroup>
```

### Filters

**Filter Pattern**
```tsx
<div className="flex gap-4 items-center">
  <Select value={statusFilter} onValueChange={setStatusFilter}>
    <SelectTrigger className="w-40">
      <SelectValue placeholder="ステータス" />
    </SelectTrigger>
    <SelectContent>
      <SelectItem value="all">すべて</SelectItem>
      <SelectItem value="published">公開中</SelectItem>
      <SelectItem value="draft">下書き</SelectItem>
    </SelectContent>
  </Select>
  
  <DateRangePicker
    value={dateRange}
    onChange={setDateRange}
  />
  
  <Button
    variant="outline"
    size="sm"
    onClick={handleClearFilters}
  >
    フィルタをクリア
  </Button>
</div>
```

---

## Performance Guidelines

### Code Splitting

```tsx
// Route-based code splitting
const DashboardPage = lazy(() => import('./pages/Dashboard'));
const AssessmentsPage = lazy(() => import('./pages/Assessments'));

<Suspense fallback={<PageLoader />}>
  <Routes>
    <Route path="/dashboard" element={<DashboardPage />} />
    <Route path="/assessments" element={<AssessmentsPage />} />
  </Routes>
</Suspense>
```

### Image Optimization

```tsx
// ✅ Good: Responsive images with lazy loading
<img
  src="/images/hero.jpg"
  srcSet="/images/hero-640.jpg 640w, /images/hero-1280.jpg 1280w"
  sizes="(max-width: 640px) 640px, 1280px"
  alt="Hero image"
  loading="lazy"
/>
```

### Memoization

```tsx
// Expensive calculations
const processedData = useMemo(() => {
  return data.map(item => expensiveTransform(item));
}, [data]);

// Callbacks
const handleClick = useCallback(() => {
  // Handler logic
}, [dependencies]);
```

---

## Internationalization (i18n) Readiness

### Text Direction Support

```tsx
// Prepare for RTL languages
<div className="flex gap-4" dir="ltr">
  {/* Content */}
</div>
```

### Number & Date Formatting

```tsx
// Use Intl APIs
const formattedDate = new Intl.DateTimeFormat('ja-JP', {
  year: 'numeric',
  month: 'long',
  day: 'numeric',
}).format(date);

const formattedNumber = new Intl.NumberFormat('ja-JP', {
  style: 'decimal',
}).format(1234567);
```

---

## Testing Checklist

### Manual Testing

- [ ] キーボードのみで全機能にアクセス可能
- [ ] スクリーンリーダー (NVDA/JAWS) でナビゲーション可能
- [ ] 200%ズームでコンテンツが読める
- [ ] モバイル実機でタッチ操作可能
- [ ] 低速ネットワークでも使用可能

### Automated Testing

- [ ] Lighthouse Accessibility スコア 90+
- [ ] axe DevTools でエラーなし
- [ ] WAVE で警告なし
- [ ] Contrast Checker でコントラスト比チェック

---

## Related Specifications

- [Design System](./design-system.md) - Design tokens
- [Component Library](./component-library.md) - UI components
- [Interaction Patterns](./interaction-patterns.md) - Animations

---

## Changelog

- 2025-11-11: Initial usability guidelines specification
