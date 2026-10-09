ALTER TABLE "leads" ADD COLUMN "inflow_source" text;--> statement-breakpoint
ALTER TABLE "leads" ADD COLUMN "conversion_point" text;--> statement-breakpoint
ALTER TABLE "leads" ADD COLUMN "deal_phase" text;--> statement-breakpoint
ALTER TABLE "leads" ADD COLUMN "target_system" text;--> statement-breakpoint
ALTER TABLE "leads" ADD COLUMN "referrer_name" text;--> statement-breakpoint
ALTER TABLE "leads" ADD COLUMN "lost_reason" text;--> statement-breakpoint
ALTER TABLE "leads" ADD COLUMN "has_negotiated" boolean DEFAULT false NOT NULL;--> statement-breakpoint
ALTER TABLE "leads" ADD COLUMN "mql_qualified_at" timestamp;--> statement-breakpoint
ALTER TABLE "leads" ADD COLUMN "sql_decision" text;--> statement-breakpoint
ALTER TABLE "leads" ADD COLUMN "sql_decided_at" timestamp;--> statement-breakpoint
-- Map legacy statuses to the 5-stage sales pipeline (#54). Idempotent: safe to re-run after deploy.
UPDATE "leads" SET "status" = CASE "status"
  WHEN 'contacted' THEN 'nurturing'
  WHEN 'qualified' THEN 'negotiating'
  WHEN 'converted' THEN 'won'
  ELSE "status"
END
WHERE "status" IN ('contacted', 'qualified', 'converted');--> statement-breakpoint
UPDATE "leads" SET "has_negotiated" = true WHERE "status" IN ('negotiating', 'won');--> statement-breakpoint
-- Reject legacy values from now on (e.g. an old deployment still running during the switch)
ALTER TABLE "leads" ADD CONSTRAINT "leads_status_check" CHECK ("status" IN ('new', 'nurturing', 'negotiating', 'won', 'lost')) NOT VALID;--> statement-breakpoint
ALTER TABLE "leads" VALIDATE CONSTRAINT "leads_status_check";
