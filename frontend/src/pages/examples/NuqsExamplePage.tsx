import { useQueryState, useQueryStates, parseAsString, parseAsInteger, parseAsBoolean, parseAsArrayOf, parseAsStringEnum } from 'nuqs';

/**
 * nuqs使用例ページ
 *
 * このページは、nuqsライブラリの使い方を示すサンプルです。
 * URL検索パラメータを型安全に扱う様々なパターンを実装しています。
 */
export function NuqsExamplePage() {
  // 1. 基本的な文字列パラメータ
  const [search, setSearch] = useQueryState(
    'search',
    parseAsString.withDefault('')
  );

  // 2. 数値パラメータ（ページネーション）
  const [page, setPage] = useQueryState(
    'page',
    parseAsInteger.withDefault(1)
  );

  // 3. ブール値パラメータ（フィルター表示/非表示）
  const [showFilters, setShowFilters] = useQueryState(
    'showFilters',
    parseAsBoolean.withDefault(false)
  );

  // 4. 列挙型（enum）パラメータ
  const [status, setStatus] = useQueryState(
    'status',
    parseAsStringEnum<'all' | 'qualified' | 'nurturing' | 'converted'>(['all', 'qualified', 'nurturing', 'converted']).withDefault('all')
  );

  // 5. 配列パラメータ（複数選択タグ）
  const [tags, setTags] = useQueryState(
    'tags',
    parseAsArrayOf(parseAsString).withDefault([])
  );

  // 6. 複数のパラメータを同時に管理
  const [filters, setFilters] = useQueryStates({
    category: parseAsString.withDefault(''),
    minScore: parseAsInteger.withDefault(0),
    maxScore: parseAsInteger.withDefault(100),
  });

  // 検索ハンドラー
  const handleSearchChange = (value: string) => {
    setSearch(value);
    // 検索時はページを1にリセット
    setPage(1);
  };

  // ページ変更ハンドラー
  const handlePageChange = (newPage: number) => {
    setPage(newPage);
  };

  // タグ追加ハンドラー
  const handleAddTag = (tag: string) => {
    if (tag && !tags.includes(tag)) {
      setTags([...tags, tag]);
    }
  };

  // タグ削除ハンドラー
  const handleRemoveTag = (tagToRemove: string) => {
    setTags(tags.filter(tag => tag !== tagToRemove));
  };

  // フィルターリセット
  const handleResetFilters = () => {
    setSearch('');
    setPage(1);
    setShowFilters(false);
    setStatus('all');
    setTags([]);
    setFilters({
      category: '',
      minScore: 0,
      maxScore: 100,
    });
  };

  return (
    <div className="container mx-auto p-6 max-w-4xl">
      <h1 className="text-3xl font-bold mb-6">nuqs 使用例</h1>

      {/* 検索バー */}
      <section className="mb-8 p-6 bg-white rounded-lg shadow">
        <h2 className="text-xl font-semibold mb-4">1. 文字列パラメータ（検索）</h2>
        <input
          type="text"
          value={search}
          onChange={(e) => handleSearchChange(e.target.value)}
          placeholder="検索..."
          className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <p className="mt-2 text-sm text-gray-600">
          現在のURL: <code className="bg-gray-100 px-2 py-1 rounded">?search={search}</code>
        </p>
      </section>

      {/* ページネーション */}
      <section className="mb-8 p-6 bg-white rounded-lg shadow">
        <h2 className="text-xl font-semibold mb-4">2. 数値パラメータ（ページネーション）</h2>
        <div className="flex items-center gap-4">
          <button
            onClick={() => handlePageChange(Math.max(1, page - 1))}
            disabled={page === 1}
            className="px-4 py-2 bg-blue-500 text-white rounded disabled:bg-gray-300 disabled:cursor-not-allowed hover:bg-blue-600 transition"
          >
            前へ
          </button>
          <span className="font-semibold">ページ {page}</span>
          <button
            onClick={() => handlePageChange(page + 1)}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition"
          >
            次へ
          </button>
        </div>
        <p className="mt-2 text-sm text-gray-600">
          現在のURL: <code className="bg-gray-100 px-2 py-1 rounded">?page={page}</code>
        </p>
      </section>

      {/* ブール値トグル */}
      <section className="mb-8 p-6 bg-white rounded-lg shadow">
        <h2 className="text-xl font-semibold mb-4">3. ブール値パラメータ（トグル）</h2>
        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            checked={showFilters}
            onChange={(e) => setShowFilters(e.target.checked)}
            className="w-5 h-5 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
          />
          <span>フィルターを表示</span>
        </label>
        {showFilters && (
          <div className="mt-4 p-4 bg-gray-50 rounded">
            <p className="text-sm text-gray-700">フィルターオプションがここに表示されます</p>
          </div>
        )}
        <p className="mt-2 text-sm text-gray-600">
          現在のURL: <code className="bg-gray-100 px-2 py-1 rounded">?showFilters={showFilters ? 'true' : 'false'}</code>
        </p>
      </section>

      {/* ステータスフィルター（Enum） */}
      <section className="mb-8 p-6 bg-white rounded-lg shadow">
        <h2 className="text-xl font-semibold mb-4">4. 列挙型パラメータ（ステータス）</h2>
        <div className="flex gap-2">
          {(['all', 'qualified', 'nurturing', 'converted'] as const).map((s) => (
            <button
              key={s}
              onClick={() => setStatus(s)}
              className={`px-4 py-2 rounded transition ${
                status === s
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              {s === 'all' ? 'すべて' : s}
            </button>
          ))}
        </div>
        <p className="mt-2 text-sm text-gray-600">
          現在のURL: <code className="bg-gray-100 px-2 py-1 rounded">?status={status}</code>
        </p>
      </section>

      {/* タグ（配列） */}
      <section className="mb-8 p-6 bg-white rounded-lg shadow">
        <h2 className="text-xl font-semibold mb-4">5. 配列パラメータ（タグ）</h2>
        <div className="flex gap-2 mb-4">
          {['企業', 'ホットリード', 'フォローアップ', 'VIP'].map((tag) => (
            <button
              key={tag}
              onClick={() => handleAddTag(tag)}
              className="px-3 py-1 bg-green-500 text-white rounded hover:bg-green-600 transition text-sm"
            >
              + {tag}
            </button>
          ))}
        </div>
        <div className="flex flex-wrap gap-2">
          {tags.map((tag) => (
            <span
              key={tag}
              className="inline-flex items-center gap-2 px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
            >
              {tag}
              <button
                onClick={() => handleRemoveTag(tag)}
                className="text-blue-600 hover:text-blue-800 font-bold"
              >
                ×
              </button>
            </span>
          ))}
        </div>
        <p className="mt-2 text-sm text-gray-600">
          現在のURL: <code className="bg-gray-100 px-2 py-1 rounded">?tags={tags.join(',')}</code>
        </p>
      </section>

      {/* 複数フィルター */}
      <section className="mb-8 p-6 bg-white rounded-lg shadow">
        <h2 className="text-xl font-semibold mb-4">6. 複数パラメータの同時管理</h2>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">カテゴリー</label>
            <input
              type="text"
              value={filters.category}
              onChange={(e) => setFilters({ category: e.target.value })}
              placeholder="カテゴリー名..."
              className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">最小スコア</label>
              <input
                type="number"
                value={filters.minScore}
                onChange={(e) => setFilters({ minScore: parseInt(e.target.value) || 0 })}
                min="0"
                max="100"
                className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">最大スコア</label>
              <input
                type="number"
                value={filters.maxScore}
                onChange={(e) => setFilters({ maxScore: parseInt(e.target.value) || 100 })}
                min="0"
                max="100"
                className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>
        <p className="mt-2 text-sm text-gray-600">
          現在のURL: <code className="bg-gray-100 px-2 py-1 rounded">
            ?category={filters.category}&minScore={filters.minScore}&maxScore={filters.maxScore}
          </code>
        </p>
      </section>

      {/* リセットボタン */}
      <section className="mb-8 p-6 bg-white rounded-lg shadow">
        <button
          onClick={handleResetFilters}
          className="w-full px-6 py-3 bg-red-500 text-white rounded-lg hover:bg-red-600 transition font-semibold"
        >
          すべてのフィルターをリセット
        </button>
      </section>

      {/* 現在のURLパラメータ全体表示 */}
      <section className="p-6 bg-gray-100 rounded-lg">
        <h2 className="text-xl font-semibold mb-4">現在のURLパラメータ</h2>
        <pre className="bg-white p-4 rounded overflow-x-auto text-sm">
          {JSON.stringify({
            search,
            page,
            showFilters,
            status,
            tags,
            ...filters,
          }, null, 2)}
        </pre>
        <p className="mt-4 text-sm text-gray-600">
          完全なURL: <code className="bg-white px-2 py-1 rounded">{window.location.href}</code>
        </p>
      </section>
    </div>
  );
}
