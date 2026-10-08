/**
 * RLS helpers against a real PostgreSQL database.
 * Skipped unless TEST_DATABASE_URL is set (see ax-migration-submission.db.test.ts).
 */
import { setCurrentUser } from '@/lib/db/rls';
import * as schema from '@/lib/db/schema';
import { sql } from 'drizzle-orm';
import { drizzle } from 'drizzle-orm/postgres-js';
import postgres from 'postgres';
import { afterAll, describe, expect, it } from 'vitest';

const url = process.env.TEST_DATABASE_URL;

describe.skipIf(!url)('setCurrentUser (PostgreSQL)', () => {
  const client = url ? postgres(url, { max: 1 }) : null;
  const db = client ? drizzle(client, { schema }) : null;

  afterAll(async () => {
    await client?.end();
  });

  it('sets the user id for the current transaction only', async () => {
    const userId = '11111111-1111-4111-8111-111111111111';
    // biome-ignore lint/style/noNonNullAssertion: guarded by skipIf
    const inside = await db!.transaction(async (tx) => {
      await setCurrentUser(tx as never, userId);
      const rows = await tx.execute(sql`SELECT current_setting('app.current_user_id', true) AS id`);
      return (rows as unknown as { id: string }[])[0].id;
    });
    expect(inside).toBe(userId);

    // biome-ignore lint/style/noNonNullAssertion: guarded by skipIf
    const after = await db!.execute(sql`SELECT current_setting('app.current_user_id', true) AS id`);
    expect((after as unknown as { id: string | null }[])[0].id || '').toBe('');
  });

  it('accepts a null user', async () => {
    // biome-ignore lint/style/noNonNullAssertion: guarded by skipIf
    await expect(db!.transaction((tx) => setCurrentUser(tx as never, null))).resolves.toBeUndefined();
  });
});
