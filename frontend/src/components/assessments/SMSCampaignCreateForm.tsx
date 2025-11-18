import React, { useState, useEffect, useCallback } from 'react';
import { X, Plus, Trash2, Send, DollarSign } from 'lucide-react';
import { apiClient } from '@/lib/apiClient';

interface SMSCampaignCreateFormProps {
  assessmentId: string;
  tenantId: string;
  onSuccess: () => void;
  onCancel: () => void;
}

interface QRCode {
  id: string;
  name: string;
  short_url: string;
}

export const SMSCampaignCreateForm: React.FC<SMSCampaignCreateFormProps> = ({
  assessmentId,
  tenantId,
  onSuccess,
  onCancel,
}) => {
  const [name, setName] = useState('');
  const [messageTemplate, setMessageTemplate] = useState(
    '【DiagnoLeads】あなたの企業課題を無料診断！\n{url}\n※診断は3分で完了します'
  );
  const [recipients, setRecipients] = useState<string[]>(['']);
  const [qrCodeId, setQrCodeId] = useState<string>('');
  const [qrCodes, setQrCodes] = useState<QRCode[]>([]);
  const [scheduledAt, setScheduledAt] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [costEstimate, setCostEstimate] = useState<any>(null);
  const [testPhone, setTestPhone] = useState('');
  const [testSending, setTestSending] = useState(false);

  const loadQRCodes = useCallback(async () => {
    try {
      const response = await apiClient.get(
        `/tenants/${tenantId}/qr-codes?assessment_id=${assessmentId}`
      );
      setQrCodes(response.data);
      if (response.data.length > 0) {
        setQrCodeId(response.data[0].id);
      }
    } catch (error) {
      console.error('Failed to load QR codes:', error);
    }
  }, [tenantId, assessmentId]);

  const estimateCost = useCallback(async (numMessages: number) => {
    try {
      const response = await apiClient.post(
        `/tenants/${tenantId}/sms/estimate`,
        {
          num_messages: numMessages,
          region: 'JP',
        }
      );
      setCostEstimate(response.data);
    } catch (error) {
      console.error('Failed to estimate cost:', error);
    }
  }, [tenantId]);

  useEffect(() => {
    loadQRCodes();
  }, [loadQRCodes]);

  useEffect(() => {
    // Auto-estimate cost when recipients change
    const validRecipients = recipients.filter((r) => r.trim() !== '');
    if (validRecipients.length > 0) {
      estimateCost(validRecipients.length);
    }
  }, [recipients, estimateCost]);

  const handleAddRecipient = () => {
    if (recipients.length >= 1000) {
      setError('受信者は最大1000件までです');
      return;
    }
    setRecipients([...recipients, '']);
  };

  const handleRemoveRecipient = (index: number) => {
    setRecipients(recipients.filter((_, i) => i !== index));
  };

  const handleRecipientChange = (index: number, value: string) => {
    const updated = [...recipients];
    updated[index] = value;
    setRecipients(updated);
  };

  const handleBulkImport = (text: string) => {
    // Split by newline or comma
    const numbers = text
      .split(/[\n,]/)
      .map((n) => n.trim())
      .filter((n) => n !== '');

    if (numbers.length > 1000) {
      setError('受信者は最大1000件までです');
      return;
    }

    setRecipients(numbers);
  };

  const validatePhoneNumber = (phone: string): boolean => {
    // E.164 format: +[country code][number]
    const e164Regex = /^\+\d{10,15}$/;
    return e164Regex.test(phone);
  };

  const handleTestSMS = async () => {
    if (!testPhone.trim()) {
      setError('テスト送信先の電話番号を入力してください');
      return;
    }

    if (!validatePhoneNumber(testPhone)) {
      setError('電話番号はE.164形式（+81...）で入力してください');
      return;
    }

    try {
      setTestSending(true);
      setError(null);

      await apiClient.post(`/tenants/${tenantId}/sms/test`, {
        to: testPhone,
        message: messageTemplate.replace('{url}', 'https://example.com/test'),
      });

      alert('テストSMSを送信しました');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'テスト送信に失敗しました');
    } finally {
      setTestSending(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // Validation
    if (!name.trim()) {
      setError('キャンペーン名を入力してください');
      return;
    }

    if (!messageTemplate.trim()) {
      setError('メッセージテンプレートを入力してください');
      return;
    }

    if (!messageTemplate.includes('{url}')) {
      setError('メッセージテンプレートに{url}を含めてください');
      return;
    }

    const validRecipients = recipients.filter((r) => r.trim() !== '');
    if (validRecipients.length === 0) {
      setError('受信者を最低1件入力してください');
      return;
    }

    // Validate all phone numbers
    const invalidNumbers = validRecipients.filter(
      (phone) => !validatePhoneNumber(phone)
    );
    if (invalidNumbers.length > 0) {
      setError(
        `無効な電話番号があります（E.164形式で入力）: ${invalidNumbers.slice(0, 3).join(', ')}`
      );
      return;
    }

    try {
      setLoading(true);

      await apiClient.post(`/tenants/${tenantId}/sms/campaigns`, {
        assessment_id: assessmentId,
        qr_code_id: qrCodeId || null,
        name,
        message_template: messageTemplate,
        recipients: validRecipients,
        scheduled_at: scheduledAt || null,
      });

      onSuccess();
    } catch (err: any) {
      setError(
        err.response?.data?.detail || 'SMSキャンペーンの作成に失敗しました'
      );
    } finally {
      setLoading(false);
    }
  };

  const messageLength = messageTemplate.replace('{url}', 'https://example.com/abc123').length;
  const segmentCount = Math.ceil(messageLength / 160);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-2xl font-bold text-gray-900">
            新規SMSキャンペーン作成
          </h3>
          <button
            onClick={onCancel}
            className="text-gray-400 hover:text-gray-600"
          >
            <X size={24} />
          </button>
        </div>

        {error && (
          <div className="mb-4 bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} noValidate className="space-y-6">
          {/* Basic Info */}
          <div className="space-y-4">
            <h4 className="text-lg font-semibold text-gray-900">基本情報</h4>

            <div>
              <label htmlFor="campaign-name" className="block text-sm font-medium text-gray-700 mb-2">
                キャンペーン名 <span className="text-red-500">*</span>
              </label>
              <input
                id="campaign-name"
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="例: 11月診断キャンペーン"
                required
              />
            </div>

            <div>
              <label htmlFor="qr-code" className="block text-sm font-medium text-gray-700 mb-2">
                QRコード（短縮URL）
              </label>
              <select
                id="qr-code"
                value={qrCodeId}
                onChange={(e) => setQrCodeId(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">選択してください</option>
                {qrCodes.map((qr) => (
                  <option key={qr.id} value={qr.id}>
                    {qr.name} - {qr.short_url}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label htmlFor="message-template" className="block text-sm font-medium text-gray-700 mb-2">
                メッセージテンプレート <span className="text-red-500">*</span>
              </label>
              <textarea
                id="message-template"
                value={messageTemplate}
                onChange={(e) => setMessageTemplate(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
                rows={4}
                placeholder="{url}を含めてください"
                required
              />
              <div className="flex items-center justify-between text-xs text-gray-500 mt-1">
                <span>
                  {messageLength}文字 / {segmentCount}セグメント
                  {segmentCount > 1 && ` (${segmentCount}通分の料金)`}
                </span>
                <span className="text-blue-600">
                  ※ {'{url}'} は短縮URLに置き換えられます
                </span>
              </div>
            </div>

            <div>
              <label htmlFor="scheduled-at" className="block text-sm font-medium text-gray-700 mb-2">
                送信予定日時（オプション）
              </label>
              <input
                id="scheduled-at"
                type="datetime-local"
                value={scheduledAt}
                onChange={(e) => setScheduledAt(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <p className="text-xs text-gray-500 mt-1">
                空欄の場合は即時送信されます
              </p>
            </div>
          </div>

          {/* Recipients */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h4 className="text-lg font-semibold text-gray-900">
                受信者 ({recipients.filter((r) => r.trim()).length}/1000)
              </h4>
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={() => {
                    const text = prompt(
                      '電話番号を改行またはカンマ区切りで入力してください：'
                    );
                    if (text) handleBulkImport(text);
                  }}
                  className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
                >
                  一括追加
                </button>
                <button
                  type="button"
                  onClick={handleAddRecipient}
                  disabled={recipients.length >= 1000}
                  className="flex items-center gap-2 px-3 py-1 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                >
                  <Plus size={14} />
                  追加
                </button>
              </div>
            </div>

            <div className="max-h-60 overflow-y-auto space-y-2 border border-gray-200 rounded-lg p-3">
              {recipients.map((recipient, index) => (
                <div key={index} className="flex items-center gap-2">
                  <input
                    type="tel"
                    value={recipient}
                    onChange={(e) => handleRecipientChange(index, e.target.value)}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm"
                    placeholder="+819012345678"
                  />
                  <button
                    type="button"
                    onClick={() => handleRemoveRecipient(index)}
                    className="text-red-600 hover:text-red-800"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              ))}
            </div>

            <p className="text-xs text-gray-500">
              ※ 電話番号はE.164形式（+国番号+番号）で入力してください。例: +819012345678
            </p>
          </div>

          {/* Cost Estimate */}
          {costEstimate && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <DollarSign size={18} className="text-blue-600" />
                <h4 className="font-semibold text-blue-900">コスト見積もり</h4>
              </div>
              <div className="grid grid-cols-3 gap-4 text-sm">
                <div>
                  <span className="text-blue-700">送信数:</span>{' '}
                  <span className="font-semibold">{costEstimate.num_messages}通</span>
                </div>
                <div>
                  <span className="text-blue-700">単価:</span>{' '}
                  <span className="font-semibold">
                    ${costEstimate.cost_per_message.toFixed(4)}
                  </span>
                </div>
                <div>
                  <span className="text-blue-700">合計:</span>{' '}
                  <span className="font-semibold text-lg">
                    ${costEstimate.total_cost.toFixed(2)}
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* Test SMS */}
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 space-y-3">
            <h4 className="font-semibold text-gray-900">テスト送信</h4>
            <div className="space-y-2">
              <label htmlFor="test-phone" className="block text-sm font-medium text-gray-700">
                テスト送信先電話番号
              </label>
              <div className="flex items-center gap-2">
                <input
                  id="test-phone"
                  type="tel"
                  value={testPhone}
                  onChange={(e) => setTestPhone(e.target.value)}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg"
                  placeholder="+819012345678"
                />
                <button
                  type="button"
                  onClick={handleTestSMS}
                  disabled={testSending}
                  className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
                >
                  <Send size={16} />
                  {testSending ? '送信中...' : 'テスト送信'}
                </button>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center justify-end gap-3 pt-4 border-t">
            <button
              type="button"
              onClick={onCancel}
              className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
            >
              キャンセル
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? '作成中...' : 'キャンペーンを作成'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
