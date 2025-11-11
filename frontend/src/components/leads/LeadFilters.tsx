/**
 * Lead Filters Component
 * 
 * Advanced filtering for lead list:
 * - Status filter (multiple selection)
 * - Score range filter
 * - Date range filter
 * - Assessment filter
 * - Hot leads toggle
 */


import { FilterIcon, XIcon } from 'lucide-react';

export interface LeadFilterState {
  status?: string[];
  score_min?: number;
  score_max?: number;
  is_hot?: boolean;
  assessment_id?: string;
  created_after?: string;
  created_before?: string;
  search?: string;
}

interface LeadFiltersProps {
  filters: LeadFilterState;
  onChange: (filters: LeadFilterState) => void;
  onReset?: () => void;
}

export function LeadFilters({ filters, onChange, onReset }: LeadFiltersProps) {
  const handleStatusToggle = (status: string) => {
    const currentStatuses = filters.status || [];
    const newStatuses = currentStatuses.includes(status)
      ? currentStatuses.filter(s => s !== status)
      : [...currentStatuses, status];
    
    onChange({ ...filters, status: newStatuses.length > 0 ? newStatuses : undefined });
  };

  const handleScoreChange = (min?: number, max?: number) => {
    onChange({ 
      ...filters, 
      score_min: min, 
      score_max: max 
    });
  };

  const handleHotLeadsToggle = () => {
    onChange({ 
      ...filters, 
      is_hot: !filters.is_hot,
      // If enabling hot leads, set score_min to 80
      score_min: !filters.is_hot ? 80 : undefined,
      score_max: !filters.is_hot ? 100 : undefined,
    });
  };

  const handleReset = () => {
    if (onReset) {
      onReset();
    } else {
      onChange({});
    }
  };

  const activeFilterCount = [
    filters.status?.length,
    filters.score_min !== undefined || filters.score_max !== undefined,
    filters.is_hot,
    filters.assessment_id,
    filters.created_after || filters.created_before,
  ].filter(Boolean).length;

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4 space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <FilterIcon className="w-5 h-5 text-gray-600" />
          <h3 className="font-semibold text-gray-900">フィルター</h3>
          {activeFilterCount > 0 && (
            <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full">
              {activeFilterCount}
            </span>
          )}
        </div>
        {activeFilterCount > 0 && (
          <button
            onClick={handleReset}
            className="flex items-center gap-1 text-sm text-gray-600 hover:text-gray-900"
          >
            <XIcon className="w-4 h-4" />
            リセット
          </button>
        )}
      </div>

      {/* Hot Leads Toggle */}
      <div>
        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            checked={filters.is_hot || false}
            onChange={handleHotLeadsToggle}
            className="w-4 h-4 text-red-600 border-gray-300 rounded focus:ring-red-500"
          />
          <span className="text-sm font-medium text-gray-700">
            🔥 ホットリードのみ表示（スコア ≥ 80）
          </span>
        </label>
      </div>

      {/* Status Filter */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          ステータス
        </label>
        <div className="space-y-2">
          {[
            { value: 'new', label: '新規' },
            { value: 'contacted', label: 'コンタクト済み' },
            { value: 'qualified', label: '有望' },
            { value: 'negotiation', label: '商談中' },
            { value: 'won', label: '成約' },
            { value: 'lost', label: '失注' },
          ].map((status) => (
            <label key={status.value} className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={filters.status?.includes(status.value) || false}
                onChange={() => handleStatusToggle(status.value)}
                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <span className="text-sm text-gray-700">{status.label}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Score Range Filter */}
      {!filters.is_hot && (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            スコア範囲
          </label>
          <div className="flex items-center gap-3">
            <input
              type="number"
              placeholder="Min"
              value={filters.score_min || ''}
              onChange={(e) => handleScoreChange(
                e.target.value ? parseInt(e.target.value) : undefined,
                filters.score_max
              )}
              min="0"
              max="100"
              className="w-24 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
            <span className="text-gray-500">-</span>
            <input
              type="number"
              placeholder="Max"
              value={filters.score_max || ''}
              onChange={(e) => handleScoreChange(
                filters.score_min,
                e.target.value ? parseInt(e.target.value) : undefined
              )}
              min="0"
              max="100"
              className="w-24 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          <p className="text-xs text-gray-500 mt-1">0-100の範囲で指定</p>
        </div>
      )}

      {/* Date Range Filter */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          獲得日
        </label>
        <div className="space-y-2">
          <input
            type="date"
            value={filters.created_after || ''}
            onChange={(e) => onChange({ ...filters, created_after: e.target.value || undefined })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
          <span className="text-xs text-gray-500 block text-center">から</span>
          <input
            type="date"
            value={filters.created_before || ''}
            onChange={(e) => onChange({ ...filters, created_before: e.target.value || undefined })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
      </div>
    </div>
  );
}
