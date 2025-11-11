/**
 * Lead Row Component
 * 
 * Individual lead row with:
 * - Hot lead highlighting (score >= 80)
 * - Score badge with color coding
 * - Status badge
 * - Quick actions
 */

import React from 'react';
import { useNavigate } from 'react-router-dom';
import { FlameIcon, MailIcon, PhoneIcon, BuildingIcon } from 'lucide-react';
import { LeadStatusBadge } from './LeadStatusBadge';

interface Lead {
  id: string;
  name: string;
  email: string;
  company?: string;
  job_title?: string;
  phone?: string;
  score: number;
  status: string;
  created_at: string;
  tenant_id?: string;
}

interface LeadRowProps {
  lead: Lead;
  tenantId: string;
}

export function LeadRow({ lead, tenantId }: LeadRowProps) {
  const navigate = useNavigate();
  const isHot = lead.score >= 80;

  const getScoreBadgeColor = (score: number): string => {
    if (score >= 80) return 'bg-red-100 text-red-800 border-red-200';
    if (score >= 60) return 'bg-yellow-100 text-yellow-800 border-yellow-200';
    return 'bg-gray-100 text-gray-600 border-gray-200';
  };

  const handleClick = () => {
    navigate(`/tenants/${tenantId}/leads/${lead.id}`);
  };

  return (
    <tr
      onClick={handleClick}
      className={`
        cursor-pointer transition-colors
        ${isHot 
          ? 'bg-orange-50 hover:bg-orange-100 border-l-4 border-orange-500' 
          : 'hover:bg-gray-50'
        }
      `}
    >
      {/* Hot Lead Icon */}
      <td className="px-4 py-4 whitespace-nowrap w-12">
        {isHot && (
          <FlameIcon className="w-5 h-5 text-orange-500 animate-pulse" />
        )}
      </td>

      {/* Name */}
      <td className="px-4 py-4 whitespace-nowrap">
        <div className="flex items-center gap-2">
          <div className="text-sm font-medium text-gray-900">
            {lead.name}
          </div>
        </div>
      </td>

      {/* Company */}
      <td className="px-4 py-4 whitespace-nowrap">
        <div className="flex items-center gap-2 text-sm text-gray-600">
          {lead.company ? (
            <>
              <BuildingIcon className="w-4 h-4 text-gray-400" />
              <span>{lead.company}</span>
            </>
          ) : (
            <span className="text-gray-400">-</span>
          )}
        </div>
        {lead.job_title && (
          <div className="text-xs text-gray-500 mt-1">{lead.job_title}</div>
        )}
      </td>

      {/* Contact Info */}
      <td className="px-4 py-4 whitespace-nowrap">
        <div className="space-y-1">
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <MailIcon className="w-3 h-3 text-gray-400" />
            <span className="text-xs">{lead.email}</span>
          </div>
          {lead.phone && (
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <PhoneIcon className="w-3 h-3 text-gray-400" />
              <span className="text-xs">{lead.phone}</span>
            </div>
          )}
        </div>
      </td>

      {/* Score */}
      <td className="px-4 py-4 whitespace-nowrap">
        <div className="flex items-center gap-2">
          <span
            className={`
              inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold border
              ${getScoreBadgeColor(lead.score)}
            `}
          >
            {lead.score}
          </span>
          {isHot && (
            <span className="text-xs text-orange-600 font-medium">HOT</span>
          )}
        </div>
      </td>

      {/* Status */}
      <td className="px-4 py-4 whitespace-nowrap">
        <LeadStatusBadge status={lead.status} />
      </td>

      {/* Created Date */}
      <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-600">
        {new Date(lead.created_at).toLocaleDateString('ja-JP', {
          year: 'numeric',
          month: '2-digit',
          day: '2-digit',
        })}
      </td>
    </tr>
  );
}
