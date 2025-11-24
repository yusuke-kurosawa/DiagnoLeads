/**
 * Lead List Component with nuqs
 *
 * nuqsを使用してURL検索パラメータでフィルター状態を管理するサンプル実装
 *
 * このファイルは実装例であり、実際のコードには統合されていません。
 * 必要に応じてLeadList.tsxに統合してください。
 */

import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { useQueryStates, parseAsString, parseAsInteger, parseAsBoolean, parseAsArrayOf } from 'nuqs';
import { SearchIcon } from 'lucide-react';
import { leadService } from '../../services/leadService';
import type { components } from '../../types/api.generated';

type LeadResponse = components['schemas']['LeadResponse'];

interface LeadListWithNuqsProps {
  tenantId: string;
}

/**
 * nuqsを使用したLeadListコンポーネントの実装例
 *
 * メリット:
 * 1. URLでフィルター状態を共有可能（ブックマーク、共有リンク）
 * 2. ブラウザの戻る/進むボタンでフィルター履歴をナビゲート
 * 3. ページリロード後もフィルター状態が保持される
 * 4. 型安全なクエリパラメータ管理
 */
export const LeadListWithNuqs: React.FC<LeadListWithNuqsProps> = ({ tenantId }) => {
  const navigate = useNavigate();

  // nuqsでURL検索パラメータを管理
  // すべてのフィルター状態がURLに保存される
  const [filters, setFilters] = useQueryStates({
    // 検索クエリ
    search: parseAsString.withDefault(''),

    // ページネーション
    page: parseAsInteger.withDefault(1),
    limit: parseAsInteger.withDefault(20),

    // ステータスフィルター（複数選択可能）
    status: parseAsArrayOf(parseAsString).withDefault([]),

    // スコアフィルター
    score_min: parseAsInteger.withDefault(0),
    score_max: parseAsInteger.withDefault(100),

    // ホットリードフラグ
    is_hot: parseAsBoolean.withDefault(false),

    // 日付フィルター（ISO形式）
    created_after: parseAsString,
    created_before: parseAsString,

    // ソート
    sort_by: parseAsString.withDefault('created_at'),
    sort_order: parseAsString.withDefault('desc'),
  });

  // APIからリードを取得
  const { data: leads, isLoading, error } = useQuery<LeadResponse[]>({
    queryKey: ['leads', tenantId, filters],
    queryFn: async () => {
      // 検索クエリがある場合
      if (filters.search.length > 0) {
        return leadService.search(tenantId, filters.search);
      }

      // ホットリードフィルター
      if (filters.is_hot) {
        return leadService.getHotLeads(tenantId);
      }

      // 通常のリスト取得
      return leadService.list(tenantId, {
        status: filters.status[0] || undefined,
        limit: filters.limit,
      });
    },
  });

  // クライアントサイドフィルタリング
  const displayLeads = React.useMemo(() => {
    if (!leads) return [];

    return leads.filter((lead) => {
      // スコアフィルター
      if (lead.score < filters.score_min || lead.score > filters.score_max) {
        return false;
      }

      // ステータスフィルター
      if (filters.status.length > 0 && !filters.status.includes(lead.status)) {
        return false;
      }

      // 日付フィルター
      const createdAt = new Date(lead.created_at);
      if (filters.created_after && createdAt < new Date(filters.created_after)) {
        return false;
      }
      if (filters.created_before && createdAt > new Date(filters.created_before)) {
        return false;
      }

      return true;
    });
  }, [leads, filters]);

  // ページネーション用のリード
  const paginatedLeads = React.useMemo(() => {
    const start = (filters.page - 1) * filters.limit;
    const end = start + filters.limit;
    return displayLeads.slice(start, end);
  }, [displayLeads, filters.page, filters.limit]);

  const totalPages = Math.ceil(displayLeads.length / filters.limit);

  // フィルター更新関数（URLパラメータも自動更新）
  const handleSearchChange = (search: string) => {
    setFilters({ search, page: 1 }); // 検索時はページを1にリセット
  };

  const handleStatusToggle = (status: string) => {
    const newStatus = filters.status.includes(status)
      ? filters.status.filter(s => s !== status)
      : [...filters.status, status];
    setFilters({ status: newStatus, page: 1 });
  };

  const handleScoreChange = (score_min: number, score_max: number) => {
    setFilters({ score_min, score_max, page: 1 });
  };

  const handlePageChange = (page: number) => {
    setFilters({ page });
    // ページトップにスクロール
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleResetFilters = () => {
    setFilters({
      search: '',
      page: 1,
      limit: 20,
      status: [],
      score_min: 0,
      score_max: 100,
      is_hot: false,
      created_after: null,
      created_before: null,
      sort_by: 'created_at',
      sort_order: 'desc',
    });
  };

  // URLを共有する機能
  const handleShareFilters = () => {
    const url = window.location.href;
    navigator.clipboard.writeText(url);
    alert('フィルター設定付きURLをコピーしました！');
  };

  return (
    <div className="space-y-6">
      {/* ヘッダー */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">リード管理（nuqs版）</h2>
          <p className="text-sm text-gray-600 mt-1">
            URLパラメータでフィルター状態を管理
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={handleShareFilters}
            className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md shadow-sm"
          >
            🔗 フィルターを共有
          </button>
          <button
            onClick={() => navigate(`/tenants/${tenantId}/leads/create`)}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md shadow-sm"
          >
            + 新規リード
          </button>
        </div>
      </div>

      <div className="grid grid-cols-12 gap-6">
        {/* サイドバー: フィルター */}
        <div className="col-span-3 space-y-4">
          <div className="bg-white p-4 rounded-lg shadow">
            <h3 className="font-semibold mb-4">フィルター</h3>

            {/* 検索 */}
            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">検索</label>
              <div className="relative">
                <SearchIcon className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
                <input
                  type="text"
                  value={filters.search}
                  onChange={(e) => handleSearchChange(e.target.value)}
                  placeholder="リードを検索..."
                  className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            {/* ステータス */}
            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">ステータス</label>
              <div className="space-y-2">
                {['qualified', 'nurturing', 'converted', 'unqualified'].map((status) => (
                  <label key={status} className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={filters.status.includes(status)}
                      onChange={() => handleStatusToggle(status)}
                      className="rounded text-blue-600 focus:ring-2 focus:ring-blue-500"
                    />
                    <span className="text-sm">{status}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* スコア範囲 */}
            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">スコア範囲</label>
              <div className="grid grid-cols-2 gap-2">
                <input
                  type="number"
                  value={filters.score_min}
                  onChange={(e) => handleScoreChange(parseInt(e.target.value) || 0, filters.score_max)}
                  min="0"
                  max="100"
                  placeholder="最小"
                  className="px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                />
                <input
                  type="number"
                  value={filters.score_max}
                  onChange={(e) => handleScoreChange(filters.score_min, parseInt(e.target.value) || 100)}
                  min="0"
                  max="100"
                  placeholder="最大"
                  className="px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            {/* ホットリード */}
            <div className="mb-4">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={filters.is_hot}
                  onChange={(e) => setFilters({ is_hot: e.target.checked, page: 1 })}
                  className="rounded text-blue-600 focus:ring-2 focus:ring-blue-500"
                />
                <span className="text-sm font-medium">🔥 ホットリードのみ</span>
              </label>
            </div>

            <button
              onClick={handleResetFilters}
              className="w-full px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition"
            >
              フィルターをリセット
            </button>
          </div>

          {/* 現在のURL表示 */}
          <div className="bg-blue-50 p-3 rounded-lg text-xs">
            <p className="font-semibold mb-1">現在のURL:</p>
            <code className="block break-all text-blue-800">{window.location.search || '(パラメータなし)'}</code>
          </div>
        </div>

        {/* メインコンテンツ: リード一覧 */}
        <div className="col-span-9">
          {isLoading && (
            <div className="text-center py-12">読み込み中...</div>
          )}

          {error && (
            <div className="text-center py-12 text-red-600">
              エラーが発生しました
            </div>
          )}

          {!isLoading && !error && (
            <>
              {/* 結果サマリー */}
              <div className="bg-white p-4 rounded-lg shadow mb-4">
                <p className="text-sm text-gray-600">
                  {displayLeads.length}件のリードが見つかりました
                  （{filters.page}ページ / {totalPages}ページ中）
                </p>
              </div>

              {/* リードテーブル */}
              <div className="bg-white rounded-lg shadow overflow-hidden">
                <table className="min-w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">名前</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">スコア</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">ステータス</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">作成日</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {paginatedLeads.map((lead) => (
                      <tr key={lead.id} className="hover:bg-gray-50 cursor-pointer">
                        <td className="px-6 py-4 whitespace-nowrap">{lead.name}</td>
                        <td className="px-6 py-4 whitespace-nowrap">{lead.score}</td>
                        <td className="px-6 py-4 whitespace-nowrap">{lead.status}</td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          {new Date(lead.created_at).toLocaleDateString()}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* ページネーション */}
              {totalPages > 1 && (
                <div className="bg-white p-4 rounded-lg shadow mt-4">
                  <div className="flex justify-center gap-2">
                    <button
                      onClick={() => handlePageChange(filters.page - 1)}
                      disabled={filters.page === 1}
                      className="px-4 py-2 bg-blue-500 text-white rounded disabled:bg-gray-300 disabled:cursor-not-allowed"
                    >
                      前へ
                    </button>
                    <span className="px-4 py-2">
                      {filters.page} / {totalPages}
                    </span>
                    <button
                      onClick={() => handlePageChange(filters.page + 1)}
                      disabled={filters.page === totalPages}
                      className="px-4 py-2 bg-blue-500 text-white rounded disabled:bg-gray-300 disabled:cursor-not-allowed"
                    >
                      次へ
                    </button>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};
