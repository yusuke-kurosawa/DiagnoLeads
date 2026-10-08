import { z } from 'zod';
import type { InflowSource } from '../leads/types/pipeline';

/**
 * Tracking parameters captured on the landing page.
 * `ref` is a referral code given to partners / referrers (紹介元).
 */
export const trackingSchema = z
  .object({
    utmSource: z.string().max(100).optional(),
    utmMedium: z.string().max(100).optional(),
    utmCampaign: z.string().max(200).optional(),
    utmContent: z.string().max(200).optional(),
    utmTerm: z.string().max(200).optional(),
    ref: z.string().max(100).optional(),
    referrer: z.string().max(500).optional(),
    landingPath: z.string().max(500).optional(),
  })
  .default({});
export type Tracking = z.infer<typeof trackingSchema>;

const MEDIUM_TO_INFLOW: Record<string, InflowSource> = {
  cpc: 'advertising',
  ppc: 'advertising',
  paid: 'advertising',
  paid_search: 'advertising',
  paid_social: 'advertising',
  display: 'advertising',
  ads: 'advertising',
  retargeting: 'advertising',
  seminar: 'seminar',
  webinar: 'seminar',
  event: 'seminar',
  referral: 'referral_partner',
  partner: 'referral_partner',
  customer: 'existing_customer',
  existing_customer: 'existing_customer',
  executive: 'executive_network',
};

/**
 * Infer the 流入元 of a lead from tracking parameters.
 * Falls back to LP（自然検索） when nothing identifies the channel.
 */
export function inferInflowSource(tracking: Tracking): {
  inflowSource: InflowSource;
  referrerName: string | null;
} {
  const ref = tracking.ref?.trim();
  if (ref) {
    return { inflowSource: 'referral_partner', referrerName: ref };
  }
  const medium = tracking.utmMedium?.trim().toLowerCase();
  if (medium && MEDIUM_TO_INFLOW[medium]) {
    return { inflowSource: MEDIUM_TO_INFLOW[medium], referrerName: null };
  }
  return { inflowSource: 'lp_organic', referrerName: null };
}

/** Drop empty values so only meaningful tracking is stored */
export function compactTracking(tracking: Tracking): Record<string, string> {
  return Object.fromEntries(
    Object.entries(tracking).filter(
      (entry): entry is [string, string] => typeof entry[1] === 'string' && entry[1].trim() !== ''
    )
  );
}
