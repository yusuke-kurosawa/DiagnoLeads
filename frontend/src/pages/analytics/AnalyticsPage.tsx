/**
 * Analytics Page
 *
 * Main analytics dashboard displaying overview, charts, and trends
 */

import React, { useEffect, useState } from 'react';
import { useAuthStore } from '../../store/authStore';
import analyticsService from '../../services/analyticsService';
import type {
  OverviewAnalytics,
  TrendData,
} from '../../services/analyticsService';
import MetricCard from '../../components/analytics/MetricCard';
import StatusPieChart from '../../components/analytics/StatusPieChart';
import TrendLineChart from '../../components/analytics/TrendLineChart';
import { useTrackDashboardEvents } from '../../hooks/useGoogleAnalytics';

const AnalyticsPage: React.FC = () => {
  const { user } = useAuthStore();
  const [overview, setOverview] = useState<OverviewAnalytics | null>(null);
  const [leadTrends, setLeadTrends] = useState<TrendData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [period, setPeriod] = useState<'7d' | '30d' | '90d'>('30d');
  const { trackDashboardViewed } = useTrackDashboardEvents();

  // Track analytics page view
  useEffect(() => {
    trackDashboardViewed('analytics');
  }, [trackDashboardViewed]);

  useEffect(() => {
    if (!user?.tenant_id) return;

    const fetchAnalytics = async () => {
      try {
        setLoading(true);
        setError(null);

        // Fetch overview and trends in parallel
        const [overviewData, trendsData] = await Promise.all([
          analyticsService.getOverview(user.tenant_id),
          analyticsService.getTrends(user.tenant_id, period, 'leads'),
        ]);

        setOverview(overviewData);
        setLeadTrends(trendsData);
      } catch (err) {
        console.error('Failed to fetch analytics:', err);
        setError('分析データの取得に失敗しました');
      } finally {
        setLoading(false);
      }
    };

    fetchAnalytics();
  }, [user?.tenant_id, period]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-xl text-gray-600">読み込み中...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-xl text-red-600">{error}</div>
      </div>
    );
  }

  if (!overview) {
    return null;
  }

  const { leads, assessments } = overview;

  // Prepare chart data
  const leadStatusData = [
    { name: '新規', value: leads.new },
    { name: 'コンタクト済', value: leads.contacted },
    { name: '見込みあり', value: leads.qualified },
    { name: '成約', value: leads.converted },
    { name: '見送り', value: leads.disqualified },
  ];

  const leadScoreData = [
    { name: 'Hot (61-100)', value: leads.hot_leads },
    { name: 'Warm (31-60)', value: leads.warm_leads },
    { name: 'Cold (0-30)', value: leads.cold_leads },
  ];

  const assessmentStatusData = [
    { name: '公開中', value: assessments.published },
    { name: '下書き', value: assessments.draft },
    { name: 'アーカイブ', value: assessments.archived },
  ];

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          アナリティクスダッシュボード
        </h1>
        <p className="text-gray-600">
          リードと診断のパフォーマンスを確認できます
        </p>
      </div>

      {/* Overview Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <MetricCard label="総リード数" value={leads.total} />
        <MetricCard
          label="成約率"
          value={leads.conversion_rate}
          unit="%"
        />
        <MetricCard
          label="平均スコア"
          value={leads.average_score.toFixed(1)}
        />
        <MetricCard label="Hot リード" value={leads.hot_leads} />
      </div>

      {/* Second row metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <MetricCard label="総診断数" value={assessments.total} />
        <MetricCard label="公開中" value={assessments.published} />
        <MetricCard label="AI生成" value={assessments.ai_generated} />
        <MetricCard label="手動作成" value={assessments.manual_created} />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <StatusPieChart
          data={leadStatusData}
          title="リードステータス分布"
        />
        <StatusPieChart
          data={leadScoreData}
          title="リードスコア分布"
          colors={['#ef4444', '#f59e0b', '#3b82f6']}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <StatusPieChart
          data={assessmentStatusData}
          title="診断ステータス分布"
        />
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">AI生成 vs 手動作成</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-gray-700">AI生成</span>
              <span className="text-2xl font-bold text-blue-600">
                {assessments.ai_generated}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-700">手動作成</span>
              <span className="text-2xl font-bold text-green-600">
                {assessments.manual_created}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-700">ハイブリッド</span>
              <span className="text-2xl font-bold text-purple-600">
                {assessments.hybrid}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Trends */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold text-gray-900">トレンド</h2>
          <div className="flex space-x-2">
            <button
              onClick={() => setPeriod('7d')}
              className={`px-4 py-2 rounded ${
                period === '7d'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-700'
              }`}
            >
              7日間
            </button>
            <button
              onClick={() => setPeriod('30d')}
              className={`px-4 py-2 rounded ${
                period === '30d'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-700'
              }`}
            >
              30日間
            </button>
            <button
              onClick={() => setPeriod('90d')}
              className={`px-4 py-2 rounded ${
                period === '90d'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-700'
              }`}
            >
              90日間
            </button>
          </div>
        </div>

        {leadTrends && (
          <TrendLineChart
            data={leadTrends.data_points}
            title="リード登録数の推移"
            yAxisLabel="リード数"
          />
        )}
      </div>

      {/* Summary Stats */}
      {leadTrends && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">サマリー統計</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <div className="text-sm text-gray-600 mb-1">期間</div>
              <div className="text-xl font-bold text-gray-900">
                {leadTrends.period}
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-600 mb-1">総リード数</div>
              <div className="text-xl font-bold text-gray-900">
                {leadTrends.summary.total}
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-600 mb-1">1日あたり平均</div>
              <div className="text-xl font-bold text-gray-900">
                {leadTrends.summary.average_per_day.toFixed(1)}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AnalyticsPage;
