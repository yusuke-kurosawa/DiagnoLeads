/**
 * Create Report Dialog Component
 *
 * Dialog for creating a new custom report.
 */

import React, { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { X } from 'lucide-react';
import { reportService, type CreateReportData } from '../../services/reportService';
import { toast } from 'react-hot-toast';

interface CreateReportDialogProps {
  isOpen: boolean;
  onClose: () => void;
  tenantId: string;
}

const REPORT_TYPES = [
  { value: 'custom', label: 'カスタムレポート' },
  { value: 'lead_analysis', label: 'リード分析レポート' },
  { value: 'assessment_performance', label: 'アセスメントパフォーマンス' },
  { value: 'conversion_funnel', label: 'コンバージョンファネル' },
  { value: 'ai_insights', label: 'AI分析レポート' },
];

const AVAILABLE_METRICS = [
  { value: 'leads_total', label: 'リード総数' },
  { value: 'conversion_rate', label: 'コンバージョン率' },
  { value: 'average_score', label: '平均スコア' },
  { value: 'hot_leads_count', label: 'ホットリード数' },
  { value: 'warm_leads_count', label: 'ウォームリード数' },
  { value: 'cold_leads_count', label: 'コールドリード数' },
  { value: 'assessment_completions', label: 'アセスメント完了数' },
  { value: 'assessment_completion_rate', label: 'アセスメント完了率' },
];

const VISUALIZATION_TYPES = [
  { value: 'table', label: 'テーブル' },
  { value: 'bar_chart', label: '棒グラフ' },
  { value: 'line_chart', label: '折れ線グラフ' },
  { value: 'pie_chart', label: '円グラフ' },
];

const GROUP_BY_OPTIONS = [
  { value: 'none', label: 'グループ化なし' },
  { value: 'status', label: 'ステータス' },
  { value: 'industry', label: '業界' },
  { value: 'date', label: '日付' },
  { value: 'assessment', label: 'アセスメント' },
];

export const CreateReportDialog: React.FC<CreateReportDialogProps> = ({
  isOpen,
  onClose,
  tenantId,
}) => {
  const queryClient = useQueryClient();
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    report_type: 'custom',
    metrics: [] as string[],
    visualization: 'table',
    group_by: 'none',
    is_public: false,
  });

  const createMutation = useMutation({
    mutationFn: (data: CreateReportData) => reportService.create(tenantId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reports', tenantId] });
      toast.success('レポートを作成しました');
      handleClose();
    },
    onError: () => {
      toast.error('レポートの作成に失敗しました');
    },
  });

  const handleClose = () => {
    setFormData({
      name: '',
      description: '',
      report_type: 'custom',
      metrics: [],
      visualization: 'table',
      group_by: 'none',
      is_public: false,
    });
    onClose();
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.name.trim()) {
      toast.error('レポート名を入力してください');
      return;
    }

    if (formData.metrics.length === 0) {
      toast.error('少なくとも1つのメトリクスを選択してください');
      return;
    }

    const reportData: CreateReportData = {
      name: formData.name,
      description: formData.description || undefined,
      report_type: formData.report_type,
      config: {
        metrics: formData.metrics,
        visualization: formData.visualization as any,
        group_by: formData.group_by !== 'none' ? (formData.group_by as any) : undefined,
        sort_order: 'desc',
      },
      is_public: formData.is_public,
    };

    createMutation.mutate(reportData);
  };

  const handleMetricToggle = (metric: string) => {
    setFormData((prev) => ({
      ...prev,
      metrics: prev.metrics.includes(metric)
        ? prev.metrics.filter((m) => m !== metric)
        : [...prev.metrics, metric],
    }));
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">新規レポート作成</h2>
          <button
            onClick={handleClose}
            className="p-2 hover:bg-gray-100 rounded-full"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Name */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              レポート名 <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="例: 月次リード分析レポート"
            />
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              説明
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              rows={3}
              placeholder="レポートの目的や内容を説明してください"
            />
          </div>

          {/* Report Type */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              レポートタイプ
            </label>
            <select
              value={formData.report_type}
              onChange={(e) => setFormData({ ...formData, report_type: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              {REPORT_TYPES.map((type) => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
          </div>

          {/* Metrics */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              メトリクス <span className="text-red-500">*</span>
            </label>
            <div className="grid grid-cols-2 gap-2">
              {AVAILABLE_METRICS.map((metric) => (
                <label
                  key={metric.value}
                  className="flex items-center gap-2 p-3 border border-gray-200 rounded-md hover:bg-gray-50 cursor-pointer"
                >
                  <input
                    type="checkbox"
                    checked={formData.metrics.includes(metric.value)}
                    onChange={() => handleMetricToggle(metric.value)}
                    className="w-4 h-4 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="text-sm text-gray-700">{metric.label}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Visualization Type */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              可視化タイプ
            </label>
            <select
              value={formData.visualization}
              onChange={(e) => setFormData({ ...formData, visualization: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              {VISUALIZATION_TYPES.map((type) => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
          </div>

          {/* Group By */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              グループ化
            </label>
            <select
              value={formData.group_by}
              onChange={(e) => setFormData({ ...formData, group_by: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              {GROUP_BY_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          {/* Public */}
          <div>
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={formData.is_public}
                onChange={(e) => setFormData({ ...formData, is_public: e.target.checked })}
                className="w-4 h-4 text-blue-600 focus:ring-blue-500"
              />
              <span className="text-sm text-gray-700">
                このレポートをテナント内の全ユーザーに公開する
              </span>
            </label>
          </div>

          {/* Actions */}
          <div className="flex justify-end gap-3 pt-4 border-t border-gray-200">
            <button
              type="button"
              onClick={handleClose}
              className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
            >
              キャンセル
            </button>
            <button
              type="submit"
              disabled={createMutation.isPending}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {createMutation.isPending ? '作成中...' : 'レポートを作成'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
