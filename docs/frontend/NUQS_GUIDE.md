# nuqs（ナックス）導入ガイド

## 概要

**nuqs**は、ReactでURL検索パラメータ（クエリストリング）を型安全に扱えるライブラリです。`useState`のような感覚でURLパラメータを状態管理できます。

### 公式サイト
- https://nuqs.dev/

### メリット

1. **URL共有可能**: フィルター状態をURLに保存できるため、URLをコピーするだけで他のユーザーと同じ状態を共有できる
2. **ブラウザ履歴対応**: 戻る/進むボタンでフィルター履歴をナビゲート可能
3. **状態の永続化**: ページリロード後も状態が保持される
4. **型安全**: TypeScriptで型安全にパラメータを管理
5. **使いやすさ**: `useState`と同じAPIで直感的に使える

## インストール

### 1. パッケージのインストール

```bash
cd frontend
npm install nuqs
```

### 2. React Router v7アダプターのセットアップ

`frontend/src/App.tsx`で`NuqsAdapter`をセットアップします：

```tsx
import { BrowserRouter as Router } from 'react-router-dom';
import { NuqsAdapter } from 'nuqs/adapters/react-router/v7';

function App() {
  return (
    <Router>
      <NuqsAdapter>
        {/* アプリケーションのコンテンツ */}
      </NuqsAdapter>
    </Router>
  );
}
```

**重要**: `NuqsAdapter`は`Router`の内側に配置してください。

## 基本的な使い方

### 1. 単一パラメータの管理（useQueryState）

```tsx
import { useQueryState, parseAsString, parseAsInteger } from 'nuqs';

function MyComponent() {
  // 文字列パラメータ
  const [search, setSearch] = useQueryState(
    'search',
    parseAsString.withDefault('')
  );

  // 数値パラメータ
  const [page, setPage] = useQueryState(
    'page',
    parseAsInteger.withDefault(1)
  );

  return (
    <div>
      <input
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        placeholder="検索..."
      />
      <button onClick={() => setPage(page + 1)}>次のページ</button>
    </div>
  );
}
```

### 2. 複数パラメータの同時管理（useQueryStates）

```tsx
import { useQueryStates, parseAsString, parseAsInteger, parseAsBoolean } from 'nuqs';

function FilterComponent() {
  const [filters, setFilters] = useQueryStates({
    search: parseAsString.withDefault(''),
    page: parseAsInteger.withDefault(1),
    status: parseAsString.withDefault('all'),
    showArchived: parseAsBoolean.withDefault(false),
  });

  // 個別更新
  const handleSearch = (value: string) => {
    setFilters({ search: value, page: 1 }); // 検索時はページを1にリセット
  };

  // 一括リセット
  const handleReset = () => {
    setFilters({
      search: '',
      page: 1,
      status: 'all',
      showArchived: false,
    });
  };

  return (
    <div>
      <input
        value={filters.search}
        onChange={(e) => handleSearch(e.target.value)}
      />
      <select
        value={filters.status}
        onChange={(e) => setFilters({ status: e.target.value })}
      >
        <option value="all">すべて</option>
        <option value="active">アクティブ</option>
      </select>
    </div>
  );
}
```

## 組み込みパーサー

nuqsは様々な型のパーサーを提供しています：

| パーサー | 型 | 説明 | 使用例 |
|---------|-----|------|--------|
| `parseAsString` | `string \| null` | 文字列 | 検索クエリ、名前 |
| `parseAsInteger` | `number \| null` | 整数 | ページ番号、ID |
| `parseAsFloat` | `number \| null` | 浮動小数点数 | 価格、評価 |
| `parseAsBoolean` | `boolean \| null` | ブール値 | トグル、フラグ |
| `parseAsTimestamp` | `number \| null` | Unixタイムスタンプ | 日時 |
| `parseAsIsoDateTime` | `Date \| null` | ISO8601日時 | 日時 |
| `parseAsArrayOf(parser)` | `T[] \| null` | 配列 | タグ、複数選択 |
| `parseAsJson<T>()` | `T \| null` | JSON | 複雑なオブジェクト |
| `parseAsStringEnum<T>(values)` | `T \| null` | 列挙型 | ステータス |
| `parseAsStringLiteral(values)` | リテラル型 | リテラル列挙型 | - |
| `parseAsNumberLiteral(values)` | 数値リテラル | 数値リテラル列挙型 | - |

### 使用例

```tsx
import {
  useQueryStates,
  parseAsString,
  parseAsInteger,
  parseAsBoolean,
  parseAsArrayOf,
  parseAsStringEnum,
} from 'nuqs';

function AdvancedFilters() {
  const [filters, setFilters] = useQueryStates({
    // 文字列
    search: parseAsString.withDefault(''),

    // 整数
    page: parseAsInteger.withDefault(1),
    limit: parseAsInteger.withDefault(20),

    // ブール値
    showArchived: parseAsBoolean.withDefault(false),

    // 配列（複数選択タグ）
    tags: parseAsArrayOf(parseAsString).withDefault([]),

    // 列挙型
    status: parseAsStringEnum<'all' | 'active' | 'inactive'>(['all', 'active', 'inactive']).withDefault('all'),

    // スコア範囲
    minScore: parseAsInteger.withDefault(0),
    maxScore: parseAsInteger.withDefault(100),
  });

  return (
    <div>
      {/* フィルターUI */}
    </div>
  );
}
```

## 実装例

### 例1: 検索とページネーション

```tsx
import { useQueryStates, parseAsString, parseAsInteger } from 'nuqs';

function SearchablePage() {
  const [params, setParams] = useQueryStates({
    q: parseAsString.withDefault(''),
    page: parseAsInteger.withDefault(1),
  });

  const handleSearch = (query: string) => {
    setParams({ q: query, page: 1 }); // 検索時はページを1にリセット
  };

  const handlePageChange = (newPage: number) => {
    setParams({ page: newPage });
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div>
      <input
        value={params.q}
        onChange={(e) => handleSearch(e.target.value)}
        placeholder="検索..."
      />
      <Pagination page={params.page} onPageChange={handlePageChange} />
    </div>
  );
}
```

### 例2: リードフィルター（実際のユースケース）

実装例は以下のファイルを参照してください：

- **基本的なデモ**: `frontend/src/pages/examples/NuqsExamplePage.tsx`
- **実際のユースケース**: `frontend/src/components/leads/LeadListWithNuqs.example.tsx`

デモページは以下のURLでアクセスできます：
```
http://localhost:5173/examples/nuqs
```

## ベストプラクティス

### 1. デフォルト値を常に設定する

```tsx
// ✅ 良い例
const [page, setPage] = useQueryState(
  'page',
  parseAsInteger.withDefault(1)
);

// ❌ 悪い例（nullableになる）
const [page, setPage] = useQueryState('page', parseAsInteger);
```

### 2. 検索時はページを1にリセット

```tsx
const handleSearch = (value: string) => {
  setFilters({ search: value, page: 1 }); // ページをリセット
};
```

### 3. 複数パラメータは`useQueryStates`でまとめる

```tsx
// ✅ 良い例 - 1つのhookで管理
const [filters, setFilters] = useQueryStates({
  search: parseAsString.withDefault(''),
  page: parseAsInteger.withDefault(1),
  status: parseAsString.withDefault('all'),
});

// ❌ 悪い例 - 個別に管理
const [search, setSearch] = useQueryState('search', parseAsString.withDefault(''));
const [page, setPage] = useQueryState('page', parseAsInteger.withDefault(1));
const [status, setStatus] = useQueryState('status', parseAsString.withDefault('all'));
```

### 4. URL共有機能を提供する

```tsx
const handleShareFilters = () => {
  const url = window.location.href;
  navigator.clipboard.writeText(url);
  alert('フィルター設定付きURLをコピーしました！');
};
```

### 5. リセット機能を提供する

```tsx
const handleResetFilters = () => {
  setFilters({
    search: '',
    page: 1,
    status: 'all',
    tags: [],
  });
};
```

## トラブルシューティング

### 1. パラメータがURLに反映されない

**原因**: `NuqsAdapter`がセットアップされていない

**解決策**: `App.tsx`で`NuqsAdapter`を`Router`の内側に配置してください。

```tsx
<Router>
  <NuqsAdapter>
    {/* コンテンツ */}
  </NuqsAdapter>
</Router>
```

### 2. 型エラーが発生する

**原因**: パーサーの型が合っていない

**解決策**: 正しいパーサーを使用してください。

```tsx
// ❌ 数値に文字列パーサーを使用
const [page, setPage] = useQueryState('page', parseAsString);

// ✅ 数値には整数パーサーを使用
const [page, setPage] = useQueryState('page', parseAsInteger);
```

### 3. ブラウザの戻るボタンが動作しない

**原因**: オプションで`history: 'replace'`を設定している

**解決策**: デフォルトの`history: 'push'`を使用してください（または明示的に設定）。

```tsx
const [search, setSearch] = useQueryState(
  'search',
  parseAsString.withDefault('').withOptions({ history: 'push' })
);
```

## 既存コードへの統合

### LeadListコンポーネントへの統合例

現在のLeadListコンポーネント（`frontend/src/components/leads/LeadList.tsx`）は`useState`を使用しています：

```tsx
// 現在の実装
const [searchQuery, setSearchQuery] = useState('');
const [filters, setFilters] = useState<LeadFilterState>({});
```

これをnuqsに置き換えるには：

```tsx
// nuqsを使用した実装
import { useQueryStates, parseAsString, parseAsInteger, parseAsBoolean, parseAsArrayOf } from 'nuqs';

const [filters, setFilters] = useQueryStates({
  search: parseAsString.withDefault(''),
  page: parseAsInteger.withDefault(1),
  status: parseAsArrayOf(parseAsString).withDefault([]),
  score_min: parseAsInteger.withDefault(0),
  score_max: parseAsInteger.withDefault(100),
  is_hot: parseAsBoolean.withDefault(false),
});
```

詳細は`LeadListWithNuqs.example.tsx`を参照してください。

## 参考資料

- **公式サイト**: https://nuqs.dev/
- **GitHub**: https://github.com/47ng/nuqs
- **公式ドキュメント**: https://nuqs.dev/docs
- **Built-in Parsers**: https://nuqs.dev/docs/parsers/built-in

## まとめ

nuqsを使用することで：

✅ URL検索パラメータを型安全に管理
✅ フィルター状態をURLで共有可能
✅ ブラウザ履歴対応
✅ 直感的なAPI（`useState`と同じ）
✅ ページリロード後も状態が保持

フィルタリング、ページネーション、検索機能を持つすべてのページでnuqsの使用を推奨します。
