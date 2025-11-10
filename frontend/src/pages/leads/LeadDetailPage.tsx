/**
 * Lead Detail Page
 * 
 * Displays detailed information about a lead with actions.
 */

import React, { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useAuthStore } from '../../store/authStore';
import { leadService } from '../../services/leadService';
import { LeadStatusBadge } from '../../components/leads/LeadStatusBadge';

export const LeadDetailPage: React.FC = () => {
  const { leadId } = useParams<{ leadId: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { user } = useAuthStore();
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  const { data: lead, isLoading, error } = useQuery({
    queryKey: ['leads', user?.tenant_id, leadId],
    queryFn: () => {
      if (!user?.tenant_id || !leadId) throw new Error('Missing required parameters');
      return leadService.getById(user.tenant_id, leadId);
    },
    enabled: !!user?.tenant_id && !!leadId,
  });

  const deleteMutation = useMutation({
    mutationFn: () => {
      if (!user?.tenant_id || !leadId) throw new Error('Missing required parameters');
      return leadService.delete(user.tenant_id, leadId);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['leads'] });
      navigate(`/tenants/${user?.tenant_id}/leads`);
    },
  });

  const handleDelete = () => {
    deleteMutation.mutate();
  };

  const getScoreColor = (score: number): string => {
    if (score >= 61) return 'text-green-600';
    if (score >= 31) return 'text-yellow-600';
    return 'text-gray-600';
  };

  const getScoreLabel = (score: number): string => {
    if (score >= 61) return 'Hot Lead';
    if (score >= 31) return 'Warm Lead';
    return 'Cold Lead';
  };

  if (!user || !user.tenant_id) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-gray-500">Please log in to view lead details</div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-gray-500">Loading lead...</div>
      </div>
    );
  }

  if (error || !lead) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          Error: {error ? (error as Error).message : 'Lead not found'}
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-6">
        <button
          onClick={() => navigate(`/tenants/${user.tenant_id}/leads`)}
          className="text-blue-600 hover:text-blue-700 mb-4"
        >
          ← Back to Leads
        </button>
        
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{lead.name}</h1>
            <div className="mt-2 flex items-center gap-3">
              <LeadStatusBadge status={lead.status} />
              <span className={`text-lg font-semibold ${getScoreColor(lead.score)}`}>
                {lead.score} / 100 - {getScoreLabel(lead.score)}
              </span>
            </div>
          </div>

          <div className="flex gap-3">
            <button
              onClick={() => navigate(`/tenants/${user.tenant_id}/leads/${leadId}/edit`)}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              Edit
            </button>
            <button
              onClick={() => setShowDeleteConfirm(true)}
              className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
            >
              Delete
            </button>
          </div>
        </div>
      </div>

      {/* Delete Confirmation */}
      {showDeleteConfirm && (
        <div className="mb-6 bg-red-50 border border-red-200 p-4 rounded-md">
          <p className="text-red-800 font-medium mb-3">
            Are you sure you want to delete this lead? This action cannot be undone.
          </p>
          <div className="flex gap-3">
            <button
              onClick={handleDelete}
              disabled={deleteMutation.isPending}
              className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 disabled:opacity-50"
            >
              {deleteMutation.isPending ? 'Deleting...' : 'Yes, Delete'}
            </button>
            <button
              onClick={() => setShowDeleteConfirm(false)}
              className="px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Info */}
        <div className="lg:col-span-2 space-y-6">
          {/* Contact Information */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Contact Information</h2>
            <dl className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <dt className="text-sm font-medium text-gray-500">Email</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  <a href={`mailto:${lead.email}`} className="text-blue-600 hover:text-blue-700">
                    {lead.email}
                  </a>
                </dd>
              </div>
              
              {lead.phone && (
                <div>
                  <dt className="text-sm font-medium text-gray-500">Phone</dt>
                  <dd className="mt-1 text-sm text-gray-900">
                    <a href={`tel:${lead.phone}`} className="text-blue-600 hover:text-blue-700">
                      {lead.phone}
                    </a>
                  </dd>
                </div>
              )}

              {lead.company && (
                <div>
                  <dt className="text-sm font-medium text-gray-500">Company</dt>
                  <dd className="mt-1 text-sm text-gray-900">{lead.company}</dd>
                </div>
              )}

              {lead.job_title && (
                <div>
                  <dt className="text-sm font-medium text-gray-500">Job Title</dt>
                  <dd className="mt-1 text-sm text-gray-900">{lead.job_title}</dd>
                </div>
              )}
            </dl>
          </div>

          {/* Notes */}
          {lead.notes && (
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Notes</h2>
              <p className="text-sm text-gray-700 whitespace-pre-wrap">{lead.notes}</p>
            </div>
          )}

          {/* Tags */}
          {lead.tags && lead.tags.length > 0 && (
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Tags</h2>
              <div className="flex flex-wrap gap-2">
                {lead.tags.map((tag, index) => (
                  <span
                    key={index}
                    className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Score Card */}
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Lead Score</h3>
            <div className="text-center">
              <div className={`text-5xl font-bold ${getScoreColor(lead.score)}`}>
                {lead.score}
              </div>
              <div className="mt-2 text-sm text-gray-600">{getScoreLabel(lead.score)}</div>
              <div className="mt-4 w-full bg-gray-200 rounded-full h-2">
                <div
                  className={`h-2 rounded-full ${
                    lead.score >= 61
                      ? 'bg-green-600'
                      : lead.score >= 31
                      ? 'bg-yellow-600'
                      : 'bg-gray-600'
                  }`}
                  style={{ width: `${lead.score}%` }}
                />
              </div>
            </div>
          </div>

          {/* Activity */}
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Activity</h3>
            <dl className="space-y-3">
              <div>
                <dt className="text-sm font-medium text-gray-500">Created</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {new Date(lead.created_at).toLocaleDateString()}
                </dd>
              </div>
              
              <div>
                <dt className="text-sm font-medium text-gray-500">Last Updated</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {new Date(lead.updated_at).toLocaleDateString()}
                </dd>
              </div>

              {lead.last_contacted_at && (
                <div>
                  <dt className="text-sm font-medium text-gray-500">Last Contacted</dt>
                  <dd className="mt-1 text-sm text-gray-900">
                    {new Date(lead.last_contacted_at).toLocaleDateString()}
                  </dd>
                </div>
              )}

              {lead.last_activity_at && (
                <div>
                  <dt className="text-sm font-medium text-gray-500">Last Activity</dt>
                  <dd className="mt-1 text-sm text-gray-900">
                    {new Date(lead.last_activity_at).toLocaleDateString()}
                  </dd>
                </div>
              )}
            </dl>
          </div>
        </div>
      </div>
    </div>
  );
};
