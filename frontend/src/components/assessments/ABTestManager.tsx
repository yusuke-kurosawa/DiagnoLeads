import React, { useState, useEffect } from 'react';
import { Play, Pause, CheckCircle, Plus, TrendingUp, Target } from 'lucide-react';
import { apiClient } from '@/lib/api-client';

interface ABTest {
  id: string;
  name: string;
  description?: string;
  assessment_id: string;
  test_type: string;
  status: 'draft' | 'running' | 'paused' | 'completed' | 'archived';
  total_impressions: number;
  total_conversions: number;
  overall_conversion_rate: number;
  winner_variant_id?: string;
  created_at: string;
}

interface ABTestManagerProps {
  assessmentId: string;
  tenantId: string;
}

export const ABTestManager: React.FC<ABTestManagerProps> = ({ assessmentId, tenantId }) => {
  const [tests, setTests] = useState<ABTest[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);

  useEffect(() => {
    loadTests();
  }, [assessmentId, tenantId]);

  const loadTests = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get(
        `/tenants/${tenantId}/ab-tests?assessment_id=${assessmentId}`
      );
      setTests(response.data);
    } catch (error) {
      console.error('Failed to load A/B tests:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      draft: { label: '下書き', className: 'bg-gray-100 text-gray-800' },
      running: { label: '実行中', className: 'bg-green-100 text-green-800' },
      paused: { label: '一時停止', className: 'bg-yellow-100 text-yellow-800' },
      completed: { label: '完了', className: 'bg-blue-100 text-blue-800' },
      archived: { label: 'アーカイブ', className: 'bg-gray-100 text-gray-600' },
    };

    const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.draft;

    return (
      <span className={`px-2 py-1 text-xs font-medium rounded-full ${config.className}`}>
        {config.label}
      </span>
    );
  };

  const formatConversionRate = (rate: number) => {
    return `${(rate * 100).toFixed(2)}%`;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">A/Bテスト</h2>
          <p className="text-sm text-gray-600 mt-1">
            Thompson Samplingで自動最適化されるA/Bテストを管理
          </p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Plus size={18} />
          新規テスト作成
        </button>
      </div>

      {/* Tests List */}
      {tests.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
          <Target size={48} className="mx-auto text-gray-400 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            A/Bテストがまだありません
          </h3>
          <p className="text-gray-600 mb-4">
            最初のA/Bテストを作成して、コンバージョン率を最適化しましょう
          </p>
          <button
            onClick={() => setShowCreateModal(true)}
            className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            <Plus size={18} />
            テストを作成
          </button>
        </div>
      ) : (
        <div className="grid gap-4">
          {tests.map((test) => (
            <div
              key={test.id}
              className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-lg font-semibold text-gray-900">{test.name}</h3>
                    {getStatusBadge(test.status)}
                  </div>
                  {test.description && (
                    <p className="text-sm text-gray-600">{test.description}</p>
                  )}
                </div>
              </div>

              {/* Stats */}
              <div className="grid grid-cols-3 gap-4 mb-4">
                <div className="bg-gray-50 rounded-lg p-3">
                  <div className="text-sm text-gray-600 mb-1">インプレッション</div>
                  <div className="text-2xl font-bold text-gray-900">
                    {test.total_impressions.toLocaleString()}
                  </div>
                </div>
                <div className="bg-gray-50 rounded-lg p-3">
                  <div className="text-sm text-gray-600 mb-1">コンバージョン</div>
                  <div className="text-2xl font-bold text-gray-900">
                    {test.total_conversions.toLocaleString()}
                  </div>
                </div>
                <div className="bg-gray-50 rounded-lg p-3">
                  <div className="text-sm text-gray-600 mb-1">CVR</div>
                  <div className="text-2xl font-bold text-green-600">
                    {formatConversionRate(test.overall_conversion_rate)}
                  </div>
                </div>
              </div>

              {/* Actions */}
              <div className="flex items-center gap-2">
                <button
                  onClick={() => window.location.href = `/ab-tests/${test.id}`}
                  className="flex items-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
                >
                  <TrendingUp size={16} />
                  詳細を見る
                </button>
                {test.status === 'draft' && (
                  <button
                    className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                  >
                    <Play size={16} />
                    開始
                  </button>
                )}
                {test.status === 'running' && (
                  <>
                    <button
                      className="flex items-center gap-2 px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors"
                    >
                      <Pause size={16} />
                      一時停止
                    </button>
                    <button
                      className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                    >
                      <CheckCircle size={16} />
                      完了
                    </button>
                  </>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Create Modal (placeholder) */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <h3 className="text-xl font-bold mb-4">新規A/Bテスト作成</h3>
            <p className="text-gray-600 mb-4">
              この機能は開発中です。ABTestCreateFormコンポーネントが必要です。
            </p>
            <button
              onClick={() => setShowCreateModal(false)}
              className="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300"
            >
              閉じる
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
