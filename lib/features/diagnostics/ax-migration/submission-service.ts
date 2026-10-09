import type { db as defaultDb } from '@/lib/db/client';
import { type Lead, diagnosticSubmissions, leads } from '@/lib/db/schema';
import { and, asc, eq, isNull, sql } from 'drizzle-orm';
import { z } from 'zod';
import { validateAnswers } from '../engine';
import { type Tracking, compactTracking, inferInflowSource, trackingSchema } from '../tracking';
import type { AnswerValidationIssue, DiagnosticAnswers } from '../types';
import { AX_MIGRATION_DIAGNOSTIC_KEY, axMigrationDefinition } from './definition';
import { type AxMigrationResult, evaluateAxMigration } from './evaluate';

type Database = typeof defaultDb;

export const axMigrationSubmissionSchema = z.object({
  answers: z.record(z.unknown()),
  contact: z.object({
    company: z.string().trim().min(1).max(200),
    name: z.string().trim().min(1).max(100),
    email: z.string().trim().email().max(254),
    phone: z.string().trim().max(30).optional(),
    department: z.string().trim().max(100).optional(),
  }),
  privacyConsent: z.literal(true),
  consultationRequested: z.boolean().default(false),
  tracking: trackingSchema,
  locale: z.enum(['ja', 'en']).default('ja'),
  /** Honeypot: people never fill it. The route answers a filled one with a fake success */
  website: z.string().max(500).optional(),
});
export type AxMigrationSubmissionInput = z.infer<typeof axMigrationSubmissionSchema>;

/** The existing lead as stored in the DB (never taken from the unauthenticated request) */
export interface ExistingLeadSnapshot {
  name: string | null;
  company: string | null;
  email: string;
}

export type SubmitOutcome =
  | {
      ok: true;
      submissionId: string;
      leadId: string;
      leadCreated: boolean;
      /** Set when the email matched an existing lead (identity not verified) */
      existingLead: ExistingLeadSnapshot | null;
      result: AxMigrationResult;
      answers: DiagnosticAnswers;
    }
  | { ok: false; issues: AnswerValidationIssue[] };

/** Summary stored on a lead created by the diagnosis */
function buildLeadSummary(
  submissionId: string,
  result: AxMigrationResult,
  input: AxMigrationSubmissionInput,
  now: Date
) {
  return {
    submissionId,
    diagnosedAt: now.toISOString(),
    difficulty: result.difficulty.level,
    urgency: result.urgency.level,
    primaryChallenge: result.challenges.primary,
    challenges: result.challenges.selected,
    mqlCandidate: result.mql.candidate,
    sqlSignals: result.sqlSignals.candidate,
    needsHearing: result.needsHearing,
    consultationRequested: input.consultationRequested,
    department: input.contact.department ?? null,
  };
}

/**
 * Save an AX migration diagnosis and link it to a lead.
 *
 * - Scores are computed here on the server; nothing from the client is trusted.
 * - The endpoint is unauthenticated, so a matching existing lead is never modified:
 *   the submission is only linked to it and sales is told the identity is unverified.
 *   Only a lead created by this submission gets the diagnosis values.
 * - A transaction-scoped advisory lock on (organization, email) serializes concurrent
 *   submissions for the same address, so a double submit cannot create two leads.
 */
export async function submitAxMigrationDiagnosis(
  database: Database,
  organizationId: string,
  input: AxMigrationSubmissionInput,
  now: Date = new Date()
): Promise<SubmitOutcome> {
  const validation = validateAnswers(axMigrationDefinition, input.answers);
  if (!validation.success) {
    return { ok: false, issues: validation.issues };
  }
  const answers = validation.answers;
  const result = evaluateAxMigration(answers);
  const tracking: Tracking = input.tracking ?? {};
  const inflow = inferInflowSource(tracking);
  const email = input.contact.email.toLowerCase();

  return database.transaction(async (tx) => {
    await tx.execute(
      sql`SELECT pg_advisory_xact_lock(hashtextextended(${`${organizationId}:${email}`}, 0))`
    );

    const existing: Lead | undefined = await tx.query.leads.findFirst({
      where: and(eq(leads.organizationId, organizationId), sql`lower(${leads.email}) = ${email}`),
      orderBy: [asc(leads.createdAt)],
    });

    let leadId: string;
    if (existing) {
      leadId = existing.id;
    } else {
      const [created] = await tx
        .insert(leads)
        .values({
          organizationId,
          email,
          name: input.contact.name,
          company: input.contact.company,
          phone: input.contact.phone || null,
          status: 'new',
          score: result.leadScore,
          source: 'website',
          inflowSource: inflow.inflowSource,
          referrerName: inflow.referrerName,
          conversionPoint: input.consultationRequested ? 'consultation' : 'web_diagnosis',
          targetSystem: result.targetSystem,
          mqlQualifiedAt: result.mql.qualified ? now : null,
          createdAt: now,
          updatedAt: now,
        })
        .returning({ id: leads.id });
      leadId = created.id;
    }

    const [submission] = await tx
      .insert(diagnosticSubmissions)
      .values({
        organizationId,
        leadId,
        leadCreated: !existing,
        diagnosticKey: AX_MIGRATION_DIAGNOSTIC_KEY,
        diagnosticVersion: axMigrationDefinition.version,
        answers,
        result: result as unknown as Record<string, unknown>,
        tracking: compactTracking(tracking),
        locale: input.locale,
        consultationRequestedAt: input.consultationRequested ? now : null,
        createdAt: now,
      })
      .returning({ id: diagnosticSubmissions.id });

    if (!existing) {
      await tx
        .update(leads)
        .set({ responses: { axMigration: buildLeadSummary(submission.id, result, input, now) } })
        .where(eq(leads.id, leadId));
    }

    return {
      ok: true as const,
      submissionId: submission.id,
      leadId,
      leadCreated: !existing,
      existingLead: existing
        ? { name: existing.name, company: existing.company, email: existing.email }
        : null,
      result,
      answers,
    };
  });
}

/**
 * Record a consultation request made from the result page.
 * Exactly one concurrent request wins (conditional UPDATE), so sales is notified once.
 * The lead is updated only when it was created by this submission.
 */
export async function requestAxMigrationConsultation(
  database: Database,
  submissionId: string,
  now: Date = new Date()
): Promise<
  | {
      ok: true;
      alreadyRequested: boolean;
      organizationId: string;
      leadId: string | null;
      leadCreated: boolean;
    }
  | { ok: false; reason: 'not_found' }
> {
  return database.transaction(async (tx) => {
    const [claimed] = await tx
      .update(diagnosticSubmissions)
      .set({ consultationRequestedAt: now })
      .where(
        and(
          eq(diagnosticSubmissions.id, submissionId),
          eq(diagnosticSubmissions.diagnosticKey, AX_MIGRATION_DIAGNOSTIC_KEY),
          isNull(diagnosticSubmissions.consultationRequestedAt)
        )
      )
      .returning({
        organizationId: diagnosticSubmissions.organizationId,
        leadId: diagnosticSubmissions.leadId,
        leadCreated: diagnosticSubmissions.leadCreated,
      });

    if (!claimed) {
      const submission = await tx.query.diagnosticSubmissions.findFirst({
        where: and(
          eq(diagnosticSubmissions.id, submissionId),
          eq(diagnosticSubmissions.diagnosticKey, AX_MIGRATION_DIAGNOSTIC_KEY)
        ),
      });
      if (!submission) return { ok: false as const, reason: 'not_found' as const };
      return {
        ok: true as const,
        alreadyRequested: true,
        organizationId: submission.organizationId,
        leadId: submission.leadId,
        leadCreated: submission.leadCreated,
      };
    }

    if (claimed.leadId && claimed.leadCreated) {
      await tx
        .update(leads)
        .set({
          conversionPoint: 'consultation',
          responses: sql`jsonb_set(
            coalesce(${leads.responses}, '{}'::jsonb),
            '{axMigration}',
            coalesce(${leads.responses} -> 'axMigration', '{}'::jsonb) || '{"consultationRequested": true}'::jsonb,
            true
          )`,
          updatedAt: now,
        })
        .where(eq(leads.id, claimed.leadId));
    }

    return {
      ok: true as const,
      alreadyRequested: false,
      organizationId: claimed.organizationId,
      leadId: claimed.leadId,
      leadCreated: claimed.leadCreated,
    };
  });
}
