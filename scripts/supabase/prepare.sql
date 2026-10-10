-- Prepare a Supabase project for `bun run db:migrate`.
-- Run as the postgres role (SQL Editor, or psql through the session pooler on port 5432)
-- before the first migration. Safe to run again.
BEGIN;

-- Extensions used by the migrations (0001: vector, ltree). Supabase keeps extensions in the
-- extensions schema, which is on the postgres role's search_path.
CREATE EXTENSION IF NOT EXISTS vector WITH SCHEMA extensions;
CREATE EXTENSION IF NOT EXISTS ltree WITH SCHEMA extensions;

-- The application connects as postgres and does not use the Data API (PostgREST, pg_graphql).
-- Supabase grants anon and authenticated full access to new objects in public by default, so
-- withdraw those grants for existing objects and for everything postgres creates from now on.
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public REVOKE ALL ON TABLES FROM anon, authenticated;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public REVOKE ALL ON SEQUENCES FROM anon, authenticated;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public REVOKE ALL ON FUNCTIONS FROM anon, authenticated;
REVOKE ALL ON ALL TABLES IN SCHEMA public FROM anon, authenticated;
REVOKE ALL ON ALL SEQUENCES IN SCHEMA public FROM anon, authenticated;
REVOKE ALL ON ALL FUNCTIONS IN SCHEMA public FROM anon, authenticated;

COMMIT;
