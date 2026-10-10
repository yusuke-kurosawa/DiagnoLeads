/**
 * Links of the AX migration site.
 * Optional URLs come from environment variables so that marketing can add them without a code
 * change; the corresponding links are hidden while they are not set.
 */
export const AX_SITE_LINKS = {
  operator: 'https://sas-com.com/',
  relatedService: 'https://maru2-dx.com/',
} as const;

/** Privacy policy linked from the consent text and the footer */
export function axPrivacyPolicyUrl(): string | undefined {
  return process.env.NEXT_PUBLIC_AX_PRIVACY_POLICY_URL || undefined;
}

/** Booking page for a consultation without taking the diagnosis (e.g. Microsoft Bookings) */
export function axConsultationUrl(): string | undefined {
  return process.env.NEXT_PUBLIC_AX_CONSULTATION_URL || undefined;
}

/** Section anchors on the landing page */
export const AX_SECTIONS = {
  problems: 'problems',
  steps: 'steps',
  targets: 'targets',
  diagnosis: 'diagnosis',
  faq: 'faq',
} as const;
