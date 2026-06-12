from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class KeywordCreate(BaseModel):
    keyword: str = Field(min_length=1, max_length=255)

    @field_validator("keyword")
    @classmethod
    def keyword_must_not_be_blank(cls, value: str):
        cleaned_value = value.strip()
        if not cleaned_value:
            raise ValueError("Keyword must not be blank")
        return cleaned_value


class KeywordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    keyword_id: int
    job_id: int
    keyword: str


class AnalyzeDescriptionRequest(BaseModel):
    job_description: str = Field(min_length=1)


class AnalyzedKeyword(BaseModel):
    keyword: str
    confidence: float


class AnalyzeDescriptionResponse(BaseModel):
    summary: str
    suggested_keywords: list[AnalyzedKeyword] = Field(default_factory=list)
    seniority: str
    score: int


class ApplicationBase(BaseModel):
    status: str = "Not Applied"
    date_applied: Optional[date] = None
    cv_version: Optional[str] = None
    cover_letter_version: Optional[str] = None
    referral_contact: Optional[str] = None
    interview_stage: Optional[str] = None
    notes: Optional[str] = None


class ApplicationCreate(ApplicationBase):
    job_id: int


class ApplicationUpdate(BaseModel):
    status: Optional[str] = None
    date_applied: Optional[date] = None
    cv_version: Optional[str] = None
    cover_letter_version: Optional[str] = None
    referral_contact: Optional[str] = None
    interview_stage: Optional[str] = None
    notes: Optional[str] = None


class ApplicationResponse(ApplicationBase):
    model_config = ConfigDict(from_attributes=True)

    application_id: int
    job_id: int
    last_updated: Optional[datetime] = None


class JobBase(BaseModel):
    company_name: str
    job_title: str
    location: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    job_description: str
    source_url: Optional[str] = None
    application_deadline: Optional[date] = None


class JobCreate(JobBase):
    keywords: list[str] = Field(default_factory=list)


class JobUpdate(BaseModel):
    company_name: Optional[str] = None
    job_title: Optional[str] = None
    location: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    job_description: Optional[str] = None
    source_url: Optional[str] = None
    application_deadline: Optional[date] = None


class JobResponse(JobBase):
    model_config = ConfigDict(from_attributes=True)

    job_id: int
    date_found: date
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    application: Optional[ApplicationResponse] = None
    keywords: list[KeywordResponse] = Field(default_factory=list)


class SummaryReport(BaseModel):
    total_jobs: int
    total_applications: int
    jobs_without_application_record: int
    active_applications: int
    unique_companies: int
    total_keywords: int
    upcoming_deadlines: int
    overdue_deadlines: int


class CountByLabel(BaseModel):
    label: str
    count: int


class SalarySummary(BaseModel):
    jobs_with_salary_min: int
    jobs_with_salary_max: int
    average_salary_min: Optional[float] = None
    average_salary_max: Optional[float] = None
    lowest_salary_min: Optional[float] = None
    highest_salary_max: Optional[float] = None
