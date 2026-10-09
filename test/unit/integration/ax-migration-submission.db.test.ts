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
import { and, eq, sql } from 'drizzle-orm';
import { drizzle } from 'drizzle-orm/postgres-js';
import postgres from 'postgres';
import { afterAll, beforeAll, describe, expect, it } from 'vitest';

const url = process.env.TEST_DATABASE_URL;

describe.skipIf(!url)('AX migration submission (PostgreSQL)', () => {
  // Several connections so that concurrent submissions really run in parallel
  const client = url ? postgres(url, { max: 4 }) : null;
  const database = client ? drizzle(client, { schema }) : null;
  // biome-ignore lint/style/noNonNullAssertion: guarded by skipIf
  const pg = database!;
  const db = pg as unknown as Parameters<typeof submitAxMigrationDiagnosis>[0];
  let organizationId: string;
  let otherOrganizationId: string;
  const now = new Date('2026-10-09T01:00:00Z');
  const unique = () => `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;

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
    contact: { company: '三田製作所', name: '山田 太郎', email: `Yamada-${unique()}@Example.co.jp` },
    privacyConsent: true,
    consultationRequested: false,
    tracking: { utmSource: 'google', utmMedium: 'cpc', utmCampaign: 'ax-hito' },
    locale: 'ja',
    ...overrides,
  });

  const leadsByEmail = (orgId: string, email: string) =>
    pg
      .select()
      .from(leads)
      .where(and(eq(leads.organizationId, orgId), sql`lower(${leads.email}) = ${email.toLowerCase()}`));

  beforeAll(async () => {
    const created = await pg
      .insert(organizations)
      .values([
        { name: 'AX test', slug: `ax-test-${unique()}` },
        { name: 'AX other', slug: `ax-other-${unique()}` },
      ])
      .returning({ id: organizations.id });
    organizationId = created[0].id;
    otherOrganizationId = created[1].id;
  });

  afterAll(async () => {
    if (organizationId) {
      await pg.delete(organizations).where(eq(organizations.id, organizationId));
      await pg.delete(organizations).where(eq(organizations.id, otherOrganizationId));
    }
    await client?.end();
  });

  it('creates a lead with pipeline fields filled from the diagnosis', async () => {
    const data = input();
    const outcome = await submitAxMigrationDiagnosis(db, organizationId, data, now);
    expect(outcome.ok).toBe(true);
    if (!outcome.ok) return;
    expect(outcome.leadCreated).toBe(true);
    expect(outcome.existingLead).toBeNull();

    const lead = await pg.query.leads.findFirst({ where: eq(leads.id, outcome.leadId) });
    expect(lead).toMatchObject({
      email: data.contact.email.toLowerCase(),
      company: '三田製作所',
      status: 'new',
      source: 'website',
      inflowSource: 'advertising',
      conversionPoint: 'web_diagnosis',
      targetSystem: 'as400',
      score: outcome.result.leadScore,
    });
    // The Web diagnosis counts as the MQL action (2026-10-09 decision)
    expect(lead?.mqlQualifiedAt).toEqual(now);
    expect(lead?.responses).toMatchObject({
      axMigration: { submissionId: outcome.submissionId, mqlCandidate: true, primaryChallenge: 'people' },
    });

    const submission = await pg.query.diagnosticSubmissions.findFirst({
      where: eq(diagnosticSubmissions.id, outcome.submissionId),
    });
    expect(submission).toMatchObject({
      leadId: outcome.leadId,
      leadCreated: true,
      diagnosticKey: 'ax-migration',
      diagnosticVersion: 1,
      tracking: { utmSource: 'google', utmMedium: 'cpc', utmCampaign: 'ax-hito' },
      consultationRequestedAt: null,
    });
  });

  it('never modifies an existing lead from the public form (email is case-insensitive)', async () => {
    const email = `owner-${unique()}@example.co.jp`;
    const [existing] = await pg
      .insert(leads)
      .values({
        organizationId,
        email,
        name: '登録済み 花子',
        company: '登録済み商事',
        status: 'negotiating',
        hasNegotiated: true,
        score: 40,
        inflowSource: 'existing_customer',
        conversionPoint: 'via_sales',
        dealPhase: 'proposal',
        responses: { note: 'keep me' },
      })
      .returning();

    const outcome = await submitAxMigrationDiagnosis(
      db,
      organizationId,
      input({
        contact: { company: '偽名商事', name: '偽名', email: email.toUpperCase() },
        tracking: { ref: 'partner-x' },
        consultationRequested: true,
      }),
      now
    );
    expect(outcome.ok).toBe(true);
    if (!outcome.ok) return;
    expect(outcome.leadCreated).toBe(false);
    expect(outcome.leadId).toBe(existing.id);
    expect(outcome.existingLead).toEqual({ name: '登録済み 花子', company: '登録済み商事', email });

    const [after] = await leadsByEmail(organizationId, email);
    expect(after).toMatchObject({
      name: '登録済み 花子',
      company: '登録済み商事',
      status: 'negotiating',
      score: 40,
      inflowSource: 'existing_customer',
      conversionPoint: 'via_sales',
      dealPhase: 'proposal',
      referrerName: null,
      responses: { note: 'keep me' },
    });

    const submission = await pg.query.diagnosticSubmissions.findFirst({
      where: eq(diagnosticSubmissions.id, outcome.submissionId),
    });
    expect(submission).toMatchObject({ leadId: existing.id, leadCreated: false });
    expect(submission?.consultationRequestedAt).toBeInstanceOf(Date);
  });

  it('creates only one lead when the same email is submitted concurrently', async () => {
    const email = `double-${unique()}@example.jp`;
    const data = input({ contact: { company: '並行商事', name: '並行', email } });
    const outcomes = await Promise.all([
      submitAxMigrationDiagnosis(db, organizationId, data, now),
      submitAxMigrationDiagnosis(db, organizationId, data, now),
      submitAxMigrationDiagnosis(db, organizationId, data, now),
    ]);
    expect(outcomes.every((o) => o.ok)).toBe(true);
    expect(await leadsByEmail(organizationId, email)).toHaveLength(1);
    expect(outcomes.filter((o) => o.ok && o.leadCreated)).toHaveLength(1);
  });

  it('serializes submissions for the same email with an advisory lock', async () => {
    const email = `locked-${unique()}@example.jp`;
    // Hold the same lock from another session, as a concurrent submission would
    const holder = postgres(url as string, { max: 1 });
    await holder`SELECT pg_advisory_lock(hashtextextended(${`${organizationId}:${email}`}, 0))`;

    let settled = false;
    const pending = submitAxMigrationDiagnosis(
      db,
      organizationId,
      input({ contact: { company: 'ロック商事', name: 'ロック', email } }),
      now
    ).then((outcome) => {
      settled = true;
      return outcome;
    });

    await new Promise((resolve) => setTimeout(resolve, 300));
    expect(settled).toBe(false); // still waiting for the lock

    await holder`SELECT pg_advisory_unlock(hashtextextended(${`${organizationId}:${email}`}, 0))`;
    await holder.end();
    const outcome = await pending;
    expect(outcome.ok && outcome.leadCreated).toBe(true);
  });

  it('keeps organizations apart: the same email in another organization is not touched', async () => {
    const email = `tenant-${unique()}@example.jp`;
    await pg.insert(leads).values({ organizationId: otherOrganizationId, email, company: '他社' });

    const outcome = await submitAxMigrationDiagnosis(
      db,
      organizationId,
      input({ contact: { company: '自社', name: '自社', email } }),
      now
    );
    expect(outcome.ok && outcome.leadCreated).toBe(true);
    expect(await leadsByEmail(organizationId, email)).toHaveLength(1);
    const [other] = await leadsByEmail(otherOrganizationId, email);
    expect(other.company).toBe('他社');
  });

  it('rejects invalid answers without writing anything', async () => {
    const count = async () =>
      (
        await pg
          .select()
          .from(diagnosticSubmissions)
          .where(eq(diagnosticSubmissions.organizationId, organizationId))
      ).length;
    const before = await count();
    const outcome = await submitAxMigrationDiagnosis(
      db,
      organizationId,
      input({ answers: { industry: 'manufacturing' } }),
      now
    );
    expect(outcome.ok).toBe(false);
    expect(await count()).toBe(before);
  });

  it('records a consultation request once even when it arrives concurrently', async () => {
    const outcome = await submitAxMigrationDiagnosis(
      db,
      organizationId,
      input({ contact: { company: '品川商事', name: '佐藤', email: `sato-${unique()}@example.jp` } }),
      now
    );
    if (!outcome.ok) throw new Error('submission failed');

    const results = await Promise.all([
      requestAxMigrationConsultation(db, outcome.submissionId),
      requestAxMigrationConsultation(db, outcome.submissionId),
      requestAxMigrationConsultation(db, outcome.submissionId),
    ]);
    const first = results.filter((r) => r.ok && !r.alreadyRequested);
    expect(first).toHaveLength(1);
    expect(first[0]).toMatchObject({ leadId: outcome.leadId, leadCreated: true });

    const lead = await pg.query.leads.findFirst({ where: eq(leads.id, outcome.leadId) });
    expect(lead?.conversionPoint).toBe('consultation');
    expect(lead?.responses).toMatchObject({ axMigration: { consultationRequested: true } });
  });

  it('does not update an existing lead on a consultation request from its email', async () => {
    const email = `existing-consult-${unique()}@example.jp`;
    const [existing] = await pg
      .insert(leads)
      .values({ organizationId, email, conversionPoint: 'document_download' })
      .returning();
    const outcome = await submitAxMigrationDiagnosis(
      db,
      organizationId,
      input({ contact: { company: 'x', name: 'x', email } }),
      now
    );
    if (!outcome.ok) throw new Error('submission failed');

    const result = await requestAxMigrationConsultation(db, outcome.submissionId);
    expect(result).toMatchObject({ ok: true, alreadyRequested: false, leadCreated: false });
    const lead = await pg.query.leads.findFirst({ where: eq(leads.id, existing.id) });
    expect(lead?.conversionPoint).toBe('document_download');
  });

  it('returns not_found for an unknown submission', async () => {
    const result = await requestAxMigrationConsultation(db, '00000000-0000-0000-0000-000000000000');
    expect(result).toEqual({ ok: false, reason: 'not_found' });
  });
});
