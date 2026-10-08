import {
  LEAD_STATUSES,
  buildStatusTransition,
  deriveHasNegotiated,
  leadPipelineFieldsSchema,
  normalizeLeadStatus,
} from '@/lib/features/leads/types/pipeline';
import { describe, expect, it } from 'vitest';

describe('LEAD_STATUSES', () => {
  it('defines the 5-stage pipeline in order', () => {
    expect(LEAD_STATUSES).toEqual(['new', 'nurturing', 'negotiating', 'won', 'lost']);
  });
});

describe('deriveHasNegotiated', () => {
  it('turns on when the lead reaches negotiation or is won', () => {
    expect(deriveHasNegotiated('negotiating')).toBe(true);
    expect(deriveHasNegotiated('won')).toBe(true);
  });

  it('stays off for earlier stages', () => {
    expect(deriveHasNegotiated('new')).toBe(false);
    expect(deriveHasNegotiated('nurturing')).toBe(false);
  });

  it('never goes back to false once set', () => {
    expect(deriveHasNegotiated('lost', true)).toBe(true);
    expect(deriveHasNegotiated('nurturing', true)).toBe(true);
  });
});

describe('buildStatusTransition', () => {
  const now = new Date('2026-10-09T00:00:00Z');
  const fresh = { hasNegotiated: false, sqlQualifiedAt: null };

  it('records the SQL date the first time the lead reaches negotiation', () => {
    expect(buildStatusTransition(fresh, 'negotiating', now)).toEqual({
      status: 'negotiating',
      hasNegotiated: true,
      sqlQualifiedAt: now,
    });
  });

  it('keeps the original SQL date on later transitions', () => {
    const earlier = new Date('2026-09-01T00:00:00Z');
    const result = buildStatusTransition(
      { hasNegotiated: true, sqlQualifiedAt: earlier },
      'won',
      now
    );
    expect(result.sqlQualifiedAt).toBe(earlier);
  });

  it('does not set the SQL date for nurturing or lost before negotiation', () => {
    expect(buildStatusTransition(fresh, 'nurturing', now).sqlQualifiedAt).toBeNull();
    expect(buildStatusTransition(fresh, 'lost', now)).toEqual({
      status: 'lost',
      hasNegotiated: false,
      sqlQualifiedAt: null,
    });
  });

  it('keeps the negotiated flag when a negotiated lead is lost', () => {
    const result = buildStatusTransition({ hasNegotiated: true, sqlQualifiedAt: now }, 'lost');
    expect(result.hasNegotiated).toBe(true);
  });
});

describe('normalizeLeadStatus', () => {
  it('maps legacy values', () => {
    expect(normalizeLeadStatus('contacted')).toBe('nurturing');
    expect(normalizeLeadStatus('qualified')).toBe('negotiating');
    expect(normalizeLeadStatus('converted')).toBe('won');
  });

  it('trims and lowercases current values', () => {
    expect(normalizeLeadStatus(' Won ')).toBe('won');
  });

  it('passes non-string values through', () => {
    expect(normalizeLeadStatus(undefined)).toBeUndefined();
  });
});

describe('leadPipelineFieldsSchema', () => {
  it('accepts the sales flow values', () => {
    const result = leadPipelineFieldsSchema.parse({
      inflowSource: 'referral_partner',
      conversionPoint: 'web_diagnosis',
      dealPhase: 'simple_diagnosis',
      targetSystem: 'as400',
      referrerName: 'Partner Inc.',
      lostReason: null,
    });
    expect(result.dealPhase).toBe('simple_diagnosis');
    expect(result.lostReason).toBeNull();
  });

  it('rejects unknown values', () => {
    expect(() => leadPipelineFieldsSchema.parse({ dealPhase: 'closing' })).toThrow();
    expect(() => leadPipelineFieldsSchema.parse({ targetSystem: 'windows' })).toThrow();
  });
});
