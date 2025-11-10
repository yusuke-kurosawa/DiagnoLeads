/**
 * Lead List Component
 * 
 * Displays a list of leads with filtering, search, and actions.
 */

import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { leadService } from '../../services/leadService';
import { LeadStatusBadge } from './LeadStatusBadge';
import type { components } from '../../types/api.generated';

type LeadResponse = components['schemas']['LeadResponse'];

interface LeadListProps {
  tenantId: string;
}

export const LeadList: React.FC<LeadListProps> = ({ tenantId }) => {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [showHotLeadsOnly, setShowHotLeadsOnly] = useState(false);

  // Fetch leads
  const { data: leads, isLoading, error } = useQuery<LeadResponse[]>({
    queryKey: ['leads', tenantId, statusFilter, showHotLeadsOnly],
    queryFn: async () => {
      if (showHotLeadsOnly) {
        return leadService.getHotLeads(tenantId);
      }
      return leadService.list(tenantId, {
        status: statusFilter || undefined,
        limit: 100,
      });
    },
  });

  // Search leads
  const { data: searchResults } = useQuery<LeadResponse[]>({
    queryKey: ['leads-search', tenantId, searchQuery],
    queryFn: () => leadService.search(tenantId, searchQuery),
    enabled: searchQuery.length > 0,
  });

  const displayLeads = searchQuery.length > 0 ? searchResults : leads;

  const getScoreColor = (score: number): string => {
    if (score >= 61) return 'text-green-600 font-semibold';
    if (score >= 31) return 'text-yellow-600';
    return 'text-gray-600';
  };

  const getScoreLabel = (score: number): string => {
    if (score >= 61) return 'Hot';
    if (score >= 31) return 'Warm';
    return 'Cold';
  };

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

  return (
    <div className="space-y-4">
      {/* Header with actions */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Leads</h2>
        <button
          onClick={() => navigate(`/tenants/${tenantId}/leads/create`)}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md"
        >
          Create Lead
        </button>
      </div>

      {/* Filters and search */}
      <div className="flex gap-4 flex-wrap">
        <input
          type="text"
          placeholder="Search by name, email, or company..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="flex-1 min-w-[300px] px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
        />

        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="">All Statuses</option>
          <option value="new">New</option>
          <option value="contacted">Contacted</option>
          <option value="qualified">Qualified</option>
          <option value="converted">Converted</option>
          <option value="disqualified">Disqualified</option>
        </select>

        <label className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-md bg-white cursor-pointer">
          <input
            type="checkbox"
            checked={showHotLeadsOnly}
            onChange={(e) => setShowHotLeadsOnly(e.target.checked)}
            className="rounded text-blue-600 focus:ring-blue-500"
          />
          <span className="text-sm font-medium text-gray-700">Hot Leads Only</span>
        </label>
      </div>

      {/* Results count */}
      {displayLeads && (
        <div className="text-sm text-gray-600">
          {displayLeads.length} lead{displayLeads.length !== 1 ? 's' : ''} found
        </div>
      )}

      {/* Lead list */}
      {displayLeads && displayLeads.length > 0 ? (
        <div className="bg-white shadow overflow-hidden sm:rounded-md">
          <ul className="divide-y divide-gray-200">
            {displayLeads.map((lead) => (
              <li
                key={lead.id}
                onClick={() => navigate(`/tenants/${tenantId}/leads/${lead.id}`)}
                className="hover:bg-gray-50 cursor-pointer transition-colors"
              >
                <div className="px-4 py-4 sm:px-6">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3">
                        <h3 className="text-lg font-medium text-gray-900">
                          {lead.name}
                        </h3>
                        <LeadStatusBadge status={lead.status} />
                        <span className={`text-sm ${getScoreColor(lead.score)}`}>
                          {lead.score} pts ({getScoreLabel(lead.score)})
                        </span>
                      </div>
                      <div className="mt-2 flex items-center gap-4 text-sm text-gray-500">
                        <span>{lead.email}</span>
                        {lead.company && (
                          <>
                            <span>•</span>
                            <span>{lead.company}</span>
                          </>
                        )}
                        {lead.job_title && (
                          <>
                            <span>•</span>
                            <span>{lead.job_title}</span>
                          </>
                        )}
                      </div>
                      {lead.tags && lead.tags.length > 0 && (
                        <div className="mt-2 flex gap-2">
                          {lead.tags.map((tag, index) => (
                            <span
                              key={index}
                              className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800"
                            >
                              {tag}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                    <div className="text-right text-sm text-gray-500">
                      <div>Created: {new Date(lead.created_at).toLocaleDateString()}</div>
                      {lead.last_contacted_at && (
                        <div>
                          Last contact: {new Date(lead.last_contacted_at).toLocaleDateString()}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        </div>
      ) : (
        <div className="text-center py-12 bg-white rounded-lg border border-gray-200">
          <p className="text-gray-500">No leads found</p>
          <button
            onClick={() => navigate(`/tenants/${tenantId}/leads/create`)}
            className="mt-4 text-blue-600 hover:text-blue-700"
          >
            Create your first lead
          </button>
        </div>
      )}
    </div>
  );
};
