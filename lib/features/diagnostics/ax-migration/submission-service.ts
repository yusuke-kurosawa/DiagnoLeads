import type { db as defaultDb } from '@/lib/db/client';
import { type Lead, diagnosticSubmissions, leads } from '@/lib/db/schema';
import { and, eq, sql } from 'drizzle-orm';
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
  /** Honeypot: must stay empty (bots fill every field) */
  website: z.string().max(0).optional(),
});
export type AxMigrationSubmissionInput = z.infer<typeof axMigrationSubmissionSchema>;

export type SubmitOutcome =
  | {
      ok: true;
      submissionId: string;
      leadId: string;
      leadCreated: boolean;
      result: AxMigrationResult;
      answers: DiagnosticAnswers;
    }
  | { ok: false; issues: AnswerValidationIssue[] };

/** Summary stored on leads.responses so sales can see the latest diagnosis on the lead */
function buildLeadSummary(
  submissionId: string,
  result: AxMigrationResult,
  input: AxMigrationSubmissionInput
) {
  return {
    submissionId,
    diagnosedAt: new Date().toISOString(),
    difficulty: result.difficulty.level,
    urgency: result.urgency.level,
    primaryChallenge: result.challenges.primary,
    challenges: result.challenges.selected,
    mql: result.mql.qualified,
    sqlCandidate: result.sqlSignals.candidate,
    consultationRequested: input.consultationRequested,
    department: input.contact.department ?? null,
  };
}

/**
 * Save an AX migration diagnosis and create or update the lead.
 * Scores are computed here on the server; nothing from the client is trusted.
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
  const conversionPoint = input.consultationRequested ? 'consultation' : 'web_diagnosis';

  return database.transaction(async (tx) => {
    const [submission] = await tx
      .insert(diagnosticSubmissions)
      .values({
        organizationId,
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

    const summary = buildLeadSummary(submission.id, result, input);

    const existing: Lead | undefined = await tx.query.leads.findFirst({
      where: and(eq(leads.organizationId, organizationId), sql`lower(${leads.email}) = ${email}`),
    });

    let leadId: string;
    if (existing) {
      const [updated] = await tx
        .update(leads)
        .set({
          name: existing.name || input.contact.name,
          company: existing.company || input.contact.company,
          phone: existing.phone || input.contact.phone || null,
          // Keep the higher score when the same person answers again
          score: Math.max(existing.score ?? 0, result.leadScore),
          inflowSource: existing.inflowSource ?? inflow.inflowSource,
          referrerName: existing.referrerName ?? inflow.referrerName,
          // A consultation request always wins; otherwise keep the first conversion point
          conversionPoint: input.consultationRequested
            ? 'consultation'
            : (existing.conversionPoint ?? conversionPoint),
          targetSystem: existing.targetSystem ?? result.targetSystem,
          mqlQualifiedAt: existing.mqlQualifiedAt ?? (result.mql.qualified ? now : null),
          responses: { ...(existing.responses ?? {}), axMigration: summary },
          updatedAt: now,
        })
        .where(eq(leads.id, existing.id))
        .returning({ id: leads.id });
      leadId = updated.id;
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
          conversionPoint,
          targetSystem: result.targetSystem,
          mqlQualifiedAt: result.mql.qualified ? now : null,
          responses: { axMigration: summary },
          createdAt: now,
          updatedAt: now,
        })
        .returning({ id: leads.id });
      leadId = created.id;
    }

    await tx
      .update(diagnosticSubmissions)
      .set({ leadId })
      .where(eq(diagnosticSubmissions.id, submission.id));

    return {
      ok: true as const,
      submissionId: submission.id,
      leadId,
      leadCreated: !existing,
      result,
      answers,
    };
  });
}

/**
 * Record a consultation request made from the result page.
 * Idempotent: the first request time is kept.
 */
export async function requestAxMigrationConsultation(
  database: Database,
  submissionId: string,
  now: Date = new Date()
): Promise<
  | { ok: true; alreadyRequested: boolean; organizationId: string; leadId: string | null }
  | { ok: false; reason: 'not_found' }
> {
  return database.transaction(async (tx) => {
    const submission = await tx.query.diagnosticSubmissions.findFirst({
      where: and(
        eq(diagnosticSubmissions.id, submissionId),
        eq(diagnosticSubmissions.diagnosticKey, AX_MIGRATION_DIAGNOSTIC_KEY)
      ),
    });
    if (!submission) return { ok: false as const, reason: 'not_found' as const };

    const alreadyRequested = submission.consultationRequestedAt !== null;
    if (!alreadyRequested) {
      await tx
        .update(diagnosticSubmissions)
        .set({ consultationRequestedAt: now })
        .where(eq(diagnosticSubmissions.id, submissionId));

      if (submission.leadId) {
        await tx
          .update(leads)
          .set({
            conversionPoint: 'consultation',
            responses: sql`jsonb_set(coalesce(${leads.responses}, '{}'::jsonb), '{axMigration,consultationRequested}', 'true'::jsonb, true)`,
            updatedAt: now,
          })
          .where(eq(leads.id, submission.leadId));
      }
    }

    return {
      ok: true as const,
      alreadyRequested,
      organizationId: submission.organizationId,
      leadId: submission.leadId,
    };
  });
}
