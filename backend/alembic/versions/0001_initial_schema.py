"""initial schema

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-06-12 00:00:00
"""
from alembic import op

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS jobs (
            job_id SERIAL PRIMARY KEY,
            company_name VARCHAR(255) NOT NULL,
            job_title VARCHAR(255) NOT NULL,
            location VARCHAR(255),
            salary_min DOUBLE PRECISION,
            salary_max DOUBLE PRECISION,
            job_description TEXT NOT NULL,
            source_url TEXT NOT NULL,
            date_found DATE NOT NULL DEFAULT CURRENT_DATE,
            application_deadline DATE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE
        )
        """
    )

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS applications (
            application_id SERIAL PRIMARY KEY,
            job_id INTEGER NOT NULL UNIQUE REFERENCES jobs (job_id) ON DELETE CASCADE,
            status VARCHAR(100) NOT NULL DEFAULT 'Not Applied',
            date_applied DATE,
            cv_version VARCHAR(255),
            cover_letter_version VARCHAR(255),
            referral_contact VARCHAR(255),
            interview_stage VARCHAR(255),
            notes TEXT,
            last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
        """
    )

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS keywords (
            keyword_id SERIAL PRIMARY KEY,
            job_id INTEGER NOT NULL REFERENCES jobs (job_id) ON DELETE CASCADE,
            keyword VARCHAR(255) NOT NULL
        )
        """
    )

    op.execute("CREATE INDEX IF NOT EXISTS ix_jobs_job_id ON jobs (job_id)")
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_applications_application_id ON applications (application_id)"
    )
    op.execute("CREATE INDEX IF NOT EXISTS ix_keywords_keyword_id ON keywords (keyword_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_keywords_job_id ON keywords (job_id)")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS keywords")
    op.execute("DROP TABLE IF EXISTS applications")
    op.execute("DROP TABLE IF EXISTS jobs")
