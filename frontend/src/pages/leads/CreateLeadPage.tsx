/**
 * Create Lead Page
 * 
 * Page for creating a new lead.
 */

import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useAuthStore } from '../../store/authStore';
import { leadService } from '../../services/leadService';
import { LeadForm } from '../../components/leads/LeadForm';
import type { components } from '../../types/api.generated';

type LeadCreate = components['schemas']['LeadCreate'];

export const CreateLeadPage: React.FC = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { user } = useAuthStore();

  const createMutation = useMutation({
    mutationFn: (data: LeadCreate) => {
      if (!user?.tenant_id) throw new Error('Tenant ID not found');
      return leadService.create(user.tenant_id, data);
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['leads'] });
      navigate(`/tenants/${user?.tenant_id}/leads/${data.id}`);
    },
  });

  const handleSubmit = (data: LeadCreate) => {
    createMutation.mutate(data);
  };

  const handleCancel = () => {
    navigate(`/tenants/${user?.tenant_id}/leads`);
  };

  if (!user || !user.tenant_id) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-gray-500">Please log in to create a lead</div>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Create New Lead</h1>
        <p className="mt-2 text-sm text-gray-600">
          Add a new lead to your sales pipeline
        </p>
      </div>

      <div className="bg-white shadow rounded-lg p-6">
        {createMutation.error && (
          <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            {(createMutation.error as Error).message}
          </div>
        )}

        <LeadForm
          onSubmit={handleSubmit}
          onCancel={handleCancel}
          isSubmitting={createMutation.isPending}
        />
      </div>
    </div>
  );
};
