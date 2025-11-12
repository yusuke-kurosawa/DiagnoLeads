import { useState } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';
import type { AuditLog } from '../../services/auditLogService';

interface AuditLogTableProps {
  logs: AuditLog[];
  loading?: boolean;
}

export default function AuditLogTable({ logs, loading = false }: AuditLogTableProps) {
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const getActionBadgeColor = (action: string) => {
    switch (action) {
      case 'CREATE':
        return 'bg-green-100 text-green-800';
      case 'UPDATE':
        return 'bg-blue-100 text-blue-800';
      case 'DELETE':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getEntityTypeLabel = (type: string) => {
    switch (type) {
      case 'TENANT':
        return 'テナント';
      case 'USER':
        return 'ユーザー';
      case 'TOPIC':
        return 'トピック';
      case 'INDUSTRY':
        return '業界';
      default:
        return type;
    }
  };

  const getActionLabel = (action: string) => {
    switch (action) {
      case 'CREATE':
        return '作成';
      case 'UPDATE':
        return '更新';
      case 'DELETE':
        return '削除';
      default:
        return action;
    }
  };

  if (loading) {
    return (
      <div className="text-center py-8 text-gray-500">
        読み込み中...
      </div>
    );
  }

  if (logs.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        監査ログがありません
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse">
        <thead>
          <tr className="bg-gray-100 border-b border-gray-200">
            <th className="px-6 py-3 text-left font-semibold text-gray-700">日時</th>
            <th className="px-6 py-3 text-left font-semibold text-gray-700">操作</th>
            <th className="px-6 py-3 text-left font-semibold text-gray-700">対象</th>
            <th className="px-6 py-3 text-left font-semibold text-gray-700">詳細</th>
          </tr>
        </thead>
        <tbody>
          {logs.map((log) => (
            <tr
              key={log.id}
              className="border-b border-gray-200 hover:bg-gray-50 cursor-pointer"
              onClick={() => setExpandedId(expandedId === log.id ? null : log.id)}
            >
              <td className="px-6 py-3 text-sm text-gray-600">
                {new Date(log.created_at).toLocaleString('ja-JP')}
              </td>
              <td className="px-6 py-3">
                <span
                  className={`px-3 py-1 rounded text-xs font-semibold ${getActionBadgeColor(
                    log.action
                  )}`}
                >
                  {getActionLabel(log.action)}
                </span>
              </td>
              <td className="px-6 py-3 text-sm">
                <div className="space-y-1">
                  <p className="font-medium">{getEntityTypeLabel(log.entity_type)}</p>
                  {log.entity_name && (
                    <p className="text-gray-600">「{log.entity_name}」</p>
                  )}
                </div>
              </td>
              <td className="px-6 py-3 text-center">
                {(log.old_values || log.new_values) && (
                  expandedId === log.id ? (
                    <ChevronUp size={18} className="text-gray-600" />
                  ) : (
                    <ChevronDown size={18} className="text-gray-600" />
                  )
                )}
              </td>
            </tr>
          ))}

          {/* Expanded row details */}
          {logs.map((log) =>
            expandedId === log.id ? (
              <tr key={`${log.id}-expanded`} className="bg-gray-50 border-b border-gray-200">
                <td colSpan={4} className="px-6 py-4">
                  <div className="space-y-4">
                    {/* Metadata */}
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <p className="text-gray-600 font-medium">ユーザー ID</p>
                        <p className="text-gray-800 text-xs font-mono">{log.user_id}</p>
                      </div>
                      {log.ip_address && (
                        <div>
                          <p className="text-gray-600 font-medium">IPアドレス</p>
                          <p className="text-gray-800">{log.ip_address}</p>
                        </div>
                      )}
                      {log.reason && (
                        <div className="col-span-2">
                          <p className="text-gray-600 font-medium">変更理由</p>
                          <p className="text-gray-800">{log.reason}</p>
                        </div>
                      )}
                    </div>

                    {/* Old Values */}
                    {log.old_values && Object.keys(log.old_values).length > 0 && (
                      <div>
                        <p className="text-gray-600 font-medium mb-2">変更前</p>
                        <div className="bg-white border border-red-200 rounded p-3 text-sm">
                          <pre className="text-red-700 font-mono whitespace-pre-wrap break-words">
                            {JSON.stringify(log.old_values, null, 2)}
                          </pre>
                        </div>
                      </div>
                    )}

                    {/* New Values */}
                    {log.new_values && Object.keys(log.new_values).length > 0 && (
                      <div>
                        <p className="text-gray-600 font-medium mb-2">変更後</p>
                        <div className="bg-white border border-green-200 rounded p-3 text-sm">
                          <pre className="text-green-700 font-mono whitespace-pre-wrap break-words">
                            {JSON.stringify(log.new_values, null, 2)}
                          </pre>
                        </div>
                      </div>
                    )}
                  </div>
                </td>
              </tr>
            ) : null
          )}
        </tbody>
      </table>
    </div>
  );
}
