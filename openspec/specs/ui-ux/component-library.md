# Component Library Specification

## Overview

DiagnoLeadsの再利用可能なUIコンポーネントライブラリの仕様。shadcn/uiベースで、デザインシステムに準拠したコンポーネントを定義します。

## Component Architecture

### Design Principles

1. **Composition over Configuration**: 小さく再利用可能なコンポーネントを組み合わせる
2. **Accessibility First**: ARIA属性、キーボードナビゲーション、スクリーンリーダー対応
3. **Type-Safe**: TypeScriptで完全な型安全性を確保
4. **Unstyled Base**: Radix UIなどのヘッドレスUIをベースに独自スタイルを適用
5. **Consistent API**: すべてのコンポーネントで一貫したprops設計

---

## Core Components

### 1. Button

**Purpose**: ユーザーアクションをトリガーするインタラクティブ要素

#### Variants

**Primary (Main Action)**
```tsx
<Button variant="primary" size="md">
  作成する
</Button>
```
- Background: `bg-primary-600`
- Hover: `hover:bg-primary-700`
- Shadow: `shadow-primary`
- Use case: メインCTA、重要なアクション

**Secondary (Supporting Action)**
```tsx
<Button variant="secondary" size="md">
  キャンセル
</Button>
```
- Background: `bg-gray-100`
- Hover: `hover:bg-gray-200`
- Text: `text-gray-900`
- Use case: セカンダリアクション、キャンセル

**Outline (Tertiary Action)**
```tsx
<Button variant="outline" size="md">
  詳細を見る
</Button>
```
- Border: `border border-gray-300`
- Hover: `hover:bg-gray-50`
- Use case: 軽いアクション、リンク的な操作

**Ghost (Minimal Action)**
```tsx
<Button variant="ghost" size="md">
  <IconEdit /> 編集
</Button>
```
- Background: transparent
- Hover: `hover:bg-gray-100`
- Use case: アイコンボタン、ツールバー

**Destructive (Danger Action)**
```tsx
<Button variant="destructive" size="md">
  削除
</Button>
```
- Background: `bg-error-600`
- Hover: `hover:bg-error-700`
- Use case: 削除、危険なアクション

#### Sizes

```tsx
size="xs"   // px-2 py-1 text-xs
size="sm"   // px-3 py-1.5 text-sm
size="md"   // px-4 py-2 text-base (default)
size="lg"   // px-6 py-3 text-lg
size="xl"   // px-8 py-4 text-xl
```

#### States

```tsx
// Loading
<Button loading>送信中...</Button>

// Disabled
<Button disabled>無効</Button>

// With Icon
<Button leftIcon={<IconPlus />}>追加</Button>
<Button rightIcon={<IconArrowRight />}>次へ</Button>

// Icon Only
<Button variant="ghost" size="sm" iconOnly>
  <IconSearch />
</Button>
```

#### TypeScript Interface

```typescript
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'destructive';
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  loading?: boolean;
  disabled?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  iconOnly?: boolean;
  fullWidth?: boolean;
  className?: string;
  children: React.ReactNode;
}
```

---

### 2. Card

**Purpose**: コンテンツをグループ化する視覚的コンテナ

#### Basic Card

```tsx
<Card>
  <CardHeader>
    <CardTitle>診断タイトル</CardTitle>
    <CardDescription>診断の説明文</CardDescription>
  </CardHeader>
  <CardContent>
    <p>カードの本文コンテンツ</p>
  </CardContent>
  <CardFooter>
    <Button variant="primary">アクション</Button>
  </CardFooter>
</Card>
```

#### Variants

**Default (Standard Card)**
```tsx
<Card variant="default">
  {/* Content */}
</Card>
```
- Background: `bg-white`
- Border: `border border-gray-200`
- Shadow: `shadow-sm`
- Hover: `hover:shadow-md transition-shadow`

**Elevated (Floating Card)**
```tsx
<Card variant="elevated">
  {/* Content */}
</Card>
```
- Background: `bg-white`
- Shadow: `shadow-lg`
- Hover: `hover:shadow-xl hover:-translate-y-1 transition-all`
- Use case: 重要なカード、クリッカブルカード

**Outlined (Minimal Card)**
```tsx
<Card variant="outlined">
  {/* Content */}
</Card>
```
- Background: `bg-white`
- Border: `border-2 border-gray-200`
- Shadow: none
- Use case: リスト内のカード

**Filled (Background Card)**
```tsx
<Card variant="filled">
  {/* Content */}
</Card>
```
- Background: `bg-gray-50`
- Border: none
- Use case: サブセクション、情報カード

#### Interactive Card

```tsx
<Card 
  interactive 
  onClick={() => navigate('/details')}
  className="cursor-pointer"
>
  <CardContent>
    クリックして詳細を表示
  </CardContent>
</Card>
```

#### TypeScript Interface

```typescript
interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'elevated' | 'outlined' | 'filled';
  interactive?: boolean;
  className?: string;
  children: React.ReactNode;
}
```

---

### 3. Input

**Purpose**: ユーザーからのテキスト入力を受け取る

#### Basic Input

```tsx
<Input 
  type="text"
  placeholder="メールアドレスを入力"
  value={value}
  onChange={(e) => setValue(e.target.value)}
/>
```

#### With Label & Helper Text

```tsx
<FormField>
  <Label htmlFor="email">メールアドレス</Label>
  <Input 
    id="email"
    type="email"
    placeholder="you@example.com"
  />
  <HelperText>アカウント作成時に使用したメールアドレス</HelperText>
</FormField>
```

#### With Icon

```tsx
<InputGroup>
  <InputLeftAddon>
    <IconSearch className="w-4 h-4 text-gray-500" />
  </InputLeftAddon>
  <Input placeholder="検索..." />
</InputGroup>

<InputGroup>
  <Input type="url" placeholder="https://" />
  <InputRightAddon>
    <IconExternalLink className="w-4 h-4 text-gray-500" />
  </InputRightAddon>
</InputGroup>
```

#### States

**Error State**
```tsx
<FormField>
  <Label htmlFor="email">メールアドレス</Label>
  <Input 
    id="email"
    type="email"
    error
    className="border-error-600"
  />
  <ErrorText>有効なメールアドレスを入力してください</ErrorText>
</FormField>
```

**Disabled State**
```tsx
<Input disabled placeholder="無効な入力フィールド" />
```

**Loading State**
```tsx
<InputGroup>
  <Input placeholder="検索中..." />
  <InputRightAddon>
    <Spinner size="sm" />
  </InputRightAddon>
</InputGroup>
```

#### Sizes

```tsx
size="sm"   // px-3 py-1.5 text-sm
size="md"   // px-4 py-2 text-base (default)
size="lg"   // px-5 py-3 text-lg
```

#### TypeScript Interface

```typescript
interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  size?: 'sm' | 'md' | 'lg';
  error?: boolean;
  leftAddon?: React.ReactNode;
  rightAddon?: React.ReactNode;
  className?: string;
}
```

---

### 4. Badge

**Purpose**: ステータス、カテゴリ、カウントなどを表示する小さなラベル

#### Variants

```tsx
// Default
<Badge variant="default">デフォルト</Badge>

// Primary
<Badge variant="primary">公開中</Badge>

// Success
<Badge variant="success">成功</Badge>

// Warning
<Badge variant="warning">保留中</Badge>

// Error
<Badge variant="error">エラー</Badge>

// Info
<Badge variant="info">情報</Badge>
```

#### Sizes

```tsx
<Badge size="sm">Small</Badge>
<Badge size="md">Medium</Badge>
<Badge size="lg">Large</Badge>
```

#### With Icon

```tsx
<Badge variant="success" leftIcon={<IconCheck />}>
  完了
</Badge>

<Badge variant="error" rightIcon={<IconX />}>
  失敗
</Badge>
```

#### With Dot Indicator

```tsx
<Badge variant="success" dot>
  オンライン
</Badge>
```

#### TypeScript Interface

```typescript
interface BadgeProps {
  variant?: 'default' | 'primary' | 'success' | 'warning' | 'error' | 'info';
  size?: 'sm' | 'md' | 'lg';
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  dot?: boolean;
  className?: string;
  children: React.ReactNode;
}
```

---

### 5. Modal / Dialog

**Purpose**: ユーザーの注意を必要とする重要な情報やアクションを表示

#### Basic Modal

```tsx
<Modal open={isOpen} onClose={() => setIsOpen(false)}>
  <ModalOverlay />
  <ModalContent>
    <ModalHeader>
      <ModalTitle>診断を削除しますか？</ModalTitle>
      <ModalCloseButton />
    </ModalHeader>
    
    <ModalBody>
      <p>この操作は取り消せません。本当に削除しますか？</p>
    </ModalBody>
    
    <ModalFooter>
      <Button variant="outline" onClick={() => setIsOpen(false)}>
        キャンセル
      </Button>
      <Button variant="destructive" onClick={handleDelete}>
        削除する
      </Button>
    </ModalFooter>
  </ModalContent>
</Modal>
```

#### Sizes

```tsx
size="sm"   // max-w-md
size="md"   // max-w-lg (default)
size="lg"   // max-w-2xl
size="xl"   // max-w-4xl
size="full" // max-w-full h-full
```

#### Variants

**Confirmation Dialog**
```tsx
<ConfirmDialog
  open={isOpen}
  onClose={() => setIsOpen(false)}
  onConfirm={handleConfirm}
  title="確認"
  description="この操作を実行しますか？"
  confirmText="実行"
  cancelText="キャンセル"
/>
```

**Alert Dialog**
```tsx
<AlertDialog
  open={isOpen}
  onClose={() => setIsOpen(false)}
  variant="error"
  title="エラー"
  description="予期しないエラーが発生しました。"
  confirmText="OK"
/>
```

#### TypeScript Interface

```typescript
interface ModalProps {
  open: boolean;
  onClose: () => void;
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full';
  closeOnOverlayClick?: boolean;
  closeOnEsc?: boolean;
  className?: string;
  children: React.ReactNode;
}
```

---

### 6. Dropdown Menu

**Purpose**: 複数のアクションやオプションを表示するメニュー

#### Basic Dropdown

```tsx
<DropdownMenu>
  <DropdownMenuTrigger asChild>
    <Button variant="outline">
      アクション <IconChevronDown />
    </Button>
  </DropdownMenuTrigger>
  
  <DropdownMenuContent>
    <DropdownMenuItem onClick={handleEdit}>
      <IconEdit className="mr-2" />
      編集
    </DropdownMenuItem>
    <DropdownMenuItem onClick={handleDuplicate}>
      <IconCopy className="mr-2" />
      複製
    </DropdownMenuItem>
    <DropdownMenuSeparator />
    <DropdownMenuItem 
      onClick={handleDelete}
      className="text-error-600"
    >
      <IconTrash className="mr-2" />
      削除
    </DropdownMenuItem>
  </DropdownMenuContent>
</DropdownMenu>
```

#### With Sections

```tsx
<DropdownMenuContent>
  <DropdownMenuLabel>マイアカウント</DropdownMenuLabel>
  <DropdownMenuItem>プロフィール</DropdownMenuItem>
  <DropdownMenuItem>設定</DropdownMenuItem>
  
  <DropdownMenuSeparator />
  
  <DropdownMenuLabel>組織</DropdownMenuLabel>
  <DropdownMenuItem>チーム</DropdownMenuItem>
  <DropdownMenuItem>招待</DropdownMenuItem>
  
  <DropdownMenuSeparator />
  
  <DropdownMenuItem onClick={handleLogout}>
    ログアウト
  </DropdownMenuItem>
</DropdownMenuContent>
```

---

### 7. Toast Notification

**Purpose**: 一時的なフィードバックメッセージを表示

#### Usage

```tsx
// In component
import { useToast } from '@/hooks/useToast';

const { toast } = useToast();

// Success
toast({
  title: '保存しました',
  description: '診断が正常に保存されました。',
  variant: 'success',
  duration: 3000,
});

// Error
toast({
  title: 'エラー',
  description: '保存に失敗しました。もう一度お試しください。',
  variant: 'error',
  duration: 5000,
});

// Info
toast({
  title: '情報',
  description: '新しいバージョンが利用可能です。',
  variant: 'info',
});

// Warning
toast({
  title: '警告',
  description: 'この操作には時間がかかる場合があります。',
  variant: 'warning',
});
```

#### With Action

```tsx
toast({
  title: '診断を削除しました',
  description: 'この操作を元に戻せます。',
  variant: 'success',
  action: (
    <Button variant="outline" size="sm" onClick={handleUndo}>
      元に戻す
    </Button>
  ),
  duration: 5000,
});
```

---

### 8. Skeleton Loader

**Purpose**: コンテンツ読み込み中のプレースホルダー

#### Basic Usage

```tsx
// Text skeleton
<Skeleton className="h-4 w-full" />
<Skeleton className="h-4 w-3/4 mt-2" />

// Card skeleton
<Card>
  <CardHeader>
    <Skeleton className="h-6 w-1/2" />
    <Skeleton className="h-4 w-full mt-2" />
  </CardHeader>
  <CardContent>
    <Skeleton className="h-40 w-full" />
  </CardContent>
</Card>

// Table skeleton
<Table>
  {[1, 2, 3, 4, 5].map((i) => (
    <TableRow key={i}>
      <TableCell><Skeleton className="h-4 w-32" /></TableCell>
      <TableCell><Skeleton className="h-4 w-48" /></TableCell>
      <TableCell><Skeleton className="h-4 w-24" /></TableCell>
    </TableRow>
  ))}
</Table>
```

---

### 9. Empty State

**Purpose**: データがない状態を表示

#### Basic Empty State

```tsx
<EmptyState
  icon={<IconInbox className="w-16 h-16 text-gray-400" />}
  title="診断がありません"
  description="まだ診断が作成されていません。最初の診断を作成しましょう。"
  action={
    <Button variant="primary" onClick={handleCreate}>
      診断を作成
    </Button>
  }
/>
```

#### With Illustration

```tsx
<EmptyState
  illustration="/images/empty-leads.svg"
  title="リードがまだありません"
  description="診断を公開してリードを獲得しましょう。"
  action={
    <Button variant="primary" onClick={handlePublish}>
      診断を公開
    </Button>
  }
/>
```

---

### 10. Pagination

**Purpose**: 大量のデータをページ分割して表示

#### Basic Pagination

```tsx
<Pagination
  currentPage={page}
  totalPages={totalPages}
  onPageChange={setPage}
  showFirstLast
  showPrevNext
/>
```

#### With Page Size Selector

```tsx
<div className="flex items-center justify-between">
  <Pagination
    currentPage={page}
    totalPages={totalPages}
    onPageChange={setPage}
  />
  
  <Select value={pageSize} onValueChange={setPageSize}>
    <SelectTrigger className="w-32">
      <SelectValue />
    </SelectTrigger>
    <SelectContent>
      <SelectItem value="10">10件</SelectItem>
      <SelectItem value="25">25件</SelectItem>
      <SelectItem value="50">50件</SelectItem>
      <SelectItem value="100">100件</SelectItem>
    </SelectContent>
  </Select>
</div>
```

---

## Component Composition Patterns

### Form with Validation

```tsx
<form onSubmit={handleSubmit(onSubmit)}>
  <FormField>
    <Label htmlFor="title">診断タイトル</Label>
    <Input
      id="title"
      {...register('title', { required: '必須項目です' })}
      error={!!errors.title}
    />
    {errors.title && (
      <ErrorText>{errors.title.message}</ErrorText>
    )}
  </FormField>
  
  <FormField>
    <Label htmlFor="description">説明</Label>
    <Textarea
      id="description"
      {...register('description')}
      rows={4}
    />
  </FormField>
  
  <div className="flex gap-3 justify-end">
    <Button variant="outline" type="button" onClick={onCancel}>
      キャンセル
    </Button>
    <Button variant="primary" type="submit" loading={isSubmitting}>
      保存
    </Button>
  </div>
</form>
```

### Data Table with Actions

```tsx
<Card>
  <CardHeader>
    <div className="flex items-center justify-between">
      <div>
        <CardTitle>リード一覧</CardTitle>
        <CardDescription>
          {totalCount}件のリードが登録されています
        </CardDescription>
      </div>
      <Button variant="primary" onClick={handleCreate}>
        <IconPlus /> 新規作成
      </Button>
    </div>
  </CardHeader>
  
  <CardContent>
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>名前</TableHead>
          <TableHead>メール</TableHead>
          <TableHead>ステータス</TableHead>
          <TableHead>スコア</TableHead>
          <TableHead>アクション</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {leads.map((lead) => (
          <TableRow key={lead.id}>
            <TableCell>{lead.name}</TableCell>
            <TableCell>{lead.email}</TableCell>
            <TableCell>
              <Badge variant={getStatusVariant(lead.status)}>
                {lead.status}
              </Badge>
            </TableCell>
            <TableCell>{lead.score}</TableCell>
            <TableCell>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" size="sm">
                    <IconMoreVertical />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent>
                  <DropdownMenuItem onClick={() => handleView(lead.id)}>
                    詳細
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => handleEdit(lead.id)}>
                    編集
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem 
                    onClick={() => handleDelete(lead.id)}
                    className="text-error-600"
                  >
                    削除
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  </CardContent>
  
  <CardFooter>
    <Pagination
      currentPage={page}
      totalPages={totalPages}
      onPageChange={setPage}
    />
  </CardFooter>
</Card>
```

---

## Implementation Strategy

### Phase 1: Foundation Components (Week 1)
- Button (all variants)
- Card (all variants)
- Input, Textarea, Select
- Label, HelperText, ErrorText

### Phase 2: Feedback Components (Week 2)
- Badge
- Toast Notification
- Skeleton Loader
- Spinner

### Phase 3: Overlay Components (Week 3)
- Modal / Dialog
- Dropdown Menu
- Popover
- Tooltip

### Phase 4: Data Display Components (Week 4)
- Table
- Pagination
- Empty State
- Avatar

### Phase 5: Advanced Components (Week 5+)
- Tabs
- Accordion
- DatePicker
- File Upload

---

## Testing Requirements

Each component must have:

1. **Unit Tests**: Props, variants, states
2. **Accessibility Tests**: ARIA, keyboard navigation
3. **Visual Regression Tests**: Storybook + Chromatic
4. **Integration Tests**: User interactions

---

## Related Specifications

- [Design System](./design-system.md) - Design tokens & guidelines
- [Usability Guidelines](./usability-guidelines.md) - Accessibility standards
- [Interaction Patterns](./interaction-patterns.md) - Animations & transitions

---

## Changelog

- 2025-11-11: Initial component library specification
