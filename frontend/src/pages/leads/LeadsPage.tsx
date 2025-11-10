/**
 * Leads Page
 * 
 * Main page for displaying lead list.
 */

import React from 'react';
import { useAuthStore } from '../../store/authStore';
import { LeadList } from '../../components/leads/LeadList';

export const LeadsPage: React.FC = () => {
  const { user } = useAuthStore();

  if (!user || !user.tenant_id) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-gray-500">Please log in to view leads</div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <LeadList tenantId={user.tenant_id} />
    </div>
  );
};
