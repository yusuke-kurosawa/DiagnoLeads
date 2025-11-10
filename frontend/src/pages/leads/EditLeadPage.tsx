/**
 * Edit Lead Page
 * 
 * Page for editing an existing lead.
 */

import React from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useAuthStore } from '../../store/authStore';
import { leadService } from '../../services/leadService';
import { LeadForm } from '../../components/leads/LeadForm';
import type { components } from '../../types/api.generated';

type LeadCreate = components['schemas']['LeadCreate'];

export const EditLeadPage: React.FC = () => {
  const { leadId } = useParams<{ leadId: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { user } = useAuthStore();

  const { data: lead, isLoading, error } = useQuery({
    queryKey: ['leads', user?.tenant_id, leadId],
    queryFn: () => {
      if (!user?.tenant_id || !leadId) throw new Error('Missing required parameters');
      return leadService.getById(user.tenant_id, leadId);
    },
    enabled: !!user?.tenant_id && !!leadId,
  });

  const updateMutation = useMutation({
    mutationFn: (data: LeadCreate) => {
      if (!user?.tenant_id || !leadId) throw new Error('Missing required parameters');
      return leadService.update(user.tenant_id, leadId, data);
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['leads'] });
      navigate(`/tenants/${user?.tenant_id}/leads/${data.id}`);
    },
  });

  const handleSubmit = (data: LeadCreate) => {
    updateMutation.mutate(data);
  };

  const handleCancel = () => {
    navigate(`/tenants/${user?.tenant_id}/leads/${leadId}`);
  };

  if (!user || !user.tenant_id) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-gray-500">Please log in to edit a lead</div>
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
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          Error: {error ? (error as Error).message : 'Lead not found'}
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Edit Lead</h1>
        <p className="mt-2 text-sm text-gray-600">
          Update lead information
        </p>
      </div>

      <div className="bg-white shadow rounded-lg p-6">
        {updateMutation.error && (
          <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            {(updateMutation.error as Error).message}
          </div>
        )}

        <LeadForm
          initialData={lead}
          onSubmit={handleSubmit}
          onCancel={handleCancel}
          isSubmitting={updateMutation.isPending}
        />
      </div>
    </div>
  );
};
