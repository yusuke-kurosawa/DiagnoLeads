/**
 * Reports Page
 *
 * Main page for managing custom reports.
 */

import React from 'react';
import { useAuthStore } from '../../store/authStore';
import { ReportList } from '../../components/reports/ReportList';

export const ReportsPage: React.FC = () => {
  const { user } = useAuthStore();

  if (!user || !user.tenant_id) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-gray-500">Please log in to view reports</div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Custom Reports</h1>
        <p className="mt-2 text-sm text-gray-600">
          Create, manage, and export custom reports for your data analytics needs
        </p>
      </div>
      <ReportList tenantId={user.tenant_id} />
    </div>
  );
};
