/**
 * AX migration diagnosis API route tests
 * The real route handler is imported; DB access and notifications are mocked.
 */
import { NextRequest } from 'next/server';
import { beforeEach, describe, expect, it, vi } from 'vitest';

const submitMock = vi.fn();
const notifyMock = vi.fn();
const resolveOrgMock = vi.fn();

vi.mock('@/lib/db/client', () => ({ db: {} }));
vi.mock('@/lib/features/diagnostics/ax-migration/notify', () => ({
  notifyAxMigrationSubmission: (...args: unknown[]) => notifyMock(...args),
}));
vi.mock('@/lib/features/diagnostics/organization', () => ({
  resolveDiagnosisOrganizationId: () => resolveOrgMock(),
}));
vi.mock('@/lib/features/diagnostics/ax-migration/submission-service', async (importOriginal) => {
  const original =
    await importOriginal<typeof import('@/lib/features/diagnostics/ax-migration/submission-service')>();
  return {
    ...original,
    submitAxMigrationDiagnosis: (...args: unknown[]) => submitMock(...args),
  };
});

const { POST } = await import('@/app/api/diagnostics/ax-migration/route');
const { evaluateAxMigration } = await import('@/lib/features/diagnostics/ax-migration/evaluate');

const ORG_ID = '11111111-1111-4111-8111-111111111111';

const validBody = {
  answers: { industry: 'manufacturing' },
  contact: { company: '三田製作所', name: '山田', email: 'yamada@example.jp' },
  privacyConsent: true,
  consultationRequested: true,
  tracking: { utmMedium: 'cpc' },
  locale: 'ja',
};

const request = (body: unknown) =>
  new NextRequest('http://localhost/api/diagnostics/ax-migration', {
    method: 'POST',
    body: typeof body === 'string' ? body : JSON.stringify(body),
    headers: { 'content-type': 'application/json' },
  });

const result = evaluateAxMigration({
  industry: 'manufacturing',
  revenue: '10b_30b',
  system: 'as400',
  languages: ['rpg'],
  years: 'gte20',
  programs: '500_2000',
  integrations: 'some',
  maintenance: 'few',
  documents: 'partial',
  challenges: ['people'],
  timeline: '1_2y',
  role: 'it_manager',
});

describe('POST /api/diagnostics/ax-migration', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    resolveOrgMock.mockReturnValue(ORG_ID);
    notifyMock.mockResolvedValue(undefined);
  });

  it('returns the public result and notifies sales', async () => {
    submitMock.mockResolvedValue({
      ok: true,
      submissionId: 'sub-1',
      leadId: 'lead-1',
      leadCreated: true,
      result,
      answers: {},
    });

    const response = await POST(request(validBody));
    expect(response.status).toBe(200);
    const json = await response.json();
    expect(json.submissionId).toBe('sub-1');
    expect(json.result.difficulty).toEqual(result.difficulty);
    // Sales-only fields are never sent to the respondent
    expect(json.result).not.toHaveProperty('leadScore');
    expect(json.result).not.toHaveProperty('mql');
    expect(json).not.toHaveProperty('leadId');

    expect(submitMock).toHaveBeenCalledWith({}, ORG_ID, expect.objectContaining({ consultationRequested: true }));
    expect(notifyMock).toHaveBeenCalledWith(
      expect.objectContaining({ organizationId: ORG_ID, leadId: 'lead-1', consultationRequested: true })
    );
  });

  it('rejects requests without privacy consent', async () => {
    const response = await POST(request({ ...validBody, privacyConsent: false }));
    expect(response.status).toBe(400);
    expect(submitMock).not.toHaveBeenCalled();
  });

  it('rejects bots that fill the honeypot field', async () => {
    const response = await POST(request({ ...validBody, website: 'http://spam.example' }));
    expect(response.status).toBe(400);
    expect(submitMock).not.toHaveBeenCalled();
  });

  it('rejects malformed JSON', async () => {
    const response = await POST(request('{not json'));
    expect(response.status).toBe(400);
  });

  it('returns 400 with issues when answers are invalid', async () => {
    submitMock.mockResolvedValue({ ok: false, issues: [{ questionId: 'system', code: 'required' }] });
    const response = await POST(request(validBody));
    expect(response.status).toBe(400);
    expect((await response.json()).issues).toEqual([{ questionId: 'system', code: 'required' }]);
    expect(notifyMock).not.toHaveBeenCalled();
  });

  it('returns 503 when no receiving organization is configured', async () => {
    resolveOrgMock.mockReturnValue(null);
    const response = await POST(request(validBody));
    expect(response.status).toBe(503);
    expect(submitMock).not.toHaveBeenCalled();
  });

  it('still answers the respondent when notification fails', async () => {
    submitMock.mockResolvedValue({
      ok: true,
      submissionId: 'sub-2',
      leadId: 'lead-2',
      leadCreated: false,
      result,
      answers: {},
    });
    notifyMock.mockRejectedValue(new Error('smtp down'));
    const response = await POST(request(validBody));
    expect(response.status).toBe(200);
  });
});
