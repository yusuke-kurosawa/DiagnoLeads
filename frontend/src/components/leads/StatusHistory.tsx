/**
 * Status History Component
 * 
 * Display chronological status change history:
 * - Status transitions
 * - Changed by (user)
 * - Timestamp
 * - Notes/reasons
 */


import { ArrowRightIcon, ClockIcon } from 'lucide-react';

export interface StatusChange {
  id: string;
  from_status: string;
  to_status: string;
  changed_at: string;
  changed_by?: string;
  note?: string;
}

interface StatusHistoryProps {
  history: StatusChange[];
}

const statusLabels: Record<string, string> = {
  new: '新規',
  contacted: 'コンタクト済み',
  qualified: '有望',
  negotiation: '商談中',
  won: '成約',
  lost: '失注',
};

const statusColors: Record<string, string> = {
  new: 'bg-blue-100 text-blue-800',
  contacted: 'bg-yellow-100 text-yellow-800',
  qualified: 'bg-green-100 text-green-800',
  negotiation: 'bg-purple-100 text-purple-800',
  won: 'bg-emerald-100 text-emerald-800',
  lost: 'bg-red-100 text-red-800',
};

export function StatusHistory({ history }: StatusHistoryProps) {
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('ja-JP', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getStatusLabel = (status: string): string => {
    return statusLabels[status] || status;
  };

  const getStatusColor = (status: string): string => {
    return statusColors[status] || 'bg-gray-100 text-gray-800';
  };

  if (history.length === 0) {
    return (
      <div className="bg-white shadow-sm rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">ステータス履歴</h3>
        <div className="text-center py-8 text-gray-500">
          <ClockIcon className="w-12 h-12 mx-auto mb-3 text-gray-300" />
          <p>まだステータスの変更はありません</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white shadow-sm rounded-lg border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        ステータス履歴
        <span className="ml-2 text-sm font-normal text-gray-600">
          ({history.length}件の変更)
        </span>
      </h3>

      <div className="space-y-4">
        {history.map((change, index) => (
          <div
            key={change.id}
            className="relative pb-4 border-l-2 border-gray-200 pl-6 ml-3"
          >
            {/* Timeline dot */}
            <div className="absolute left-0 top-0 -ml-[9px] w-4 h-4 rounded-full bg-blue-500 border-2 border-white" />

            {/* Change details */}
            <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
              {/* Status transition */}
              <div className="flex items-center gap-3 mb-2">
                <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(change.from_status)}`}>
                  {getStatusLabel(change.from_status)}
                </span>
                <ArrowRightIcon className="w-4 h-4 text-gray-400" />
                <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(change.to_status)}`}>
                  {getStatusLabel(change.to_status)}
                </span>
              </div>

              {/* Note */}
              {change.note && (
                <div className="text-sm text-gray-700 mb-2 bg-white p-2 rounded border border-gray-200">
                  <span className="font-medium text-gray-900">メモ: </span>
                  {change.note}
                </div>
              )}

              {/* Metadata */}
              <div className="flex items-center gap-3 text-xs text-gray-600">
                <span className="flex items-center gap-1">
                  <ClockIcon className="w-3 h-3" />
                  {formatDate(change.changed_at)}
                </span>
                {change.changed_by && (
                  <>
                    <span>•</span>
                    <span>{change.changed_by}</span>
                  </>
                )}
              </div>
            </div>

            {/* Remove line for last item */}
            {index === history.length - 1 && (
              <div className="absolute left-0 bottom-0 -ml-[1px] w-0.5 h-4 bg-white" />
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
