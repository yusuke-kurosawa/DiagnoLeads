import React, { useState, useEffect } from 'react';
import { Send, MessageSquare, CheckCircle, XCircle, Clock, Plus, RefreshCw } from 'lucide-react';
import { apiClient } from '@/lib/apiClient';
import { SMSCampaignCreateForm } from './SMSCampaignCreateForm';

interface SMSCampaign {
  id: string;
  name: string;
  assessment_id: string;
  qr_code_id?: string;
  message_template: string;
  total_recipients: number;
  sent_count: number;
  delivered_count: number;
  failed_count: number;
  status: 'pending' | 'sent' | 'delivered' | 'failed' | 'undelivered';
  created_at: string;
  sent_at?: string;
}

interface SMSCampaignManagerProps {
  assessmentId: string;
  tenantId: string;
}

export const SMSCampaignManager: React.FC<SMSCampaignManagerProps> = ({
  assessmentId,
  tenantId,
}) => {
  const [campaigns, setCampaigns] = useState<SMSCampaign[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);

  useEffect(() => {
    loadCampaigns();
  }, [tenantId]);

  const loadCampaigns = async (isRefresh = false) => {
    try {
      if (isRefresh) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }
      const response = await apiClient.get(`/tenants/${tenantId}/sms/campaigns`);
      setCampaigns(response.data);
    } catch (error) {
      console.error('Failed to load SMS campaigns:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleRefresh = () => {
    loadCampaigns(true);
  };

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      pending: { label: '送信待ち', icon: Clock, className: 'bg-yellow-100 text-yellow-800' },
      sent: { label: '送信済み', icon: Send, className: 'bg-blue-100 text-blue-800' },
      delivered: { label: '配信完了', icon: CheckCircle, className: 'bg-green-100 text-green-800' },
      failed: { label: '失敗', icon: XCircle, className: 'bg-red-100 text-red-800' },
      undelivered: { label: '未配信', icon: XCircle, className: 'bg-orange-100 text-orange-800' },
    };

    const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.pending;
    const Icon = config.icon;

    return (
      <span className={`inline-flex items-center gap-1 px-2 py-1 text-xs font-medium rounded-full ${config.className}`}>
        <Icon size={12} />
        {config.label}
      </span>
    );
  };

  const calculateSuccessRate = (campaign: SMSCampaign) => {
    if (campaign.sent_count === 0) return 0;
    return ((campaign.delivered_count / campaign.sent_count) * 100).toFixed(1);
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
          <h2 className="text-2xl font-bold text-gray-900">SMSキャンペーン</h2>
          <p className="text-sm text-gray-600 mt-1">
            Twilioを使った一斉SMS配信を管理
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handleRefresh}
            disabled={refreshing}
            className="flex items-center gap-2 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
            title="データを再読み込み"
          >
            <RefreshCw size={18} className={refreshing ? 'animate-spin' : ''} />
            更新
          </button>
          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Plus size={18} />
            新規キャンペーン作成
          </button>
        </div>
      </div>

      {/* Campaigns List */}
      {campaigns.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
          <MessageSquare size={48} className="mx-auto text-gray-400 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            SMSキャンペーンがまだありません
          </h3>
          <p className="text-gray-600 mb-4">
            最初のSMSキャンペーンを作成して、リードにアプローチしましょう
          </p>
          <button
            onClick={() => setShowCreateModal(true)}
            className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            <Plus size={18} />
            キャンペーンを作成
          </button>
        </div>
      ) : (
        <div className="grid gap-4">
          {campaigns.map((campaign) => (
            <div
              key={campaign.id}
              className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-lg font-semibold text-gray-900">{campaign.name}</h3>
                    {getStatusBadge(campaign.status)}
                  </div>
                  <p className="text-sm text-gray-600 mb-2">
                    送信先: {campaign.total_recipients.toLocaleString()}件
                  </p>
                  <p className="text-xs text-gray-500 bg-gray-50 p-2 rounded border border-gray-200 font-mono">
                    {campaign.message_template}
                  </p>
                </div>
              </div>

              {/* Stats */}
              <div className="grid grid-cols-4 gap-4 mb-4">
                <div className="bg-gray-50 rounded-lg p-3">
                  <div className="text-xs text-gray-600 mb-1">送信済み</div>
                  <div className="text-xl font-bold text-blue-600">
                    {campaign.sent_count.toLocaleString()}
                  </div>
                </div>
                <div className="bg-gray-50 rounded-lg p-3">
                  <div className="text-xs text-gray-600 mb-1">配信完了</div>
                  <div className="text-xl font-bold text-green-600">
                    {campaign.delivered_count.toLocaleString()}
                  </div>
                </div>
                <div className="bg-gray-50 rounded-lg p-3">
                  <div className="text-xs text-gray-600 mb-1">失敗</div>
                  <div className="text-xl font-bold text-red-600">
                    {campaign.failed_count.toLocaleString()}
                  </div>
                </div>
                <div className="bg-gray-50 rounded-lg p-3">
                  <div className="text-xs text-gray-600 mb-1">成功率</div>
                  <div className="text-xl font-bold text-gray-900">
                    {calculateSuccessRate(campaign)}%
                  </div>
                </div>
              </div>

              {/* Metadata */}
              <div className="flex items-center gap-4 text-sm text-gray-600">
                <span>作成: {new Date(campaign.created_at).toLocaleString('ja-JP')}</span>
                {campaign.sent_at && (
                  <span>送信: {new Date(campaign.sent_at).toLocaleString('ja-JP')}</span>
                )}
              </div>

              {/* Actions */}
              <div className="flex items-center gap-2 mt-4">
                <button
                  onClick={() => window.location.href = `/sms/campaigns/${campaign.id}`}
                  className="flex items-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
                >
                  詳細を見る
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Create Modal */}
      {showCreateModal && (
        <SMSCampaignCreateForm
          assessmentId={assessmentId}
          tenantId={tenantId}
          onSuccess={() => {
            setShowCreateModal(false);
            loadCampaigns();
          }}
          onCancel={() => setShowCreateModal(false)}
        />
      )}
    </div>
  );
};
