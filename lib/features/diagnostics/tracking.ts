import { z } from 'zod';
import type { InflowSource } from '../leads/types/pipeline';

/**
 * Tracking parameters captured on the landing page.
 * `ref` is a referral code given to partners / referrers (紹介元).
 */
/** Long values are cut instead of rejected so a long UTM never blocks a submission */
const clipped = (max: number) =>
  z
    .string()
    .transform((value) => value.slice(0, max))
    .optional();

export const trackingSchema = z
  .object({
    utmSource: clipped(200),
    utmMedium: clipped(200),
    utmCampaign: clipped(200),
    utmContent: clipped(200),
    utmTerm: clipped(200),
    ref: clipped(100),
    referrer: clipped(500),
    landingPath: clipped(500),
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
  organic: 'lp_organic',
};

/**
 * Infer the 流入元 of a lead from tracking parameters.
 * - referral code → 紹介・パートナー（the code is kept as 紹介元 for sales to confirm）
 * - known utm_medium → mapped channel
 * - no campaign parameters at all → LP（自然検索）
 * - unknown utm_medium (email, dm, form, ...) → null, so outbound campaigns are not
 *   mixed into organic traffic; sales sets the right value
 */
export function inferInflowSource(tracking: Tracking): {
  inflowSource: InflowSource | null;
  referrerName: string | null;
} {
  const ref = tracking.ref?.trim();
  if (ref) {
    return { inflowSource: 'referral_partner', referrerName: ref };
  }
  const medium = tracking.utmMedium?.trim().toLowerCase();
  if (!medium) {
    return { inflowSource: 'lp_organic', referrerName: null };
  }
  return { inflowSource: MEDIUM_TO_INFLOW[medium] ?? null, referrerName: null };
}

/** Drop empty values so only meaningful tracking is stored */
export function compactTracking(tracking: Tracking): Record<string, string> {
  return Object.fromEntries(
    Object.entries(tracking).filter(
      (entry): entry is [string, string] => typeof entry[1] === 'string' && entry[1].trim() !== ''
    )
  );
}
