"""Add Row-Level Security (RLS) policies for multi-tenant isolation

Revision ID: f5a2c3d8e9b1
Revises: e33568d0d2e9
Create Date: 2025-11-12 10:00:00.000000

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f5a2c3d8e9b1"
down_revision: Union[str, None] = "e33568d0d2e9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Enable Row-Level Security (RLS) on tenant-scoped tables"""

    # Enable RLS on assessments table
    op.execute("ALTER TABLE assessments ENABLE ROW LEVEL SECURITY;")

    # Create policy for assessments: users can only see assessments from their tenant
    op.execute("""
        CREATE POLICY assessment_tenant_isolation ON assessments
        FOR ALL
        USING (tenant_id = current_setting('app.current_tenant_id')::uuid)
        WITH CHECK (tenant_id = current_setting('app.current_tenant_id')::uuid);
    """)

    # Enable RLS on leads table
    op.execute("ALTER TABLE leads ENABLE ROW LEVEL SECURITY;")

    # Create policy for leads: users can only see leads from their tenant
    op.execute("""
        CREATE POLICY lead_tenant_isolation ON leads
        FOR ALL
        USING (tenant_id = current_setting('app.current_tenant_id')::uuid)
        WITH CHECK (tenant_id = current_setting('app.current_tenant_id')::uuid);
    """)

    # Enable RLS on qr_codes table
    op.execute("ALTER TABLE qr_codes ENABLE ROW LEVEL SECURITY;")

    # Create policy for qr_codes: users can only see QR codes from their tenant
    op.execute("""
        CREATE POLICY qr_code_tenant_isolation ON qr_codes
        FOR ALL
        USING (tenant_id = current_setting('app.current_tenant_id')::uuid)
        WITH CHECK (tenant_id = current_setting('app.current_tenant_id')::uuid);
    """)

    # Enable RLS on qr_code_scans table
    op.execute("ALTER TABLE qr_code_scans ENABLE ROW LEVEL SECURITY;")

    # Create policy for qr_code_scans: users can only see scans from their tenant
    op.execute("""
        CREATE POLICY qr_code_scan_tenant_isolation ON qr_code_scans
        FOR ALL
        USING (tenant_id = current_setting('app.current_tenant_id')::uuid)
        WITH CHECK (tenant_id = current_setting('app.current_tenant_id')::uuid);
    """)

    # Grant necessary permissions to authenticated users
    op.execute("GRANT SELECT ON assessments TO postgres;")
    op.execute("GRANT INSERT ON assessments TO postgres;")
    op.execute("GRANT UPDATE ON assessments TO postgres;")
    op.execute("GRANT DELETE ON assessments TO postgres;")

    op.execute("GRANT SELECT ON leads TO postgres;")
    op.execute("GRANT INSERT ON leads TO postgres;")
    op.execute("GRANT UPDATE ON leads TO postgres;")
    op.execute("GRANT DELETE ON leads TO postgres;")


def downgrade() -> None:
    """Remove Row-Level Security policies"""

    # Drop RLS policies
    op.execute("DROP POLICY IF EXISTS assessment_tenant_isolation ON assessments;")
    op.execute("DROP POLICY IF EXISTS lead_tenant_isolation ON leads;")
    op.execute("DROP POLICY IF EXISTS qr_code_tenant_isolation ON qr_codes;")
    op.execute("DROP POLICY IF EXISTS qr_code_scan_tenant_isolation ON qr_code_scans;")

    # Disable RLS
    op.execute("ALTER TABLE assessments DISABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE leads DISABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE qr_codes DISABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE qr_code_scans DISABLE ROW LEVEL SECURITY;")
