import os
from datetime import date
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from .ai import analyze_job_description
from .auth import require_api_key
from . import crud, models, schemas
from .database import SessionLocal

app = FastAPI(title="AI Job Tracker API")

allowed_origins_raw = os.getenv(
    "ALLOWED_ORIGINS",
    "http://127.0.0.1:3000,http://localhost:3000,http://localhost",
)
allowed_origins = [
    origin.strip() for origin in allowed_origins_raw.split(",") if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def read_root():
    return {"message": "AI Job Tracker API is running"}


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ok"}


@app.post(
    "/analyze-description",
    response_model=schemas.AnalyzeDescriptionResponse,
)
def analyze_description(
    payload: schemas.AnalyzeDescriptionRequest,
):
    return analyze_job_description(payload.job_description)


@app.get("/jobs/count")
def count_jobs(db: Session = Depends(get_db)):
    count = db.query(models.Job).count()
    return {"job_count": count}


@app.post(
    "/jobs",
    response_model=schemas.JobResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_api_key)],
)
def create_job(job: schemas.JobCreate, db: Session = Depends(get_db)):
    return crud.create_job(db=db, job=job)


@app.get("/jobs", response_model=list[schemas.JobResponse])
def read_jobs(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    company: Optional[str] = None,
    title: Optional[str] = None,
    location: Optional[str] = None,
    application_status: Optional[str] = Query(default=None, alias="status"),
    deadline_from: Optional[date] = None,
    deadline_to: Optional[date] = None,
    salary_min: Optional[float] = None,
    salary_max: Optional[float] = None,
    keyword: Optional[str] = None,
    db: Session = Depends(get_db),
):
    return crud.get_jobs(
        db=db,
        skip=skip,
        limit=limit,
        company=company,
        title=title,
        location=location,
        status=application_status,
        deadline_from=deadline_from,
        deadline_to=deadline_to,
        salary_min=salary_min,
        salary_max=salary_max,
        keyword=keyword,
    )


@app.get("/jobs/{job_id}", response_model=schemas.JobResponse)
def read_job(job_id: int, db: Session = Depends(get_db)):
    db_job = crud.get_job(db=db, job_id=job_id)
    if db_job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return db_job


@app.put("/jobs/{job_id}", response_model=schemas.JobResponse)
def update_job(
    job_id: int,
    job_update: schemas.JobUpdate,
    db: Session = Depends(get_db),
):
    db_job = crud.update_job(db=db, job_id=job_id, job_update=job_update)
    if db_job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return db_job


@app.get(
    "/jobs/{job_id}/application",
    response_model=schemas.ApplicationResponse,
    dependencies=[Depends(require_api_key)],
)
def read_job_application(job_id: int, db: Session = Depends(get_db)):
    _require_job(db, job_id)
    db_application = crud.get_application_by_job_id(db=db, job_id=job_id)
    if db_application is None:
        raise HTTPException(status_code=404, detail="Application record not found")
    return db_application


@app.put(
    "/jobs/{job_id}/application",
    response_model=schemas.ApplicationResponse,
    dependencies=[Depends(require_api_key)],
)
def upsert_job_application(
    job_id: int,
    application_update: schemas.ApplicationUpdate,
    db: Session = Depends(get_db),
):
    _require_job(db, job_id)
    return crud.upsert_application_for_job(
        db=db,
        job_id=job_id,
        application_update=application_update,
    )


@app.post(
    "/jobs/{job_id}/keywords",
    response_model=schemas.KeywordResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_api_key)],
)
def add_keyword_to_job(
    job_id: int,
    keyword: schemas.KeywordCreate,
    db: Session = Depends(get_db),
):
    _require_job(db, job_id)
    return crud.add_keyword_to_job(db=db, job_id=job_id, keyword=keyword)


@app.get("/jobs/{job_id}/keywords", response_model=list[schemas.KeywordResponse])
def read_job_keywords(job_id: int, db: Session = Depends(get_db)):
    _require_job(db, job_id)
    return crud.get_keywords_for_job(db=db, job_id=job_id)


@app.post(
    "/applications",
    response_model=schemas.ApplicationResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_api_key)],
)
def create_application(
    application: schemas.ApplicationCreate,
    db: Session = Depends(get_db),
):
    _require_job(db, application.job_id)
    existing_application = crud.get_application_by_job_id(
        db=db,
        job_id=application.job_id,
    )
    if existing_application:
        raise HTTPException(
            status_code=409,
            detail="Application record already exists for this job",
        )
    return crud.create_application(db=db, application=application)


@app.get("/applications", response_model=list[schemas.ApplicationResponse])
def read_applications(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    application_status: Optional[str] = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
):
    return crud.get_applications(
        db=db,
        skip=skip,
        limit=limit,
        status=application_status,
    )


@app.get("/applications/{application_id}", response_model=schemas.ApplicationResponse)
def read_application(application_id: int, db: Session = Depends(get_db)):
    db_application = crud.get_application(db=db, application_id=application_id)
    if db_application is None:
        raise HTTPException(status_code=404, detail="Application record not found")
    return db_application


@app.put(
    "/applications/{application_id}",
    response_model=schemas.ApplicationResponse,
    dependencies=[Depends(require_api_key)],
)
def update_application(
    application_id: int,
    application_update: schemas.ApplicationUpdate,
    db: Session = Depends(get_db),
):
    db_application = crud.update_application(
        db=db,
        application_id=application_id,
        application_update=application_update,
    )
    if db_application is None:
        raise HTTPException(status_code=404, detail="Application record not found")
    return db_application


@app.get("/keywords", response_model=list[schemas.KeywordResponse])
def read_keywords(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return crud.get_keywords(db=db, skip=skip, limit=limit)


@app.get("/reports/summary", response_model=schemas.SummaryReport)
def read_summary_report(db: Session = Depends(get_db)):
    return crud.get_summary_report(db=db)


@app.get("/reports/jobs-by-status", response_model=list[schemas.CountByLabel])
def read_jobs_by_status_report(db: Session = Depends(get_db)):
    return crud.get_jobs_by_status_report(db=db)


@app.get("/reports/jobs-by-company", response_model=list[schemas.CountByLabel])
def read_jobs_by_company_report(db: Session = Depends(get_db)):
    return crud.get_jobs_by_company_report(db=db)


@app.get("/reports/keyword-frequency", response_model=list[schemas.CountByLabel])
def read_keyword_frequency_report(db: Session = Depends(get_db)):
    return crud.get_keyword_frequency_report(db=db)


@app.get("/reports/salary-summary", response_model=schemas.SalarySummary)
def read_salary_summary_report(db: Session = Depends(get_db)):
    return crud.get_salary_summary_report(db=db)


@app.get(
    "/reports/upcoming-deadlines",
    response_model=list[schemas.JobResponse],
)
def read_upcoming_deadlines_report(
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return crud.get_upcoming_deadlines_report(db=db, limit=limit)


def _require_job(db: Session, job_id: int):
    db_job = crud.get_job(db=db, job_id=job_id)
    if db_job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return db_job
