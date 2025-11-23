import { useState, useEffect } from 'react';
import { AlertCircle, Loader, AlertTriangle, XCircle, Info } from 'lucide-react';
import { getErrorLogs, getErrorSummary, type ErrorLog, type ErrorSummary } from '../../services/errorLogService';

export default function ErrorLogPage() {
  const [logs, setLogs] = useState<ErrorLog[]>([]);
  const [summary, setSummary] = useState<ErrorSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');

  // Filters
  const [errorType, setErrorType] = useState<string>('');
  const [severity, setSeverity] = useState<string>('');
  const [environment, setEnvironment] = useState<string>('');
  const [skip, setSkip] = useState(0);
  const limit = 50;

  useEffect(() => {
    loadData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [errorType, severity, environment, skip]);

  const loadData = async () => {
    try {
      setLoading(true);
      setError('');

      // Load both summary and logs in parallel
      const [summaryResponse, logsResponse] = await Promise.all([
        getErrorSummary(),
        getErrorLogs({
          error_type: errorType || undefined,
          severity: severity || undefined,
          environment: environment || undefined,
          skip,
          limit,
        })
      ]);

      setSummary(summaryResponse);
      setLogs(logsResponse.items);
    } catch (err: unknown) {
      const errorMsg = (err as { response?: { data?: { detail?: string } }; message?: string }).response?.data?.detail
        || (err as { message?: string }).message
        || 'エラーログの読み込みに失敗しました';
      setError(errorMsg);
      console.error('Error loading error logs:', err);
    } finally {
      setLoading(false);
    }
  };

  const getSeverityIcon = (sev: string) => {
    switch (sev.toLowerCase()) {
      case 'critical':
        return <XCircle className="text-red-600" size={16} />;
      case 'high':
        return <AlertTriangle className="text-orange-600" size={16} />;
      case 'medium':
        return <AlertCircle className="text-yellow-600" size={16} />;
      default:
        return <Info className="text-blue-600" size={16} />;
    }
  };

  const getSeverityBadgeClass = (sev: string) => {
    switch (sev.toLowerCase()) {
      case 'critical':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'high':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      default:
        return 'bg-blue-100 text-blue-800 border-blue-200';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 text-center mb-2">エラーログ</h1>
          <p className="text-center text-gray-600">システムエラーの監視と分析</p>
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

        {/* Summary Stats */}
        {summary && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="text-sm text-gray-600 mb-1">総エラー数</div>
              <div className="text-3xl font-bold text-gray-900">{summary.total_errors.toLocaleString()}</div>
            </div>
            <div className="bg-white rounded-lg shadow-sm border border-red-200 p-6">
              <div className="text-sm text-red-600 mb-1 flex items-center gap-1">
                <XCircle size={14} />
                クリティカル
              </div>
              <div className="text-3xl font-bold text-red-900">{summary.critical_errors}</div>
            </div>
            <div className="bg-white rounded-lg shadow-sm border border-orange-200 p-6">
              <div className="text-sm text-orange-600 mb-1">HIGH</div>
              <div className="text-3xl font-bold text-orange-900">
                {summary.errors_by_severity.high || 0}
              </div>
            </div>
            <div className="bg-white rounded-lg shadow-sm border border-yellow-200 p-6">
              <div className="text-sm text-yellow-600 mb-1">MEDIUM</div>
              <div className="text-3xl font-bold text-yellow-900">
                {summary.errors_by_severity.medium || 0}
              </div>
            </div>
          </div>
        )}

        {/* Filter Panel */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Error Type Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                エラータイプ
              </label>
              <select
                value={errorType}
                onChange={(e) => {
                  setErrorType(e.target.value);
                  setSkip(0);
                }}
                className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">すべて</option>
                <option value="API_ERROR">API エラー</option>
                <option value="DATABASE_ERROR">データベースエラー</option>
                <option value="VALIDATION_ERROR">バリデーションエラー</option>
                <option value="AUTHENTICATION_ERROR">認証エラー</option>
                <option value="AUTHORIZATION_ERROR">認可エラー</option>
                <option value="AI_SERVICE_ERROR">AI サービスエラー</option>
                <option value="INTEGRATION_ERROR">外部連携エラー</option>
                <option value="INTERNAL_ERROR">内部エラー</option>
                <option value="FRONTEND_ERROR">フロントエンドエラー</option>
                <option value="CICD_ERROR">CI/CD エラー</option>
              </select>
            </div>

            {/* Severity Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                重要度
              </label>
              <select
                value={severity}
                onChange={(e) => {
                  setSeverity(e.target.value);
                  setSkip(0);
                }}
                className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">すべて</option>
                <option value="CRITICAL">クリティカル</option>
                <option value="HIGH">高</option>
                <option value="MEDIUM">中</option>
                <option value="LOW">低</option>
              </select>
            </div>

            {/* Environment Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                環境
              </label>
              <select
                value={environment}
                onChange={(e) => {
                  setEnvironment(e.target.value);
                  setSkip(0);
                }}
                className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">すべて</option>
                <option value="production">本番環境</option>
                <option value="staging">ステージング</option>
                <option value="development">開発環境</option>
                <option value="test">テスト環境</option>
                <option value="cicd">CI/CD</option>
              </select>
            </div>
          </div>

          {/* Filter Reset */}
          <div className="mt-4">
            <button
              onClick={() => {
                setErrorType('');
                setSeverity('');
                setEnvironment('');
                setSkip(0);
              }}
              className="text-sm text-blue-600 hover:text-blue-800"
            >
              フィルターをリセット
            </button>
          </div>
        </div>

        {/* Error Logs Table */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          {loading ? (
            <div className="flex items-center justify-center py-8">
              <Loader className="animate-spin mr-2" size={20} />
              <span>読み込み中...</span>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      重要度
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      タイプ
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      メッセージ
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      エンドポイント
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      環境
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      発生時刻
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {logs.length === 0 ? (
                    <tr>
                      <td colSpan={6} className="px-6 py-8 text-center text-gray-500">
                        エラーログが見つかりません
                      </td>
                    </tr>
                  ) : (
                    logs.map((log) => (
                      <tr key={log.id} className="hover:bg-gray-50 transition-colors">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium border ${getSeverityBadgeClass(log.severity)}`}>
                            {getSeverityIcon(log.severity)}
                            {log.severity}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {log.error_type}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-900 max-w-md truncate" title={log.error_message}>
                          {log.error_message}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-500 max-w-xs truncate" title={log.endpoint || '-'}>
                          {log.endpoint || '-'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          <span className="px-2 py-1 bg-gray-100 rounded text-xs">
                            {log.environment}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {new Date(log.created_at).toLocaleString('ja-JP')}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
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
