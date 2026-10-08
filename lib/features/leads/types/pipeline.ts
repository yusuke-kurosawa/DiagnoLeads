import { z } from 'zod';

/**
 * Sales pipeline definitions shared by DB, API and UI.
 *
 * Based on the AX migration sales & marketing flow (2026-10-08).
 * Labels live in locales/{ja,en}/common.json under the matching namespace.
 */

/** 5-stage lead status: 新規 / ナーチャリング / 商談中 / 成約 / 失注 */
export const LEAD_STATUSES = ['new', 'nurturing', 'negotiating', 'won', 'lost'] as const;
export const leadStatusEnum = z.enum(LEAD_STATUSES);
export type LeadStatus = z.infer<typeof leadStatusEnum>;

/** Statuses that count as "has been in negotiation" (商談済みフラグ) */
export const NEGOTIATED_STATUSES: readonly LeadStatus[] = ['negotiating', 'won'];

/** 流入元 */
export const INFLOW_SOURCES = [
  'existing_customer',
  'referral_partner',
  'executive_network',
  'lp_organic',
  'seminar',
  'advertising',
] as const;
export const inflowSourceEnum = z.enum(INFLOW_SOURCES);
export type InflowSource = z.infer<typeof inflowSourceEnum>;

/** コンバージョンポイント */
export const CONVERSION_POINTS = [
  'consultation',
  'document_download',
  'demo_view',
  'seminar',
  'via_sales',
  'web_diagnosis',
] as const;
export const conversionPointEnum = z.enum(CONVERSION_POINTS);
export type ConversionPoint = z.infer<typeof conversionPointEnum>;

/** 商談フェーズ */
export const DEAL_PHASES = [
  'initial_hearing',
  'simple_diagnosis',
  'proposal',
  'survey_won',
  'migration_won',
  'ax',
] as const;
export const dealPhaseEnum = z.enum(DEAL_PHASES);
export type DealPhase = z.infer<typeof dealPhaseEnum>;

/** 対象システム */
export const TARGET_SYSTEMS = ['as400', 'other_legacy', 'other'] as const;
export const targetSystemEnum = z.enum(TARGET_SYSTEMS);
export type TargetSystem = z.infer<typeof targetSystemEnum>;

/** 失注・保留理由 */
export const LOST_REASONS = [
  'budget',
  'timing',
  'competitor',
  'internal_structure',
  'other',
] as const;
export const lostReasonEnum = z.enum(LOST_REASONS);
export type LostReason = z.infer<typeof lostReasonEnum>;

/** Pipeline fields accepted on lead create / update */
export const leadPipelineFieldsSchema = z.object({
  inflowSource: inflowSourceEnum.nullable().optional(),
  conversionPoint: conversionPointEnum.nullable().optional(),
  dealPhase: dealPhaseEnum.nullable().optional(),
  targetSystem: targetSystemEnum.nullable().optional(),
  referrerName: z.string().max(200).nullable().optional(),
  lostReason: lostReasonEnum.nullable().optional(),
});
export type LeadPipelineFields = z.infer<typeof leadPipelineFieldsSchema>;

/**
 * Derive the negotiated flag when the status changes.
 * The flag never goes back to false once set.
 */
export function deriveHasNegotiated(status: LeadStatus, current = false): boolean {
  return current || NEGOTIATED_STATUSES.includes(status);
}

/**
 * Fields to persist when a lead's status changes.
 * - 商談済みフラグ is set once the lead reaches negotiation and never cleared
 * - SQL qualification date is recorded the first time the lead reaches negotiation
 */
export function buildStatusTransition(
  existing: { hasNegotiated: boolean; sqlQualifiedAt: Date | null },
  nextStatus: LeadStatus,
  now: Date = new Date()
): { status: LeadStatus; hasNegotiated: boolean; sqlQualifiedAt: Date | null } {
  const reachedNegotiation = NEGOTIATED_STATUSES.includes(nextStatus);
  return {
    status: nextStatus,
    hasNegotiated: deriveHasNegotiated(nextStatus, existing.hasNegotiated),
    sqlQualifiedAt: existing.sqlQualifiedAt ?? (reachedNegotiation ? now : null),
  };
}

/** Legacy status values (before #54) mapped to the 5-stage pipeline */
export const LEGACY_LEAD_STATUS_MAP: Record<string, LeadStatus> = {
  contacted: 'nurturing',
  qualified: 'negotiating',
  converted: 'won',
};

/** Normalize a status value, accepting legacy values (e.g. from old CSV exports) */
export function normalizeLeadStatus(value: unknown): unknown {
  if (typeof value !== 'string') return value;
  const trimmed = value.trim().toLowerCase();
  return LEGACY_LEAD_STATUS_MAP[trimmed] ?? trimmed;
}
