"""Add Question, QuestionOption, Response, and Answer tables

Revision ID: b2c3d4e5f6g7
Revises: a1b2c3d4e5f6
Create Date: 2025-11-18 12:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b2c3d4e5f6g7"
down_revision: Union[str, None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add Question, QuestionOption, Response, and Answer tables"""

    # Create questions table
    op.create_table(
        "questions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("assessment_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("type", sa.String(length=50), nullable=False),  # single_choice, multiple_choice, text, slider
        sa.Column("order", sa.Integer(), nullable=False),
        sa.Column("points", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("explanation", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(["assessment_id"], ["assessments.id"], ondelete="CASCADE"),
    )

    # Create indexes for questions
    op.create_index("idx_questions_assessment_order", "questions", ["assessment_id", "order"])
    op.create_index("idx_questions_assessment_id", "questions", ["assessment_id"])

    # Create question_options table
    op.create_table(
        "question_options",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("question_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("text", sa.String(length=255), nullable=False),
        sa.Column("points", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("order", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["question_id"], ["questions.id"], ondelete="CASCADE"),
    )

    # Create indexes for question_options
    op.create_index(
        "idx_question_options_question_order",
        "question_options",
        ["question_id", "order"],
    )
    op.create_index("idx_question_options_question_id", "question_options", ["question_id"])

    # Create responses table
    op.create_table(
        "responses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("assessment_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("session_id", sa.String(length=255), nullable=False, unique=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="in_progress"),  # in_progress, completed, abandoned
        sa.Column("total_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("ip_address", sa.String(length=100), nullable=True),
        sa.Column("user_agent", sa.String(length=500), nullable=True),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["assessment_id"], ["assessments.id"], ondelete="CASCADE"),
    )

    # Create indexes for responses
    op.create_index(
        "idx_responses_assessment_completed",
        "responses",
        ["assessment_id", "completed_at"],
    )
    op.create_index("idx_responses_session_id", "responses", ["session_id"])
    op.create_index("idx_responses_assessment_id", "responses", ["assessment_id"])
    op.create_index("idx_responses_status", "responses", ["status"])

    # Create answers table
    op.create_table(
        "answers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("response_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("question_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("answer_text", sa.Text(), nullable=True),
        sa.Column("points_awarded", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "answered_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(["response_id"], ["responses.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["question_id"], ["questions.id"], ondelete="CASCADE"),
    )

    # Create indexes for answers
    op.create_index("idx_answers_response_id", "answers", ["response_id"])
    op.create_index("idx_answers_question_id", "answers", ["question_id"])
    op.create_index("idx_answers_response_question", "answers", ["response_id", "question_id"])

    # Add response_id to leads table
    op.add_column("leads", sa.Column("response_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key(
        "fk_leads_response_id",
        "leads",
        "responses",
        ["response_id"],
        ["id"],
        ondelete="SET NULL",
    )

    # Enable Row-Level Security (RLS) for responses table
    # Note: responses table doesn't have tenant_id, but tenant isolation is enforced through assessment_id
    # We'll use a more complex policy that joins with assessments table
    op.execute("""
        ALTER TABLE responses ENABLE ROW LEVEL SECURITY;
    """)

    op.execute("""
        CREATE POLICY responses_tenant_isolation
        ON responses
        FOR ALL
        USING (
            EXISTS (
                SELECT 1 FROM assessments
                WHERE assessments.id = responses.assessment_id
                AND assessments.tenant_id::text = current_setting('app.current_tenant_id', true)
            )
        );
    """)

    # Enable RLS for answers table (similar policy through responses)
    op.execute("""
        ALTER TABLE answers ENABLE ROW LEVEL SECURITY;
    """)

    op.execute("""
        CREATE POLICY answers_tenant_isolation
        ON answers
        FOR ALL
        USING (
            EXISTS (
                SELECT 1 FROM responses
                JOIN assessments ON assessments.id = responses.assessment_id
                WHERE responses.id = answers.response_id
                AND assessments.tenant_id::text = current_setting('app.current_tenant_id', true)
            )
        );
    """)


def downgrade() -> None:
    """Remove Question, QuestionOption, Response, and Answer tables"""

    # Drop RLS policies
    op.execute("DROP POLICY IF EXISTS answers_tenant_isolation ON answers;")
    op.execute("DROP POLICY IF EXISTS responses_tenant_isolation ON responses;")

    # Disable RLS
    op.execute("ALTER TABLE answers DISABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE responses DISABLE ROW LEVEL SECURITY;")

    # Remove response_id from leads table
    op.drop_constraint("fk_leads_response_id", "leads", type_="foreignkey")
    op.drop_column("leads", "response_id")

    # Drop indexes and tables in reverse order
    op.drop_index("idx_answers_response_question", table_name="answers")
    op.drop_index("idx_answers_question_id", table_name="answers")
    op.drop_index("idx_answers_response_id", table_name="answers")
    op.drop_table("answers")

    op.drop_index("idx_responses_status", table_name="responses")
    op.drop_index("idx_responses_assessment_id", table_name="responses")
    op.drop_index("idx_responses_session_id", table_name="responses")
    op.drop_index("idx_responses_assessment_completed", table_name="responses")
    op.drop_table("responses")

    op.drop_index("idx_question_options_question_id", table_name="question_options")
    op.drop_index("idx_question_options_question_order", table_name="question_options")
    op.drop_table("question_options")

    op.drop_index("idx_questions_assessment_id", table_name="questions")
    op.drop_index("idx_questions_assessment_order", table_name="questions")
    op.drop_table("questions")
