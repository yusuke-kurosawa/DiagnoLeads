import { db } from '@/lib/db/client';
import { toPublicResult } from '@/lib/features/diagnostics/ax-migration/evaluate';
import { notifyAxMigrationSubmission } from '@/lib/features/diagnostics/ax-migration/notify';
import {
  axMigrationSubmissionSchema,
  submitAxMigrationDiagnosis,
} from '@/lib/features/diagnostics/ax-migration/submission-service';
import { resolveDiagnosisOrganizationId } from '@/lib/features/diagnostics/organization';
import { type NextRequest, NextResponse } from 'next/server';

/**
 * POST /api/diagnostics/ax-migration
 *
 * Public endpoint for the AX migration self-diagnosis.
 * Validates answers, evaluates them on the server, saves the submission and
 * creates or updates the lead. Returns only the respondent-facing result.
 */
export async function POST(req: NextRequest) {
  let body: unknown;
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ error: 'Invalid JSON' }, { status: 400 });
  }

  const parsed = axMigrationSubmissionSchema.safeParse(body);
  if (!parsed.success) {
    return NextResponse.json(
      { error: 'Validation failed', details: parsed.error.flatten() },
      { status: 400 }
    );
  }

  const organizationId = resolveDiagnosisOrganizationId();
  if (!organizationId) {
    console.error(
      'AX diagnosis: AX_DIAGNOSIS_ORGANIZATION_ID / DEFAULT_ORGANIZATION_ID is not set'
    );
    return NextResponse.json({ error: 'Diagnosis is not available' }, { status: 503 });
  }

  try {
    const outcome = await submitAxMigrationDiagnosis(db, organizationId, parsed.data);
    if (!outcome.ok) {
      return NextResponse.json(
        { error: 'Invalid answers', issues: outcome.issues },
        { status: 400 }
      );
    }

    // Fire-and-forget: notifications must not delay or fail the respondent's flow
    notifyAxMigrationSubmission({
      organizationId,
      leadId: outcome.leadId,
      submissionId: outcome.submissionId,
      company: parsed.data.contact.company,
      name: parsed.data.contact.name,
      email: parsed.data.contact.email,
      result: outcome.result,
      consultationRequested: parsed.data.consultationRequested,
      leadCreated: outcome.leadCreated,
      requestedAt: new Date(),
    }).catch((error) => console.error('AX diagnosis notification error:', error));

    return NextResponse.json({
      submissionId: outcome.submissionId,
      consultationRequested: parsed.data.consultationRequested,
      result: toPublicResult(outcome.result),
    });
  } catch (error) {
    console.error('AX diagnosis submission error:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
