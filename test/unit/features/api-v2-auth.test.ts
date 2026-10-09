/**
 * REST API v2 authentication — the real route handler is called; session and DB are mocked.
 */
import { NextRequest } from 'next/server';
import { beforeEach, describe, expect, it, vi } from 'vitest';

const ORG_ID = '11111111-1111-4111-8111-111111111111';
const USER_ID = '44444444-4444-4444-8444-444444444444';

const getSession = vi.fn();
const findMembership = vi.fn();
const findLeads = vi.fn();
const countChain = {
  from: vi.fn(),
  where: vi.fn(),
};
countChain.from.mockReturnValue(countChain);

vi.mock('@/lib/auth', () => ({ auth: { api: { getSession: (...a: unknown[]) => getSession(...a) } } }));
vi.mock('next/headers', () => ({ headers: vi.fn().mockResolvedValue(new Headers()) }));
vi.mock('@/lib/db', () => ({
  db: {
    query: {
      organizationMembers: { findFirst: (...a: unknown[]) => findMembership(...a) },
      leads: { findMany: (...a: unknown[]) => findLeads(...a) },
    },
    select: vi.fn(() => countChain),
  },
}));

const { GET } = await import('@/app/api/v2/leads/route');

const get = (headers: Record<string, string> = {}) =>
  GET(new NextRequest('http://localhost/api/v2/leads', { headers }));

describe('REST API v2 authentication', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    countChain.from.mockReturnValue(countChain);
    countChain.where.mockResolvedValue([{ count: 0 }]);
    findLeads.mockResolvedValue([]);
  });

  it('rejects a bearer token that only names an organization', async () => {
    getSession.mockResolvedValue(null);
    const response = await get({ authorization: `Bearer org_${ORG_ID}_anything` });
    expect(response.status).toBe(401);
    expect(findLeads).not.toHaveBeenCalled();
  });

  it('rejects a session whose user is not a member of the active organization', async () => {
    getSession.mockResolvedValue({ session: { activeOrganizationId: ORG_ID }, user: { id: USER_ID } });
    findMembership.mockResolvedValue(undefined);
    const response = await get();
    expect(response.status).toBe(401);
    expect(findLeads).not.toHaveBeenCalled();
  });

  it('rejects a session without an active organization', async () => {
    getSession.mockResolvedValue({ session: {}, user: { id: USER_ID } });
    const response = await get();
    expect(response.status).toBe(401);
  });

  it('allows a member of the active organization', async () => {
    getSession.mockResolvedValue({ session: { activeOrganizationId: ORG_ID }, user: { id: USER_ID } });
    findMembership.mockResolvedValue({ id: 'm-1', organizationId: ORG_ID, userId: USER_ID });
    const response = await get();
    expect(response.status).not.toBe(401);
    expect(findMembership).toHaveBeenCalled();
  });
});
