CREATE TABLE "diagnostic_submissions" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"organization_id" uuid NOT NULL,
	"lead_id" uuid,
	"diagnostic_key" text NOT NULL,
	"diagnostic_version" integer NOT NULL,
	"answers" jsonb NOT NULL,
	"result" jsonb NOT NULL,
	"tracking" jsonb DEFAULT '{}'::jsonb NOT NULL,
	"locale" text,
	"consultation_requested_at" timestamp,
	"created_at" timestamp DEFAULT now() NOT NULL
);
--> statement-breakpoint
ALTER TABLE "diagnostic_submissions" ADD CONSTRAINT "diagnostic_submissions_organization_id_organizations_id_fk" FOREIGN KEY ("organization_id") REFERENCES "public"."organizations"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "diagnostic_submissions" ADD CONSTRAINT "diagnostic_submissions_lead_id_leads_id_fk" FOREIGN KEY ("lead_id") REFERENCES "public"."leads"("id") ON DELETE set null ON UPDATE no action;--> statement-breakpoint
CREATE INDEX "diagnostic_submissions_org_key_created_idx" ON "diagnostic_submissions" USING btree ("organization_id","diagnostic_key","created_at");--> statement-breakpoint
CREATE INDEX "diagnostic_submissions_lead_idx" ON "diagnostic_submissions" USING btree ("lead_id");