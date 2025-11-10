/**
 * Lead Status Badge Component
 * 
 * Displays lead status with color-coded badges.
 */

import React from 'react';

interface LeadStatusBadgeProps {
  status: string;
}

const statusConfig: Record<string, { label: string; className: string }> = {
  new: {
    label: 'New',
    className: 'bg-blue-100 text-blue-800',
  },
  contacted: {
    label: 'Contacted',
    className: 'bg-yellow-100 text-yellow-800',
  },
  qualified: {
    label: 'Qualified',
    className: 'bg-green-100 text-green-800',
  },
  converted: {
    label: 'Converted',
    className: 'bg-purple-100 text-purple-800',
  },
  disqualified: {
    label: 'Disqualified',
    className: 'bg-gray-100 text-gray-800',
  },
};

export const LeadStatusBadge: React.FC<LeadStatusBadgeProps> = ({ status }) => {
  const config = statusConfig[status] || {
    label: status,
    className: 'bg-gray-100 text-gray-800',
  };

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${config.className}`}
    >
      {config.label}
    </span>
  );
};
