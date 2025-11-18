import React, { useState } from 'react';
import { Plus, Trash2, X } from 'lucide-react';
import { apiClient } from '@/lib/apiClient';

interface Variant {
  name: string;
  description: string;
  is_control: boolean;
  config: Record<string, any>;
}

interface ABTestCreateFormProps {
  assessmentId: string;
  tenantId: string;
  onSuccess: () => void;
  onCancel: () => void;
}

export const ABTestCreateForm: React.FC<ABTestCreateFormProps> = ({
  assessmentId,
  tenantId,
  onSuccess,
  onCancel,
}) => {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [testType, setTestType] = useState<string>('custom');
  const [minSampleSize, setMinSampleSize] = useState(100);
  const [confidenceThreshold, setConfidenceThreshold] = useState(0.95);
  const [explorationRate, setExplorationRate] = useState(0.1);
  const [variants, setVariants] = useState<Variant[]>([
    {
      name: 'A',
      description: 'コントロール（現行版）',
      is_control: true,
      config: {},
    },
    {
      name: 'B',
      description: 'バリアント',
      is_control: false,
      config: {},
    },
  ]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAddVariant = () => {
    if (variants.length >= 10) {
      setError('バリアントは最大10個までです');
      return;
    }

    const nextLetter = String.fromCharCode(65 + variants.length); // A, B, C...
    setVariants([
      ...variants,
      {
        name: nextLetter,
        description: `バリアント ${nextLetter}`,
        is_control: false,
        config: {},
      },
    ]);
  };

  const handleRemoveVariant = (index: number) => {
    if (variants.length <= 2) {
      setError('バリアントは最低2個必要です');
      return;
    }
    setVariants(variants.filter((_, i) => i !== index));
  };

  const handleVariantChange = (
    index: number,
    field: keyof Variant,
    value: any
  ) => {
    const updated = [...variants];
    updated[index] = { ...updated[index], [field]: value };
    setVariants(updated);
  };

  const handleConfigChange = (index: number, key: string, value: string) => {
    const updated = [...variants];
    updated[index].config = { ...updated[index].config, [key]: value };
    setVariants(updated);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // Validation
    if (!name.trim()) {
      setError('テスト名を入力してください');
      return;
    }

    if (variants.length < 2) {
      setError('バリアントは最低2個必要です');
      return;
    }

    const hasControl = variants.some((v) => v.is_control);
    if (!hasControl) {
      setError('コントロールバリアントを1つ指定してください');
      return;
    }

    try {
      setLoading(true);

      await apiClient.post(`/tenants/${tenantId}/ab-tests`, {
        assessment_id: assessmentId,
        name,
        description,
        test_type: testType,
        variants,
        min_sample_size: minSampleSize,
        confidence_threshold: confidenceThreshold,
        exploration_rate: explorationRate,
      });

      onSuccess();
    } catch (err: any) {
      setError(
        err.response?.data?.detail || 'A/Bテストの作成に失敗しました'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-2xl font-bold text-gray-900">
            新規A/Bテスト作成
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

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Basic Info */}
          <div className="space-y-4">
            <h4 className="text-lg font-semibold text-gray-900">基本情報</h4>

            <div>
              <label htmlFor="test-name" className="block text-sm font-medium text-gray-700 mb-2">
                テスト名 <span className="text-red-500">*</span>
              </label>
              <input
                id="test-name"
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="例: CTA文言テスト"
                required
              />
            </div>

            <div>
              <label htmlFor="test-description" className="block text-sm font-medium text-gray-700 mb-2">
                説明
              </label>
              <textarea
                id="test-description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                rows={3}
                placeholder="テストの目的や仮説を記載"
              />
            </div>

            <div>
              <label htmlFor="test-type" className="block text-sm font-medium text-gray-700 mb-2">
                テストタイプ
              </label>
              <select
                id="test-type"
                value={testType}
                onChange={(e) => setTestType(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="custom">カスタム</option>
                <option value="cta_text">CTA文言</option>
                <option value="cta_color">CTAカラー</option>
                <option value="intro_text">導入文</option>
                <option value="question_order">質問順序</option>
              </select>
            </div>
          </div>

          {/* Variants */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h4 className="text-lg font-semibold text-gray-900">
                バリアント ({variants.length}/10)
              </h4>
              <button
                type="button"
                onClick={handleAddVariant}
                disabled={variants.length >= 10}
                className="flex items-center gap-2 px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Plus size={16} />
                追加
              </button>
            </div>

            {variants.map((variant, index) => (
              <div
                key={index}
                className="border border-gray-200 rounded-lg p-4 space-y-3"
              >
                <div className="flex items-center justify-between">
                  <h5 className="font-semibold text-gray-900">
                    バリアント {variant.name}
                  </h5>
                  {variants.length > 2 && (
                    <button
                      type="button"
                      onClick={() => handleRemoveVariant(index)}
                      className="text-red-600 hover:text-red-800"
                    >
                      <Trash2 size={18} />
                    </button>
                  )}
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      名前
                    </label>
                    <input
                      type="text"
                      value={variant.name}
                      onChange={(e) =>
                        handleVariantChange(index, 'name', e.target.value)
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      説明
                    </label>
                    <input
                      type="text"
                      value={variant.description}
                      onChange={(e) =>
                        handleVariantChange(index, 'description', e.target.value)
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                    />
                  </div>
                </div>

                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id={`control-${index}`}
                    checked={variant.is_control}
                    onChange={(e) =>
                      handleVariantChange(index, 'is_control', e.target.checked)
                    }
                    className="h-4 w-4 text-blue-600 rounded"
                  />
                  <label
                    htmlFor={`control-${index}`}
                    className="ml-2 text-sm text-gray-700"
                  >
                    コントロール（現行版）
                  </label>
                </div>

                {/* Config */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    設定 (JSON形式)
                  </label>
                  {testType === 'cta_text' && (
                    <input
                      type="text"
                      value={variant.config.cta_text || ''}
                      onChange={(e) =>
                        handleConfigChange(index, 'cta_text', e.target.value)
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                      placeholder="CTA文言を入力"
                    />
                  )}
                  {testType === 'cta_color' && (
                    <input
                      type="color"
                      value={variant.config.cta_color || '#3B82F6'}
                      onChange={(e) =>
                        handleConfigChange(index, 'cta_color', e.target.value)
                      }
                      className="w-20 h-10 border border-gray-300 rounded-lg"
                    />
                  )}
                  {testType === 'custom' && (
                    <textarea
                      value={JSON.stringify(variant.config, null, 2)}
                      onChange={(e) => {
                        try {
                          const parsed = JSON.parse(e.target.value);
                          handleVariantChange(index, 'config', parsed);
                        } catch {
                          // Invalid JSON, ignore
                        }
                      }}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg font-mono text-sm"
                      rows={3}
                      placeholder='{"key": "value"}'
                    />
                  )}
                </div>
              </div>
            ))}
          </div>

          {/* Advanced Settings */}
          <div className="space-y-4">
            <h4 className="text-lg font-semibold text-gray-900">詳細設定</h4>

            <div className="grid grid-cols-3 gap-4">
              <div>
                <label htmlFor="min-sample-size" className="block text-sm font-medium text-gray-700 mb-2">
                  最小サンプルサイズ
                </label>
                <input
                  id="min-sample-size"
                  type="number"
                  value={minSampleSize}
                  onChange={(e) => setMinSampleSize(Number(e.target.value))}
                  min="10"
                  max="10000"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                />
                <p className="text-xs text-gray-500 mt-1">
                  勝者判定に必要な最小インプレッション数
                </p>
              </div>

              <div>
                <label htmlFor="confidence-threshold" className="block text-sm font-medium text-gray-700 mb-2">
                  信頼度しきい値
                </label>
                <input
                  id="confidence-threshold"
                  type="number"
                  value={confidenceThreshold}
                  onChange={(e) =>
                    setConfidenceThreshold(Number(e.target.value))
                  }
                  min="0.80"
                  max="0.99"
                  step="0.01"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                />
                <p className="text-xs text-gray-500 mt-1">
                  0.95 = 95%信頼度
                </p>
              </div>

              <div>
                <label htmlFor="exploration-rate" className="block text-sm font-medium text-gray-700 mb-2">
                  探索率
                </label>
                <input
                  id="exploration-rate"
                  type="number"
                  value={explorationRate}
                  onChange={(e) => setExplorationRate(Number(e.target.value))}
                  min="0.01"
                  max="0.50"
                  step="0.01"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                />
                <p className="text-xs text-gray-500 mt-1">
                  探索と活用のバランス調整
                </p>
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
              {loading ? '作成中...' : 'テストを作成'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
