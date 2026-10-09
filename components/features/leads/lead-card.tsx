'use client';

import { Card } from '@/components/ui/card';
import type { Lead } from '@/lib/db/schema';
import type { LeadStatus } from '@/lib/features/leads/types';
import { formatDistance } from 'date-fns';
import { ja } from 'date-fns/locale';
import { useTranslations } from 'next-intl';
import { LEAD_STATUS_BADGE_CLASSES } from './lead-status-styles';

interface LeadCardProps {
  lead: Lead;
  onClick?: () => void;
}

/**
 * Lead card component
 * Displays lead information in a card format
 */
export function LeadCard({ lead, onClick }: LeadCardProps) {
  const tStatus = useTranslations('status');
  const status = lead.status as LeadStatus;

  return (
    <Card className="p-4 hover:shadow-md transition-shadow cursor-pointer" onClick={onClick}>
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <h3 className="font-semibold text-lg">{lead.name || '名前未設定'}</h3>
            <span
              className={`px-2 py-1 rounded-full text-xs font-medium ${
                LEAD_STATUS_BADGE_CLASSES[status] ?? ''
              }`}
            >
              {tStatus(status)}
            </span>
          </div>

          <div className="text-sm text-gray-600 space-y-1">
            <div className="flex items-center gap-2">
              <span className="font-medium">メール:</span>
              <span>{lead.email}</span>
            </div>

            {lead.company && (
              <div className="flex items-center gap-2">
                <span className="font-medium">会社:</span>
                <span>{lead.company}</span>
              </div>
            )}

            {lead.phone && (
              <div className="flex items-center gap-2">
                <span className="font-medium">電話:</span>
                <span>{lead.phone}</span>
              </div>
            )}

            {lead.source && (
              <div className="flex items-center gap-2">
                <span className="font-medium">ソース:</span>
                <span className="capitalize">{lead.source}</span>
              </div>
            )}
          </div>
        </div>

        <div className="text-right">
          {lead.score !== null && lead.score !== undefined && (
            <div className="mb-2">
              <span className="text-2xl font-bold text-blue-600">{lead.score}</span>
              <span className="text-sm text-gray-500 ml-1">点</span>
            </div>
          )}

          <div className="text-xs text-gray-500">
            {formatDistance(new Date(lead.createdAt), new Date(), {
              addSuffix: true,
              locale: ja,
            })}
          </div>
        </div>
      </div>
    </Card>
  );
}
