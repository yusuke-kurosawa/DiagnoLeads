-- content_editors held the dashboard's FAQ / blog editor grants, unused since #413 (CMS P1) and
-- empty in production (2026-10-23). Dropped in CMS P2 (#418, Epic #339). Idempotent.
DROP TABLE IF EXISTS "public"."content_editors";
