/**
 * Google Analytics 4 Integration Settings Component
 *
 * Allows tenant admins to configure GA4 tracking for their DiagnoLeads instance.
 */
import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Check, X, Loader2, ExternalLink, AlertCircle } from 'lucide-react';
import googleAnalyticsService, {
  type GoogleAnalyticsIntegration,
  type GoogleAnalyticsIntegrationCreate,
} from '../../services/googleAnalyticsService';

interface GoogleAnalyticsSettingsProps {
  tenantId: string;
}

export default function GoogleAnalyticsSettings({ tenantId }: GoogleAnalyticsSettingsProps) {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  const [integration, setIntegration] = useState<GoogleAnalyticsIntegration | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [testResult, setTestResult] = useState<{ status: string; message: string } | null>(null);

  // Form state
  const [formData, setFormData] = useState<GoogleAnalyticsIntegrationCreate>({
    measurement_id: '',
    measurement_protocol_api_secret: '',
    enabled: true,
    track_frontend: true,
    track_embed_widget: true,
    track_server_events: false,
  });

  // Fetch existing integration on mount
  useEffect(() => {
    fetchIntegration();
  }, [tenantId]);

  const fetchIntegration = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await googleAnalyticsService.getGoogleAnalyticsIntegration(tenantId);
      setIntegration(data);
      setFormData({
        measurement_id: data.measurement_id,
        measurement_protocol_api_secret: '', // Don't populate for security
        enabled: data.enabled,
        track_frontend: data.track_frontend,
        track_embed_widget: data.track_embed_widget,
        track_server_events: data.track_server_events,
      });
    } catch (err: any) {
      if (err.response?.status === 404) {
        // Integration not configured yet
        setIntegration(null);
      } else {
        setError('設定の取得に失敗しました');
        console.error('Failed to fetch GA integration:', err);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    setError(null);
    setTestResult(null);

    try {
      const data = await googleAnalyticsService.createOrUpdateGoogleAnalyticsIntegration(
        tenantId,
        formData
      );
      setIntegration(data);
      alert('Google Analytics設定を保存しました');
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || '設定の保存に失敗しました';
      setError(errorMessage);
      console.error('Failed to save GA integration:', err);
    } finally {
      setSaving(false);
    }
  };

  const handleTest = async () => {
    setTesting(true);
    setTestResult(null);
    setError(null);

    try {
      const result = await googleAnalyticsService.testGoogleAnalyticsConnection(tenantId);
      setTestResult(result);
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || '接続テストに失敗しました';
      setTestResult({
        status: 'failed',
        message: errorMessage,
      });
      console.error('Failed to test GA connection:', err);
    } finally {
      setTesting(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm('Google Analytics統合を削除しますか？この操作は元に戻せません。')) {
      return;
    }

    setSaving(true);
    setError(null);

    try {
      await googleAnalyticsService.deleteGoogleAnalyticsIntegration(tenantId);
      setIntegration(null);
      setFormData({
        measurement_id: '',
        measurement_protocol_api_secret: '',
        enabled: true,
        track_frontend: true,
        track_embed_widget: true,
        track_server_events: false,
      });
      alert('Google Analytics統合を削除しました');
    } catch (err: any) {
      setError('削除に失敗しました');
      console.error('Failed to delete GA integration:', err);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-2">Google Analytics 4 統合</h2>
        <p className="text-sm text-gray-600">
          診断ファネル、ユーザー行動、リード獲得をGA4で追跡します。
        </p>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4 flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-red-800">エラー</p>
            <p className="text-sm text-red-700">{error}</p>
          </div>
        </div>
      )}

      {testResult && (
        <div
          className={`border rounded-md p-4 flex items-start gap-3 ${
            testResult.status === 'success'
              ? 'bg-green-50 border-green-200'
              : 'bg-yellow-50 border-yellow-200'
          }`}
        >
          {testResult.status === 'success' ? (
            <Check className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
          ) : (
            <X className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
          )}
          <div>
            <p
              className={`text-sm font-medium ${
                testResult.status === 'success' ? 'text-green-800' : 'text-yellow-800'
              }`}
            >
              {testResult.status === 'success' ? '接続テスト成功' : '接続テスト失敗'}
            </p>
            <p
              className={`text-sm ${
                testResult.status === 'success' ? 'text-green-700' : 'text-yellow-700'
              }`}
            >
              {testResult.message}
            </p>
            {testResult.status === 'success' && (
              <a
                href="https://analytics.google.com/analytics/web/#/report/realtime-overview"
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-green-700 underline flex items-center gap-1 mt-2 hover:text-green-800"
              >
                GA4リアルタイムレポートで確認
                <ExternalLink className="w-3 h-3" />
              </a>
            )}
          </div>
        </div>
      )}

      {/* Measurement ID */}
      <div>
        <label className="block text-left text-sm font-medium text-gray-700 mb-2">
          Measurement ID <span className="text-red-500">*</span>
        </label>
        <input
          type="text"
          value={formData.measurement_id}
          onChange={(e) => setFormData({ ...formData, measurement_id: e.target.value })}
          placeholder="G-XXXXXXXXXX"
          className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
        />
        <p className="mt-1 text-sm text-gray-500">
          GA4プロパティのMeasurement ID（例: G-ABC1234567）
        </p>
      </div>

      {/* API Secret (optional) */}
      <div>
        <label className="block text-left text-sm font-medium text-gray-700 mb-2">
          Measurement Protocol API Secret（サーバーサイド追跡用）
        </label>
        <input
          type="password"
          value={formData.measurement_protocol_api_secret}
          onChange={(e) =>
            setFormData({ ...formData, measurement_protocol_api_secret: e.target.value })
          }
          placeholder="xxxxxxxxxxxxxxxxxxxxxxxxxxxx"
          className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
        />
        <p className="mt-1 text-sm text-gray-500">
          サーバーサイドイベント送信に必要（省略可）
        </p>
      </div>

      {/* Tracking Options */}
      <div className="space-y-4 pt-4 border-t border-gray-200">
        <h3 className="text-sm font-medium text-gray-900">トラッキング設定</h3>

        <div className="flex items-start justify-between">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              統合を有効化
            </label>
            <p className="text-sm text-gray-500">
              GA4トラッキングを有効化/無効化
            </p>
          </div>
          <input
            type="checkbox"
            checked={formData.enabled}
            onChange={(e) => setFormData({ ...formData, enabled: e.target.checked })}
            className="w-5 h-5 border-gray-300 rounded mt-1"
          />
        </div>

        <div className="flex items-start justify-between">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              管理画面のトラッキング
            </label>
            <p className="text-sm text-gray-500">
              React管理画面のページビューとイベントを追跡
            </p>
          </div>
          <input
            type="checkbox"
            checked={formData.track_frontend}
            onChange={(e) => setFormData({ ...formData, track_frontend: e.target.checked })}
            className="w-5 h-5 border-gray-300 rounded mt-1"
          />
        </div>

        <div className="flex items-start justify-between">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              埋め込みウィジェットのトラッキング
            </label>
            <p className="text-sm text-gray-500">
              外部サイトの埋め込み診断ウィジェットを追跡
            </p>
          </div>
          <input
            type="checkbox"
            checked={formData.track_embed_widget}
            onChange={(e) => setFormData({ ...formData, track_embed_widget: e.target.checked })}
            className="w-5 h-5 border-gray-300 rounded mt-1"
          />
        </div>

        <div className="flex items-start justify-between">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              サーバーサイドイベント
            </label>
            <p className="text-sm text-gray-500">
              サーバーからMeasurement Protocol経由でイベント送信
            </p>
          </div>
          <input
            type="checkbox"
            checked={formData.track_server_events}
            onChange={(e) => setFormData({ ...formData, track_server_events: e.target.checked })}
            className="w-5 h-5 border-gray-300 rounded mt-1"
          />
        </div>
      </div>

      {/* Info Box */}
      <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
        <h4 className="text-sm font-medium text-blue-900 mb-2">セットアップガイド</h4>
        <ol className="text-sm text-blue-800 space-y-1 list-decimal list-inside">
          <li>
            GA4プロパティを作成（
            <a
              href="https://analytics.google.com/"
              target="_blank"
              rel="noopener noreferrer"
              className="underline"
            >
              Google Analytics
            </a>
            ）
          </li>
          <li>Measurement IDを上記フィールドに入力</li>
          <li>（オプション）Measurement Protocol API Secretを生成・入力</li>
          <li>トラッキングオプションを選択</li>
          <li>「設定を保存」をクリック</li>
          <li>「接続をテスト」でGA4への接続を確認</li>
        </ol>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-4 pt-6 border-t border-gray-200">
        <button
          onClick={handleSave}
          disabled={saving || !formData.measurement_id}
          className="px-6 py-2 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
        >
          {saving && <Loader2 className="w-4 h-4 animate-spin" />}
          設定を保存
        </button>

        <button
          onClick={handleTest}
          disabled={testing || !integration}
          className="px-6 py-2 bg-gray-600 text-white font-medium rounded-md hover:bg-gray-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
        >
          {testing && <Loader2 className="w-4 h-4 animate-spin" />}
          接続をテスト
        </button>

        {integration && (
          <button
            onClick={handleDelete}
            disabled={saving}
            className="px-6 py-2 bg-red-600 text-white font-medium rounded-md hover:bg-red-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            統合を削除
          </button>
        )}
      </div>
    </div>
  );
}
