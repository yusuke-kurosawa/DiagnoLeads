import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { MessageSquare, Check, Send, AlertCircle } from 'lucide-react';
import { apiClient } from '@/lib/apiClient';

interface TeamsSettings {
  enabled: boolean;
  configured: boolean;
  hot_lead_threshold: number;
  webhook_url_set: boolean;
}

export default function TeamsIntegration() {
  const { tenantId } = useParams<{ tenantId: string }>();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  const [settings, setSettings] = useState<TeamsSettings>({
    enabled: false,
    configured: false,
    hot_lead_threshold: 80,
    webhook_url_set: false,
  });
  const [webhookUrl, setWebhookUrl] = useState('');
  const [threshold, setThreshold] = useState(80);
  const [testMessage, setTestMessage] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    fetchSettings();
  }, [tenantId]);

  const fetchSettings = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get(`/api/v1/tenants/${tenantId}/integrations/teams`);
      setSettings(response.data);
      setThreshold(response.data.hot_lead_threshold);
      setLoading(false);
    } catch (err) {
      console.error('Failed to fetch Teams settings:', err);
      setError('設定の読み込みに失敗しました');
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      setError(null);
      setSuccess(null);

      await apiClient.put(`/api/v1/tenants/${tenantId}/integrations/teams`, {
        webhook_url: webhookUrl || null,
        enabled: true,
        hot_lead_threshold: threshold,
      });

      setSuccess('設定を保存しました');
      await fetchSettings();
    } catch (err: any) {
      console.error('Failed to save Teams settings:', err);
      setError(err.response?.data?.detail || '設定の保存に失敗しました');
    } finally {
      setSaving(false);
    }
  };

  const handleTestNotification = async () => {
    try {
      setTesting(true);
      setError(null);
      setSuccess(null);

      await apiClient.post(`/api/v1/tenants/${tenantId}/integrations/teams/test`, {
        message: testMessage || 'これはDiagnoLeadsからのテスト通知です',
      });

      setSuccess('テスト通知を送信しました。Teamsチャネルをご確認ください。');
      setTestMessage('');
    } catch (err: any) {
      console.error('Failed to send test notification:', err);
      setError(err.response?.data?.detail || 'テスト通知の送信に失敗しました');
    } finally {
      setTesting(false);
    }
  };

  const handleRemove = async () => {
    if (!confirm('Teams統合を削除してもよろしいですか？')) {
      return;
    }

    try {
      setSaving(true);
      setError(null);
      setSuccess(null);

      await apiClient.delete(`/api/v1/tenants/${tenantId}/integrations/teams`);

      setSuccess('Teams統合を削除しました');
      setWebhookUrl('');
      await fetchSettings();
    } catch (err: any) {
      console.error('Failed to remove Teams integration:', err);
      setError(err.response?.data?.detail || 'Teams統合の削除に失敗しました');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="p-2 bg-blue-100 rounded-lg">
          <MessageSquare className="w-6 h-6 text-blue-600" />
        </div>
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Microsoft Teams統合</h3>
          <p className="text-sm text-gray-600">
            ホットリード獲得時にTeamsチャネルへ自動通知
          </p>
        </div>
      </div>

      {/* Status Badge */}
      {settings.configured && (
        <div className="flex items-center gap-2 px-4 py-2 bg-green-50 border border-green-200 rounded-lg">
          <Check className="w-4 h-4 text-green-600" />
          <span className="text-sm font-medium text-green-700">Teams統合が有効です</span>
        </div>
      )}

      {/* Error Alert */}
      {error && (
        <div className="flex items-start gap-2 px-4 py-3 bg-red-50 border border-red-200 rounded-lg">
          <AlertCircle className="w-5 h-5 text-red-600 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-red-700">エラー</p>
            <p className="text-sm text-red-600">{error}</p>
          </div>
        </div>
      )}

      {/* Success Alert */}
      {success && (
        <div className="flex items-start gap-2 px-4 py-3 bg-green-50 border border-green-200 rounded-lg">
          <Check className="w-5 h-5 text-green-600 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-green-700">成功</p>
            <p className="text-sm text-green-600">{success}</p>
          </div>
        </div>
      )}

      {/* Webhook URL Input */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Incoming Webhook URL
          <span className="text-red-500 ml-1">*</span>
        </label>
        <input
          type="url"
          value={webhookUrl}
          onChange={(e) => setWebhookUrl(e.target.value)}
          placeholder="https://your-tenant.webhook.office.com/webhookb2/..."
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        />
        <p className="mt-2 text-sm text-gray-600">
          Teamsチャネルで「...」→「コネクタ」→「Incoming Webhook」から取得できます
        </p>
      </div>

      {/* Hot Lead Threshold */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          ホットリード通知のしきい値
        </label>
        <div className="flex items-center gap-4">
          <input
            type="range"
            min="0"
            max="100"
            value={threshold}
            onChange={(e) => setThreshold(parseInt(e.target.value))}
            className="flex-1"
          />
          <span className="text-lg font-semibold text-gray-900 w-16 text-right">
            {threshold}点
          </span>
        </div>
        <p className="mt-2 text-sm text-gray-600">
          スコアがこの値以上のリードをTeamsに通知します
        </p>
      </div>

      {/* Save Button */}
      <div className="flex gap-3">
        <button
          onClick={handleSave}
          disabled={saving || !webhookUrl}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {saving ? '保存中...' : '設定を保存'}
        </button>

        {settings.configured && (
          <button
            onClick={handleRemove}
            disabled={saving}
            className="px-4 py-2 border border-red-300 text-red-600 rounded-lg hover:bg-red-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            統合を削除
          </button>
        )}
      </div>

      {/* Test Notification */}
      {settings.configured && (
        <div className="mt-8 pt-6 border-t border-gray-200">
          <h4 className="text-sm font-semibold text-gray-900 mb-4">テスト通知</h4>
          <div className="space-y-3">
            <input
              type="text"
              value={testMessage}
              onChange={(e) => setTestMessage(e.target.value)}
              placeholder="テストメッセージ（オプション）"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
            <button
              onClick={handleTestNotification}
              disabled={testing}
              className="flex items-center gap-2 px-4 py-2 border border-blue-600 text-blue-600 rounded-lg hover:bg-blue-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <Send size={16} />
              {testing ? 'テスト送信中...' : 'テスト通知を送信'}
            </button>
          </div>
        </div>
      )}

      {/* Setup Guide */}
      <div className="mt-8 p-4 bg-gray-50 rounded-lg border border-gray-200">
        <h4 className="text-sm font-semibold text-gray-900 mb-3">セットアップ手順</h4>
        <ol className="space-y-2 text-sm text-gray-700 list-decimal list-inside">
          <li>Microsoft Teamsで通知を受け取りたいチャネルを開く</li>
          <li>チャネル名の横の「...」→「コネクタ」をクリック</li>
          <li>「Incoming Webhook」を検索して「構成」をクリック</li>
          <li>名前を「DiagnoLeads」に設定して「作成」をクリック</li>
          <li>表示されたWebhook URLをコピーして上記に貼り付け</li>
          <li>「設定を保存」をクリック</li>
          <li>「テスト通知を送信」で動作確認</li>
        </ol>
      </div>
    </div>
  );
}
