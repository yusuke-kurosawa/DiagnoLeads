/**
 * Lead List Component
 * 
 * Displays a list of leads with filtering, search, and actions.
 */

import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { SearchIcon } from 'lucide-react';
import { leadService } from '../../services/leadService';
import { LeadFilters, LeadFilterState } from './LeadFilters';
import { LeadRow } from './LeadRow';
import type { components } from '../../types/api.generated';

type LeadResponse = components['schemas']['LeadResponse'];

interface LeadListProps {
  tenantId: string;
}

export const LeadList: React.FC<LeadListProps> = ({ tenantId }) => {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState<LeadFilterState>({});

  // Fetch leads with filters
  const { data: leads, isLoading, error } = useQuery<LeadResponse[]>({
    queryKey: ['leads', tenantId, filters, searchQuery],
    queryFn: async () => {
      if (searchQuery.length > 0) {
        return leadService.search(tenantId, searchQuery);
      }
      if (filters.is_hot) {
        return leadService.getHotLeads(tenantId);
      }
      return leadService.list(tenantId, {
        status: filters.status?.[0] || undefined,
        limit: 100,
      });
    },
  });

  // Apply client-side filters
  const displayLeads = React.useMemo(() => {
    if (!leads) return [];
    
    return leads.filter((lead) => {
      // Score filter
      if (filters.score_min !== undefined && lead.score < filters.score_min) return false;
      if (filters.score_max !== undefined && lead.score > filters.score_max) return false;
      
      // Status filter
      if (filters.status && filters.status.length > 0) {
        if (!filters.status.includes(lead.status)) return false;
      }
      
      // Date filter
      if (filters.created_after) {
        if (new Date(lead.created_at) < new Date(filters.created_after)) return false;
      }
      if (filters.created_before) {
        if (new Date(lead.created_at) > new Date(filters.created_before)) return false;
      }
      
      return true;
    });
  }, [leads, filters]);

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-gray-500">Loading leads...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
        Error loading leads: {(error as Error).message}
      </div>
    );
  }

  const handleResetFilters = () => {
    setFilters({});
    setSearchQuery('');
  };

  return (
    <div className="space-y-6">
      {/* Header with actions */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">リード管理</h2>
          <p className="text-sm text-gray-600 mt-1">
            獲得したリードを管理し、商談につなげます
          </p>
        </div>
        <button
          onClick={() => navigate(`/tenants/${tenantId}/leads/create`)}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md shadow-sm"
        >
          + 新規リード
        </button>
      </div>

      <div className="grid grid-cols-12 gap-6">
        {/* Left: Filters */}
        <div className="col-span-3">
          <LeadFilters 
            filters={filters} 
            onChange={setFilters}
            onReset={handleResetFilters}
          />
        </div>

        {/* Right: List */}
        <div className="col-span-9 space-y-4">
          {/* Search bar */}
          <div className="relative">
            <SearchIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="名前、メール、会社名で検索..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          {/* Results count */}
          {displayLeads && (
            <div className="flex items-center justify-between">
              <div className="text-sm text-gray-600">
                <span className="font-semibold">{displayLeads.length}</span> 件のリード
              </div>
            </div>
          )}

          {/* Lead table */}
          {displayLeads && displayLeads.length > 0 ? (
            <div className="bg-white shadow-sm rounded-lg border border-gray-200 overflow-hidden">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-12">
                      Hot
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      名前
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      会社
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      連絡先
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      スコア
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      ステータス
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      獲得日
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {displayLeads.map((lead) => (
                    <LeadRow 
                      key={lead.id} 
                      lead={lead as any} 
                      tenantId={tenantId} 
                    />
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-12 bg-white rounded-lg border border-gray-200">
              <p className="text-gray-500 mb-2">リードが見つかりません</p>
              <p className="text-sm text-gray-400 mb-4">
                フィルターをリセットするか、新しいリードを作成してください
              </p>
              <button
                onClick={() => navigate(`/tenants/${tenantId}/leads/create`)}
                className="text-blue-600 hover:text-blue-700 font-medium"
              >
                最初のリードを作成
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
