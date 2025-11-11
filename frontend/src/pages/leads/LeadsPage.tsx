/**
 * Leads Page
 * 
 * Main page for displaying lead list.
 */

import React from 'react';
import { useAuthStore } from '../../store/authStore';
import { LeadList } from '../../components/leads/LeadList';
import { Layout } from '../../components/layout/Layout';

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
    <Layout>
      <div className="max-w-7xl mx-auto">
        <LeadList tenantId={user.tenant_id} />
      </div>
    </Layout>
  );
};
