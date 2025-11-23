import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { AlertCircle, Loader, DollarSign, Zap, TrendingUp } from 'lucide-react';
import { getAIUsageSummary, type AIUsageSummary } from '../../services/aiUsageService';

export default function AIUsagePage() {
  const { tenantId } = useParams<{ tenantId: string }>();
  const [summary, setSummary] = useState<AIUsageSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    loadSummary();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const loadSummary = async () => {
    try {
      setLoading(true);
      setError('');

      if (!tenantId) {
        setError('テナントIDが見つかりません');
        return;
      }

      const response = await getAIUsageSummary(tenantId);
      setSummary(response);
    } catch (err: unknown) {
      const errorMsg = (err as { response?: { data?: { detail?: string } }; message?: string }).response?.data?.detail
        || (err as { message?: string }).message
        || 'AI使用量の読み込みに失敗しました';
      setError(errorMsg);
      console.error('Error loading AI usage:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 text-center mb-2">AI 使用量</h1>
          <p className="text-center text-gray-600">Claude API の使用状況とコスト分析</p>
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

        {loading ? (
          <div className="flex items-center justify-center py-12">
            <Loader className="animate-spin mr-2" size={24} />
            <span>読み込み中...</span>
          </div>
        ) : summary ? (
          <>
            {/* Summary Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <div className="flex items-center gap-2 text-sm text-gray-600 mb-1">
                  <Zap size={14} className="text-blue-600" />
                  総リクエスト数
                </div>
                <div className="text-3xl font-bold text-gray-900">{summary.total_requests.toLocaleString()}</div>
              </div>

              <div className="bg-white rounded-lg shadow-sm border border-green-200 p-6">
                <div className="flex items-center gap-2 text-sm text-green-600 mb-1">
                  <TrendingUp size={14} />
                  総トークン数
                </div>
                <div className="text-3xl font-bold text-green-900">{summary.total_tokens.toLocaleString()}</div>
              </div>

              <div className="bg-white rounded-lg shadow-sm border border-purple-200 p-6">
                <div className="flex items-center gap-2 text-sm text-purple-600 mb-1">
                  <DollarSign size={14} />
                  総コスト (USD)
                </div>
                <div className="text-3xl font-bold text-purple-900">
                  ${summary.total_cost_usd.toFixed(2)}
                </div>
              </div>

              <div className="bg-white rounded-lg shadow-sm border border-blue-200 p-6">
                <div className="text-sm text-blue-600 mb-1">成功率</div>
                <div className="text-3xl font-bold text-blue-900">
                  {(summary.success_rate * 100).toFixed(1)}%
                </div>
              </div>
            </div>

            {/* Operations Breakdown */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">操作別内訳</h2>

              <div className="space-y-4">
                {Object.entries(summary.operations).map(([operation, stats]) => {
                  const percentage = summary.total_requests > 0
                    ? (stats.count / summary.total_requests) * 100
                    : 0;

                  return (
                    <div key={operation} className="border-b border-gray-200 pb-4 last:border-0">
                      <div className="flex justify-between items-start mb-2">
                        <div>
                          <div className="font-medium text-gray-900">{operation}</div>
                          <div className="text-sm text-gray-500">{stats.count.toLocaleString()} リクエスト</div>
                        </div>
                        <div className="text-right">
                          <div className="text-sm font-semibold text-purple-900">${stats.cost_usd.toFixed(2)}</div>
                          <div className="text-xs text-gray-500">{stats.tokens.toLocaleString()} トークン</div>
                        </div>
                      </div>

                      {/* Progress Bar */}
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-blue-600 h-2 rounded-full transition-all"
                          style={{ width: `${percentage}%` }}
                        ></div>
                      </div>
                      <div className="text-xs text-gray-500 mt-1">{percentage.toFixed(1)}% of total</div>
                    </div>
                  );
                })}
              </div>

              {Object.keys(summary.operations).length === 0 && (
                <div className="text-center text-gray-500 py-8">
                  使用データがありません
                </div>
              )}
            </div>
          </>
        ) : (
          <div className="text-center text-gray-500 py-12">
            データが見つかりません
          </div>
        )}
      </main>
    </div>
  );
}
