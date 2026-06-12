from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from sqlalchemy import Date, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from .database import Base


class Job(Base):
    """
    Represents a job posting.

    One row in this table = one job you found/saved.
    """

    __tablename__ = "jobs"

    job_id: Mapped[int] = mapped_column(primary_key=True, index=True)

    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    job_title: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    salary_min: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    salary_max: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    job_description: Mapped[str] = mapped_column(Text, nullable=False)
    source_url: Mapped[str] = mapped_column(Text, nullable=False)

    date_found: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        default=date.today,
    )
    application_deadline: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
    )

    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
    )

    application: Mapped[Optional["Application"]] = relationship(
        back_populates="job",
        uselist=False,
        cascade="all, delete-orphan",
    )
    keywords: Mapped[list["Keyword"]] = relationship(
        back_populates="job",
        cascade="all, delete-orphan",
    )


class Application(Base):
    """
    Represents your personal application status for a job.

    One row in this table = your tracking info for one job.
    """

    __tablename__ = "applications"

    application_id: Mapped[int] = mapped_column(primary_key=True, index=True)

    job_id: Mapped[int] = mapped_column(
        ForeignKey("jobs.job_id"),
        unique=True,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="Not Applied",
    )
    date_applied: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    cv_version: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    cover_letter_version: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    referral_contact: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    interview_stage: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    last_updated: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    job: Mapped["Job"] = relationship(back_populates="application")


class Keyword(Base):
    """
    Represents a keyword/tag associated with a job.

    One row in this table = one keyword for one job.
    """

    __tablename__ = "keywords"

    keyword_id: Mapped[int] = mapped_column(primary_key=True, index=True)

    job_id: Mapped[int] = mapped_column(
        ForeignKey("jobs.job_id"),
        nullable=False,
    )

    keyword: Mapped[str] = mapped_column(String(255), nullable=False)

    job: Mapped["Job"] = relationship(back_populates="keywords")
