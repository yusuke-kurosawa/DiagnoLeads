# ユーザーガイド機能 開発者ガイド

## 概要

DiagnoLeadsのユーザーガイド機能は、ユーザーが各機能の使い方を簡単に理解できるよう設計された包括的なヘルプシステムです。

## 主要コンポーネント

### 1. HelpDialog
モーダル形式でヘルプコンテンツを表示するコンポーネント。

**場所**: `frontend/src/components/help/HelpDialog.tsx`

**使用例**:
```tsx
import { HelpDialog } from '@/components/help/HelpDialog';

<HelpDialog
  open={isOpen}
  onClose={handleClose}
  title="診断管理の使い方"
  description="診断の作成、編集、公開を管理します。"
  steps={[
    {
      title: '診断一覧を確認',
      description: '作成した診断の一覧が表示されます。',
      image: '/images/help/assessments-list.png' // オプション
    }
  ]}
  sections={[
    {
      title: 'AI診断生成機能',
      content: 'トピックと業界を入力するだけで...'
    }
  ]}
  relatedLinks={[
    {
      title: '詳細ドキュメント',
      url: 'https://docs.example.com/assessments'
    }
  ]}
/>
```

### 2. Tooltip
UIエレメントにホバー時のヘルプを表示するコンポーネント。

**場所**: `frontend/src/components/ui/tooltip.tsx`

**使用例**:
```tsx
import { Tooltip } from '@/components/ui/tooltip';

<Tooltip content="このボタンをクリックして診断を作成" position="bottom">
  <button>診断を作成</button>
</Tooltip>
```

**プロパティ**:
- `content`: string | ReactNode - 表示するコンテンツ
- `position`: 'top' | 'bottom' | 'left' | 'right' - 表示位置（デフォルト: 'top'）
- `delay`: number - 表示までの遅延（ms、デフォルト: 300）
- `disabled`: boolean - 無効化フラグ

### 3. HelpCenterPage
全機能のガイドとFAQを一覧表示するページ。

**場所**: `frontend/src/pages/help/HelpCenterPage.tsx`

**アクセス**: `/help`

## 新しいヘルプコンテンツの追加

### ステップ1: ヘルプコンテンツの作成

`frontend/src/data/helpContent.ts` に新しいページのヘルプを追加：

```typescript
export const helpContent: HelpContentMap = {
  // 既存のコンテンツ...

  'new-feature': {
    title: '新機能の使い方',
    description: '新機能の概要説明',
    steps: [
      {
        title: 'ステップ1',
        description: 'ステップの説明',
      },
      // 追加のステップ...
    ],
    sections: [
      {
        title: 'セクションタイトル',
        content: 'セクションの内容',
      },
    ],
    relatedLinks: [
      {
        title: '関連ドキュメント',
        url: 'https://example.com/docs',
      },
    ],
  },
};
```

### ステップ2: 型定義の更新

`frontend/src/types/help.ts` のPageKey型に新しいキーを追加：

```typescript
export type PageKey =
  | 'dashboard'
  | 'assessments'
  // ... 既存のキー
  | 'new-feature';  // 新しいキーを追加
```

### ステップ3: ページキーマッピングの更新

`frontend/src/utils/helpUtils.ts` の`getPageKeyFromPath`関数に新しいパスを追加：

```typescript
export function getPageKeyFromPath(pathname: string): PageKey {
  // 既存のマッピング...

  if (pathname.includes('/new-feature')) return 'new-feature';

  // デフォルト
  return 'dashboard';
}
```

### ステップ4: ヘルプセンターのカテゴリー追加（オプション）

`frontend/src/data/helpCategories.ts` に新しいカテゴリー項目を追加：

```typescript
export const helpCategories: HelpCategory[] = [
  {
    title: '新機能',
    icon: <NewIcon className="w-5 h-5" />,
    items: [
      {
        key: 'new-feature',
        title: '新機能',
        description: '新機能の説明',
      },
    ],
  },
  // 既存のカテゴリー...
];
```

## アーキテクチャ

```
ヘルプシステム
├── Presentation Layer
│   ├── HelpDialog.tsx          # モーダル表示
│   ├── HelpStepItem.tsx        # ステップ表示
│   ├── HelpSection.tsx         # セクション表示
│   ├── RelatedLinks.tsx        # リンク表示
│   ├── HelpCenterPage.tsx      # 一覧ページ
│   └── Tooltip.tsx             # インラインヘルプ
├── Business Logic Layer
│   ├── useHelpSearch.ts        # 検索・フィルタリング
│   └── helpUtils.ts            # ユーティリティ関数
├── Data Layer
│   ├── helpContent.ts          # ヘルプコンテンツ
│   └── helpCategories.ts       # カテゴリー・FAQ
├── State Management
│   └── helpStore.ts            # Zustand状態管理
└── Types
    └── help.ts                  # 型定義
```

## ベストプラクティス

### 1. ヘルプコンテンツの書き方

**DO**:
- ✅ ユーザーの視点で書く（「あなたは〜できます」）
- ✅ 具体的なステップを提供する
- ✅ スクリーンショットを含める（可能な場合）
- ✅ 簡潔で明確な言葉を使う

**DON'T**:
- ❌ 技術用語を多用しない
- ❌ 長すぎる説明を書かない
- ❌ 前提知識を必要とする説明をしない

### 2. ステップの構成

```typescript
// 良い例
steps: [
  {
    title: 'ダッシュボードを開く',
    description: 'サイドバーの「ダッシュボード」をクリックします。',
  },
  {
    title: 'データを確認',
    description: '主要な指標が表示されます。スコアが80以上のリードに注目しましょう。',
  },
]

// 悪い例
steps: [
  {
    title: 'システムにアクセス',
    description: 'ブラウザでURLを入力してログインし、認証後にメインダッシュボード画面に遷移してデータベースから取得した統計情報を確認します。',
  },
]
```

### 3. アクセシビリティ

- すべてのコンポーネントにARIA属性を追加
- キーボードナビゲーションをサポート
- スクリーンリーダー対応のテキストを提供

```tsx
// 良い例
<button aria-label="ヘルプを表示">
  <HelpCircle aria-hidden="true" />
</button>

// 悪い例
<button>
  <HelpCircle />
</button>
```

## テスト

### ユニットテスト

新しいヘルプコンテンツを追加した場合、対応するテストも追加してください：

```typescript
// frontend/src/utils/__tests__/helpUtils.test.ts
describe('getPageKeyFromPath', () => {
  it('should return "new-feature" for new feature path', () => {
    expect(getPageKeyFromPath('/new-feature')).toBe('new-feature');
  });
});
```

### テストの実行

```bash
cd frontend

# すべてのテストを実行
npm test

# カバレッジ付きで実行
npm run test:coverage

# 特定のテストファイルを実行
npm test -- helpUtils.test.ts
```

## トラブルシューティング

### Q: ヘルプボタンをクリックしても何も表示されない

**A**: 以下を確認してください：
1. `helpContent.ts` に該当ページのキーが存在するか
2. `getPageKeyFromPath` が正しいキーを返すか
3. `helpStore` が正しく初期化されているか

### Q: Tooltipが正しい位置に表示されない

**A**: 以下を確認してください：
1. 親要素が `position: relative` または `position: absolute` になっていないか
2. z-indexの競合がないか
3. ビューポートの境界を超えていないか（自動調整されるはず）

### Q: 新しいヘルプコンテンツが表示されない

**A**: 以下を確認してください：
1. TypeScriptの型エラーがないか（`npm run type-check`）
2. ブラウザのキャッシュをクリアしたか
3. 開発サーバーを再起動したか

## パフォーマンス最適化

### メモ化

ヘルプシステムは`useMemo`と`useCallback`を使用して最適化されています：

```typescript
// useHelpSearch.ts
const filteredCategories = useMemo(() => {
  // 重い計算処理
}, [categories, searchQuery]);

// Header.tsx
const handleHelpClick = useCallback(() => {
  // ハンドラー
}, [location.pathname, openHelp]);
```

### 画像の遅延読み込み

ヘルプコンテンツに画像を含める場合は、必ず`loading="lazy"`を使用してください：

```tsx
<img
  src={step.image}
  alt={step.title}
  loading="lazy"
  className="mt-3 rounded border border-gray-200 w-full"
/>
```

## 関連ファイル

- **型定義**: `frontend/src/types/help.ts`
- **コンテンツ**: `frontend/src/data/helpContent.ts`
- **カテゴリー**: `frontend/src/data/helpCategories.ts`
- **ユーティリティ**: `frontend/src/utils/helpUtils.ts`
- **Hooks**: `frontend/src/hooks/useHelpSearch.ts`
- **状態管理**: `frontend/src/store/helpStore.ts`
- **テスト**: `frontend/src/**/__tests__/`

## 参考リソース

- [WCAG 2.1 Accessibility Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [React Testing Library](https://testing-library.com/docs/react-testing-library/intro/)
- [Zustand Documentation](https://docs.pmnd.rs/zustand/getting-started/introduction)
