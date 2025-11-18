import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { AlertCircle, Loader, Download } from 'lucide-react';
import { getAuditLogs } from '../../services/auditLogService';
import AuditLogTable from '../../components/admin/AuditLogTable';
import type { AuditLog } from '../../services/auditLogService';

export default function AuditLogPage() {
  const { tenantId } = useParams<{ tenantId: string }>();
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');

  // Filters
  const [entityType, setEntityType] = useState<string>('');
  const [action, setAction] = useState<string>('');
  const [skip, setSkip] = useState(0);
  const limit = 50;

  useEffect(() => {
    loadLogs();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [entityType, action, skip]);

  const loadLogs = async () => {
    try {
      setLoading(true);
      setError('');
      
      if (!tenantId) {
        setError('テナントIDが見つかりません');
        return;
      }

      const response = await getAuditLogs(tenantId, {
        entity_type: entityType || undefined,
        action: action || undefined,
        skip,
        limit,
      });

      setLogs(response.items);
    } catch (err: unknown) {
      const errorMsg = (err as { response?: { data?: { detail?: string } }; message?: string }).response?.data?.detail
        || (err as { message?: string }).message
        || '監査ログの読み込みに失敗しました';
      setError(errorMsg);
      console.error('Error loading audit logs:', err);
    } finally {
      setLoading(false);
    }
  };

  const exportLogs = () => {
    try {
      const csvContent = [
        ['日時', '操作', '対象', '詳細', 'ユーザーID', 'IPアドレス'].join(','),
        ...logs.map((log) =>
          [
            new Date(log.created_at).toLocaleString('ja-JP'),
            log.action,
            log.entity_type,
            log.entity_name || '',
            log.user_id,
            log.ip_address || '',
          ]
            .map((cell) => `"${String(cell).replace(/"/g, '""')}"`)
            .join(',')
        ),
      ].join('\n');

      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      const link = document.createElement('a');
      const url = URL.createObjectURL(blob);
      link.setAttribute('href', url);
      link.setAttribute('download', `audit-logs-${new Date().toISOString().split('T')[0]}.csv`);
      link.style.visibility = 'hidden';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (err) {
      console.error('Error exporting logs:', err);
      setError('ログのエクスポートに失敗しました');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 text-center mb-2">監査ログ</h1>
          <p className="text-center text-gray-600">マスターデータの変更履歴を確認</p>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 text-red-800 rounded flex gap-2 items-start">
            <AlertCircle size={20} className="flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold">エラーが発生しました</p>
              <p className="text-sm mt-1">{error}</p>
            </div>
          </div>
        )}

        {/* Filter Panel */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Entity Type Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                対象タイプ
              </label>
              <select
                value={entityType}
                onChange={(e) => {
                  setEntityType(e.target.value);
                  setSkip(0);
                }}
                className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">すべて</option>
                <option value="TENANT">テナント</option>
                <option value="USER">ユーザー</option>
                <option value="TOPIC">トピック</option>
                <option value="INDUSTRY">業界</option>
              </select>
            </div>

            {/* Action Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                操作
              </label>
              <select
                value={action}
                onChange={(e) => {
                  setAction(e.target.value);
                  setSkip(0);
                }}
                className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">すべて</option>
                <option value="CREATE">作成</option>
                <option value="UPDATE">更新</option>
                <option value="DELETE">削除</option>
              </select>
            </div>

            {/* Export Button */}
            <div className="flex items-end">
              <button
                onClick={exportLogs}
                disabled={logs.length === 0 || loading}
                className="w-full px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
              >
                <Download size={18} />
                CSVでエクスポート
              </button>
            </div>
          </div>

          {/* Filter Reset */}
          <div className="mt-4">
            <button
              onClick={() => {
                setEntityType('');
                setAction('');
                setSkip(0);
              }}
              className="text-sm text-blue-600 hover:text-blue-800"
            >
              フィルターをリセット
            </button>
          </div>
        </div>

        {/* Logs Table */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          {loading ? (
            <div className="flex items-center justify-center py-8">
              <Loader className="animate-spin mr-2" size={20} />
              <span>読み込み中...</span>
            </div>
          ) : (
            <AuditLogTable logs={logs} />
          )}
        </div>

        {/* Pagination */}
        {logs.length > 0 && (
          <div className="mt-6 flex justify-center gap-2">
            <button
              onClick={() => setSkip(Math.max(0, skip - limit))}
              disabled={skip === 0}
              className="px-4 py-2 border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              前へ
            </button>
            <span className="px-4 py-2 text-gray-700">
              {skip / limit + 1} ページ
            </span>
            <button
              onClick={() => setSkip(skip + limit)}
              disabled={logs.length < limit}
              className="px-4 py-2 border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              次へ
            </button>
          </div>
        )}
      </main>
    </div>
  );
}
