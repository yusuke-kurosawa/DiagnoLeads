/**
 * Report List Component
 *
 * Displays a list of custom reports with actions.
 */

import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import {
  FileBarChart,
  Plus,
  Play,
  Download,
  Edit,
  Trash2,
  Calendar,
  Globe,
  Lock,
} from 'lucide-react';
import { reportService, type Report } from '../../services/reportService';
import { SkeletonTable } from '@/components/ui/skeleton';
import { EmptyState, ErrorEmptyState } from '@/components/ui/empty-state';
import { CreateReportDialog } from './CreateReportDialog';
import { toast } from 'react-hot-toast';

interface ReportListProps {
  tenantId: string;
}

export const ReportList: React.FC<ReportListProps> = ({ tenantId }) => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [executingReportId, setExecutingReportId] = useState<string | null>(null);

  // Fetch reports
  const { data: reports, isLoading, error } = useQuery<Report[]>({
    queryKey: ['reports', tenantId],
    queryFn: () => reportService.list(tenantId),
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: (reportId: string) => reportService.delete(tenantId, reportId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reports', tenantId] });
      toast.success('レポートを削除しました');
    },
    onError: () => {
      toast.error('レポートの削除に失敗しました');
    },
  });

  // Execute mutation
  const executeMutation = useMutation({
    mutationFn: (reportId: string) => reportService.execute(tenantId, reportId),
    onSuccess: (result, reportId) => {
      setExecutingReportId(null);
      toast.success('レポートを実行しました');
      // Navigate to results page
      navigate(`/tenants/${tenantId}/reports/${reportId}/results`, {
        state: { executionResult: result },
      });
    },
    onError: () => {
      setExecutingReportId(null);
      toast.error('レポートの実行に失敗しました');
    },
  });

  // Export handler
  const handleExport = async (reportId: string, format: 'csv' | 'excel' | 'pdf') => {
    try {
      toast.loading(`${format.toUpperCase()}形式でエクスポート中...`);
      const blob = await reportService.export(tenantId, reportId, format);
      const report = reports?.find((r) => r.id === reportId);
      const filename = `${report?.name || 'report'}-${new Date().toISOString().split('T')[0]}.${format === 'excel' ? 'xlsx' : format}`;
      reportService.downloadExport(blob, filename);
      toast.dismiss();
      toast.success('エクスポートが完了しました');
    } catch (error) {
      toast.dismiss();
      toast.error('エクスポートに失敗しました');
    }
  };

  // Delete handler
  const handleDelete = (reportId: string, reportName: string) => {
    if (window.confirm(`「${reportName}」を削除してもよろしいですか？`)) {
      deleteMutation.mutate(reportId);
    }
  };

  // Execute handler
  const handleExecute = (reportId: string) => {
    setExecutingReportId(reportId);
    executeMutation.mutate(reportId);
  };

  // Get report type label
  const getReportTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      custom: 'カスタム',
      lead_analysis: 'リード分析',
      assessment_performance: 'アセスメント',
      conversion_funnel: 'コンバージョン',
      ai_insights: 'AI分析',
    };
    return labels[type] || type;
  };

  return (
    <div className="space-y-6">
      {/* Header with actions */}
      <div className="flex justify-between items-center">
        <button
          onClick={() => setIsCreateDialogOpen(true)}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md shadow-sm flex items-center gap-2"
        >
          <Plus className="w-4 h-4" />
          新規レポート作成
        </button>
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="bg-white shadow-sm rounded-lg border border-gray-200 p-4">
          <SkeletonTable rows={5} />
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="bg-white shadow-sm rounded-lg border border-gray-200 p-4">
          <ErrorEmptyState
            onRetry={() => queryClient.invalidateQueries({ queryKey: ['reports', tenantId] })}
            errorMessage="レポートの読み込みに失敗しました"
          />
        </div>
      )}

      {/* Empty State */}
      {!isLoading && !error && (!reports || reports.length === 0) && (
        <div className="bg-white shadow-sm rounded-lg border border-gray-200 p-12">
          <EmptyState
            icon={FileBarChart}
            title="レポートがありません"
            description="カスタムレポートを作成して、データ分析を始めましょう"
            action={{
              label: '最初のレポートを作成',
              onClick: () => setIsCreateDialogOpen(true),
            }}
          />
        </div>
      )}

      {/* Report Cards */}
      {!isLoading && !error && reports && reports.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {reports.map((report) => (
            <div
              key={report.id}
              className="bg-white border border-gray-200 rounded-lg shadow-sm hover:shadow-md transition-shadow p-6"
            >
              {/* Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-blue-100 rounded-lg">
                    <FileBarChart className="w-5 h-5 text-blue-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900">{report.name}</h3>
                    <p className="text-xs text-gray-500 mt-1">
                      {getReportTypeLabel(report.report_type)}
                    </p>
                  </div>
                </div>
              </div>

              {/* Description */}
              {report.description && (
                <p className="text-sm text-gray-600 mb-4 line-clamp-2">
                  {report.description}
                </p>
              )}

              {/* Metadata */}
              <div className="flex items-center gap-4 mb-4 text-xs text-gray-500">
                {report.is_scheduled && (
                  <div className="flex items-center gap-1">
                    <Calendar className="w-3 h-3" />
                    <span>スケジュール済み</span>
                  </div>
                )}
                <div className="flex items-center gap-1">
                  {report.is_public ? (
                    <>
                      <Globe className="w-3 h-3" />
                      <span>公開</span>
                    </>
                  ) : (
                    <>
                      <Lock className="w-3 h-3" />
                      <span>非公開</span>
                    </>
                  )}
                </div>
              </div>

              {/* Actions */}
              <div className="flex items-center gap-2 pt-4 border-t border-gray-200">
                <button
                  onClick={() => handleExecute(report.id)}
                  disabled={executingReportId === report.id}
                  className="flex items-center gap-1 px-3 py-2 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex-1 justify-center"
                >
                  <Play className="w-3 h-3" />
                  {executingReportId === report.id ? '実行中...' : '実行'}
                </button>

                <div className="relative group">
                  <button
                    className="p-2 text-gray-600 hover:bg-gray-100 rounded"
                    title="エクスポート"
                  >
                    <Download className="w-4 h-4" />
                  </button>
                  <div className="absolute right-0 mt-1 w-32 bg-white border border-gray-200 rounded-md shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-10">
                    <button
                      onClick={() => handleExport(report.id, 'csv')}
                      className="block w-full text-left px-4 py-2 text-sm hover:bg-gray-100"
                    >
                      CSV
                    </button>
                    <button
                      onClick={() => handleExport(report.id, 'excel')}
                      className="block w-full text-left px-4 py-2 text-sm hover:bg-gray-100"
                    >
                      Excel
                    </button>
                    <button
                      onClick={() => handleExport(report.id, 'pdf')}
                      className="block w-full text-left px-4 py-2 text-sm hover:bg-gray-100"
                    >
                      PDF
                    </button>
                  </div>
                </div>

                <button
                  onClick={() => navigate(`/tenants/${tenantId}/reports/${report.id}/edit`)}
                  className="p-2 text-gray-600 hover:bg-gray-100 rounded"
                  title="編集"
                >
                  <Edit className="w-4 h-4" />
                </button>

                <button
                  onClick={() => handleDelete(report.id, report.name)}
                  disabled={deleteMutation.isPending}
                  className="p-2 text-red-600 hover:bg-red-50 rounded disabled:opacity-50"
                  title="削除"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Create Report Dialog */}
      <CreateReportDialog
        isOpen={isCreateDialogOpen}
        onClose={() => setIsCreateDialogOpen(false)}
        tenantId={tenantId}
      />
    </div>
  );
};
