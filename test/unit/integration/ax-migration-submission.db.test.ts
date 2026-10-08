/**
 * AX migration submission against a real PostgreSQL database.
 *
 * Skipped unless TEST_DATABASE_URL points to a database with the drizzle migrations applied:
 *   TEST_DATABASE_URL=postgres://postgres:postgres@127.0.0.1:55432/dl_test \
 *     bunx vitest --run test/unit/integration/ax-migration-submission.db.test.ts
 */
import * as schema from '@/lib/db/schema';
import { diagnosticSubmissions, leads, organizations } from '@/lib/db/schema';
import {
  type AxMigrationSubmissionInput,
  requestAxMigrationConsultation,
  submitAxMigrationDiagnosis,
} from '@/lib/features/diagnostics/ax-migration/submission-service';
import { eq } from 'drizzle-orm';
import { drizzle } from 'drizzle-orm/postgres-js';
import postgres from 'postgres';
import { afterAll, beforeAll, describe, expect, it } from 'vitest';

const url = process.env.TEST_DATABASE_URL;

describe.skipIf(!url)('AX migration submission (PostgreSQL)', () => {
  const client = url ? postgres(url, { max: 1 }) : null;
  const database = client ? drizzle(client, { schema }) : null;
  // biome-ignore lint/style/noNonNullAssertion: guarded by skipIf
  const db = database! as unknown as Parameters<typeof submitAxMigrationDiagnosis>[0];
  let organizationId: string;

  const input = (overrides: Partial<AxMigrationSubmissionInput> = {}): AxMigrationSubmissionInput => ({
    answers: {
      industry: 'manufacturing',
      revenue: '10b_30b',
      system: 'as400',
      languages: ['rpg', 'cl'],
      years: 'gte20',
      programs: '500_2000',
      integrations: 'some',
      maintenance: 'few',
      documents: 'partial',
      challenges: ['people', 'cost'],
      timeline: '1_2y',
      role: 'it_manager',
    },
    contact: { company: '三田製作所', name: '山田 太郎', email: 'Yamada@Example.co.jp' },
    privacyConsent: true,
    consultationRequested: false,
    tracking: { utmSource: 'google', utmMedium: 'cpc', utmCampaign: 'ax-hito' },
    locale: 'ja',
    ...overrides,
  });

  beforeAll(async () => {
    const [org] = await database!
      .insert(organizations)
      .values({ name: 'AX test', slug: `ax-test-${Date.now()}` })
      .returning({ id: organizations.id });
    organizationId = org.id;
  });

  afterAll(async () => {
    if (database && organizationId) {
      await database.delete(organizations).where(eq(organizations.id, organizationId));
    }
    await client?.end();
  });

  it('creates a lead with pipeline fields filled from the diagnosis', async () => {
    const outcome = await submitAxMigrationDiagnosis(db, organizationId, input());
    expect(outcome.ok).toBe(true);
    if (!outcome.ok) return;
    expect(outcome.leadCreated).toBe(true);

    const lead = await database!.query.leads.findFirst({ where: eq(leads.id, outcome.leadId) });
    expect(lead).toMatchObject({
      email: 'yamada@example.co.jp',
      company: '三田製作所',
      status: 'new',
      source: 'website',
      inflowSource: 'advertising',
      conversionPoint: 'web_diagnosis',
      targetSystem: 'as400',
      score: outcome.result.leadScore,
    });
    expect(lead?.mqlQualifiedAt).toBeInstanceOf(Date);
    expect(lead?.responses).toMatchObject({
      axMigration: { submissionId: outcome.submissionId, mql: true, primaryChallenge: 'people' },
    });

    const submission = await database!.query.diagnosticSubmissions.findFirst({
      where: eq(diagnosticSubmissions.id, outcome.submissionId),
    });
    expect(submission).toMatchObject({
      leadId: outcome.leadId,
      diagnosticKey: 'ax-migration',
      diagnosticVersion: 1,
      tracking: { utmSource: 'google', utmMedium: 'cpc', utmCampaign: 'ax-hito' },
      consultationRequestedAt: null,
    });
  });

  it('updates the same lead when the person answers again (email is case-insensitive)', async () => {
    const outcome = await submitAxMigrationDiagnosis(
      db,
      organizationId,
      input({
        contact: { company: '別名', name: '別名', email: 'yamada@example.co.jp' },
        answers: { ...input().answers, industry: 'other', timeline: 'undecided' },
        tracking: { ref: 'partner-x' },
        consultationRequested: true,
      })
    );
    expect(outcome.ok).toBe(true);
    if (!outcome.ok) return;
    expect(outcome.leadCreated).toBe(false);

    const rows = await database!.select().from(leads).where(eq(leads.organizationId, organizationId));
    expect(rows).toHaveLength(1);
    const [lead] = rows;
    // First values are kept, the higher score wins, a consultation request takes over
    expect(lead.company).toBe('三田製作所');
    expect(lead.inflowSource).toBe('advertising');
    expect(lead.conversionPoint).toBe('consultation');
    expect(lead.score).toBeGreaterThan(outcome.result.leadScore);
    expect(lead.mqlQualifiedAt).toBeInstanceOf(Date);
  });

  it('rejects invalid answers without writing anything', async () => {
    const before = await database!
      .select()
      .from(diagnosticSubmissions)
      .where(eq(diagnosticSubmissions.organizationId, organizationId));
    const outcome = await submitAxMigrationDiagnosis(
      db,
      organizationId,
      input({ answers: { industry: 'manufacturing' } })
    );
    expect(outcome.ok).toBe(false);
    const after = await database!
      .select()
      .from(diagnosticSubmissions)
      .where(eq(diagnosticSubmissions.organizationId, organizationId));
    expect(after).toHaveLength(before.length);
  });

  it('records a consultation request from the result page once', async () => {
    const outcome = await submitAxMigrationDiagnosis(
      db,
      organizationId,
      input({ contact: { company: '品川商事', name: '佐藤', email: 'sato@example.jp' } })
    );
    if (!outcome.ok) throw new Error('submission failed');

    const first = await requestAxMigrationConsultation(db, outcome.submissionId);
    const second = await requestAxMigrationConsultation(db, outcome.submissionId);
    expect(first).toMatchObject({ ok: true, alreadyRequested: false, leadId: outcome.leadId });
    expect(second).toMatchObject({ ok: true, alreadyRequested: true });

    const lead = await database!.query.leads.findFirst({ where: eq(leads.id, outcome.leadId) });
    expect(lead?.conversionPoint).toBe('consultation');
    expect(lead?.responses).toMatchObject({ axMigration: { consultationRequested: true } });
  });

  it('returns not_found for an unknown submission', async () => {
    const result = await requestAxMigrationConsultation(db, '00000000-0000-0000-0000-000000000000');
    expect(result).toEqual({ ok: false, reason: 'not_found' });
  });
});
