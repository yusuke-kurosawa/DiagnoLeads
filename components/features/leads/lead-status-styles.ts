import type { LeadStatus } from '@/lib/features/leads/types';

/** Tailwind badge classes per lead status */
export const LEAD_STATUS_BADGE_CLASSES: Record<LeadStatus, string> = {
  new: 'bg-blue-100 text-blue-800',
  nurturing: 'bg-yellow-100 text-yellow-800',
  negotiating: 'bg-green-100 text-green-800',
  won: 'bg-purple-100 text-purple-800',
  lost: 'bg-gray-100 text-gray-700',
};

/** Chart / badge color names per lead status */
export const LEAD_STATUS_COLORS: Record<
  LeadStatus,
  'blue' | 'yellow' | 'emerald' | 'violet' | 'gray'
> = {
  new: 'blue',
  nurturing: 'yellow',
  negotiating: 'emerald',
  won: 'violet',
  lost: 'gray',
};
