ALTER TABLE "leads" ADD COLUMN "inflow_source" text;--> statement-breakpoint
ALTER TABLE "leads" ADD COLUMN "conversion_point" text;--> statement-breakpoint
ALTER TABLE "leads" ADD COLUMN "deal_phase" text;--> statement-breakpoint
ALTER TABLE "leads" ADD COLUMN "target_system" text;--> statement-breakpoint
ALTER TABLE "leads" ADD COLUMN "referrer_name" text;--> statement-breakpoint
ALTER TABLE "leads" ADD COLUMN "lost_reason" text;--> statement-breakpoint
ALTER TABLE "leads" ADD COLUMN "has_negotiated" boolean DEFAULT false NOT NULL;--> statement-breakpoint
ALTER TABLE "leads" ADD COLUMN "mql_qualified_at" timestamp;--> statement-breakpoint
ALTER TABLE "leads" ADD COLUMN "sql_qualified_at" timestamp;--> statement-breakpoint
-- Map legacy statuses to the 5-stage sales pipeline (#54)
UPDATE "leads" SET "status" = CASE "status"
  WHEN 'contacted' THEN 'nurturing'
  WHEN 'qualified' THEN 'negotiating'
  WHEN 'converted' THEN 'won'
  ELSE "status"
END
WHERE "status" IN ('contacted', 'qualified', 'converted');--> statement-breakpoint
UPDATE "leads" SET "has_negotiated" = true WHERE "status" IN ('negotiating', 'won');
