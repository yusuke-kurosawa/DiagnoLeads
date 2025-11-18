/**
 * Report Results Page
 *
 * Displays the execution results of a report.
 */

import React from 'react';
import { useLocation, useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft, Download, RefreshCw } from 'lucide-react';
import { reportService, type ReportExecutionResult } from '../../services/reportService';
import { useAuthStore } from '../../store/authStore';
import { toast } from 'react-hot-toast';

export const ReportResultsPage: React.FC = () => {
  const { tenantId, reportId } = useParams<{ tenantId: string; reportId: string }>();
  const location = useLocation();
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const executionResult = location.state?.executionResult as ReportExecutionResult;

  if (!user || !tenantId || !reportId) {
    navigate('/login');
    return null;
  }

  if (!executionResult) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <p className="text-yellow-800">
            レポート結果が見つかりません。レポートを再実行してください。
          </p>
          <button
            onClick={() => navigate(`/tenants/${tenantId}/reports`)}
            className="mt-4 text-blue-600 hover:underline"
          >
            レポート一覧に戻る
          </button>
        </div>
      </div>
    );
  }

  const handleExport = async (format: 'csv' | 'excel' | 'pdf') => {
    try {
      toast.loading(`${format.toUpperCase()}形式でエクスポート中...`);
      const blob = await reportService.export(tenantId, reportId, format);
      const filename = `${executionResult.report_name}-${new Date().toISOString().split('T')[0]}.${format === 'excel' ? 'xlsx' : format}`;
      reportService.downloadExport(blob, filename);
      toast.dismiss();
      toast.success('エクスポートが完了しました');
    } catch (error) {
      toast.dismiss();
      toast.error('エクスポートに失敗しました');
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-6">
        <button
          onClick={() => navigate(`/tenants/${tenantId}/reports`)}
          className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4"
        >
          <ArrowLeft className="w-4 h-4" />
          レポート一覧に戻る
        </button>

        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              {executionResult.report_name}
            </h1>
            <p className="text-sm text-gray-600 mt-1">
              実行日時: {new Date(executionResult.executed_at).toLocaleString('ja-JP')}
            </p>
          </div>

          <div className="flex gap-2">
            <button
              onClick={() => window.location.reload()}
              className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
            >
              <RefreshCw className="w-4 h-4" />
              再実行
            </button>

            <div className="relative group">
              <button className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
                <Download className="w-4 h-4" />
                エクスポート
              </button>
              <div className="absolute right-0 mt-1 w-32 bg-white border border-gray-200 rounded-md shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-10">
                <button
                  onClick={() => handleExport('csv')}
                  className="block w-full text-left px-4 py-2 text-sm hover:bg-gray-100"
                >
                  CSV
                </button>
                <button
                  onClick={() => handleExport('excel')}
                  className="block w-full text-left px-4 py-2 text-sm hover:bg-gray-100"
                >
                  Excel
                </button>
                <button
                  onClick={() => handleExport('pdf')}
                  className="block w-full text-left px-4 py-2 text-sm hover:bg-gray-100"
                >
                  PDF
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Summary */}
      <div className="bg-white border border-gray-200 rounded-lg p-6 mb-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">サマリー</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-gray-50 rounded-lg p-4">
            <p className="text-sm text-gray-600">総レコード数</p>
            <p className="text-2xl font-bold text-gray-900 mt-1">
              {executionResult.summary.total_records}
            </p>
          </div>
          {Object.entries(executionResult.summary.metrics).map(([key, value]) => (
            <div key={key} className="bg-gray-50 rounded-lg p-4">
              <p className="text-sm text-gray-600">{key}</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">
                {typeof value === 'number' ? value.toLocaleString() : value}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Data Table */}
      <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">データ</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                {executionResult.data_points.length > 0 &&
                  Object.keys(executionResult.data_points[0]).map((key) => (
                    <th
                      key={key}
                      className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                    >
                      {key}
                    </th>
                  ))}
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {executionResult.data_points.map((row, index) => (
                <tr key={index} className="hover:bg-gray-50">
                  {Object.values(row).map((value, cellIndex) => (
                    <td
                      key={cellIndex}
                      className="px-6 py-4 whitespace-nowrap text-sm text-gray-900"
                    >
                      {String(value)}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
