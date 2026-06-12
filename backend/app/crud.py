from datetime import date
from typing import Optional

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from . import models, schemas


def create_job(db: Session, job: schemas.JobCreate):
    db_job = models.Job(
        company_name=job.company_name,
        job_title=job.job_title,
        location=job.location,
        salary_min=job.salary_min,
        salary_max=job.salary_max,
        job_description=job.job_description,
        source_url=job.source_url or "",
        application_deadline=job.application_deadline,
    )

    db.add(db_job)
    db.flush()

    db.add(models.Application(job_id=db_job.job_id))
    for keyword in _clean_keywords(job.keywords):
        db.add(models.Keyword(job_id=db_job.job_id, keyword=keyword))

    db.commit()
    db.refresh(db_job)

    return db_job


def get_jobs(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    company: Optional[str] = None,
    title: Optional[str] = None,
    location: Optional[str] = None,
    status: Optional[str] = None,
    deadline_from: Optional[date] = None,
    deadline_to: Optional[date] = None,
    salary_min: Optional[float] = None,
    salary_max: Optional[float] = None,
    keyword: Optional[str] = None,
):
    query = db.query(models.Job)

    if company:
        query = query.filter(models.Job.company_name.ilike(f"%{company}%"))
    if title:
        query = query.filter(models.Job.job_title.ilike(f"%{title}%"))
    if location:
        query = query.filter(models.Job.location.ilike(f"%{location}%"))
    if deadline_from:
        query = query.filter(models.Job.application_deadline >= deadline_from)
    if deadline_to:
        query = query.filter(models.Job.application_deadline <= deadline_to)
    if salary_min is not None:
        query = query.filter(
            or_(
                models.Job.salary_max >= salary_min,
                models.Job.salary_min >= salary_min,
            )
        )
    if salary_max is not None:
        query = query.filter(
            or_(
                models.Job.salary_min <= salary_max,
                models.Job.salary_max <= salary_max,
            )
        )

    if status:
        query = query.outerjoin(models.Application)
        query = query.filter(
            func.coalesce(models.Application.status, "Not Applied").ilike(
                f"%{status}%"
            )
        )

    if keyword:
        query = query.join(models.Keyword)
        query = query.filter(models.Keyword.keyword.ilike(f"%{keyword}%"))

    return (
        query.distinct()
        .order_by(models.Job.date_found.desc(), models.Job.job_id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_job(db: Session, job_id: int):
    return db.query(models.Job).filter(models.Job.job_id == job_id).first()


def update_job(db: Session, job_id: int, job_update: schemas.JobUpdate):
    db_job = get_job(db, job_id)
    if db_job is None:
        return None

    update_data = job_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_job, key, value if key != "source_url" or value is not None else "")

    db.commit()
    db.refresh(db_job)
    return db_job


def get_application(db: Session, application_id: int):
    return (
        db.query(models.Application)
        .filter(models.Application.application_id == application_id)
        .first()
    )


def get_application_by_job_id(db: Session, job_id: int):
    return (
        db.query(models.Application)
        .filter(models.Application.job_id == job_id)
        .first()
    )


def get_applications(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
):
    query = db.query(models.Application)
    if status:
        query = query.filter(models.Application.status.ilike(f"%{status}%"))

    return (
        query.order_by(
            models.Application.last_updated.desc(),
            models.Application.application_id.desc(),
        )
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_application(db: Session, application: schemas.ApplicationCreate):
    db_application = models.Application(**application.model_dump())
    db.add(db_application)
    db.commit()
    db.refresh(db_application)
    return db_application


def update_application(
    db: Session,
    application_id: int,
    application_update: schemas.ApplicationUpdate,
):
    db_application = get_application(db, application_id)
    if db_application is None:
        return None

    _apply_application_update(db_application, application_update)
    db.commit()
    db.refresh(db_application)
    return db_application


def upsert_application_for_job(
    db: Session,
    job_id: int,
    application_update: schemas.ApplicationUpdate,
):
    db_application = get_application_by_job_id(db, job_id)
    if db_application is None:
        db_application = models.Application(job_id=job_id)
        db.add(db_application)
        db.flush()

    _apply_application_update(db_application, application_update)
    db.commit()
    db.refresh(db_application)
    return db_application


def get_keywords(db: Session, skip: int = 0, limit: int = 100):
    return (
        db.query(models.Keyword)
        .order_by(models.Keyword.keyword.asc(), models.Keyword.keyword_id.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_keywords_for_job(db: Session, job_id: int):
    return (
        db.query(models.Keyword)
        .filter(models.Keyword.job_id == job_id)
        .order_by(models.Keyword.keyword.asc(), models.Keyword.keyword_id.asc())
        .all()
    )


def add_keyword_to_job(db: Session, job_id: int, keyword: schemas.KeywordCreate):
    cleaned_keyword = keyword.keyword.strip()
    existing_keyword = (
        db.query(models.Keyword)
        .filter(models.Keyword.job_id == job_id)
        .filter(func.lower(models.Keyword.keyword) == cleaned_keyword.lower())
        .first()
    )
    if existing_keyword:
        return existing_keyword

    db_keyword = models.Keyword(job_id=job_id, keyword=cleaned_keyword)
    db.add(db_keyword)
    db.commit()
    db.refresh(db_keyword)
    return db_keyword


def get_summary_report(db: Session):
    today = date.today()
    total_jobs = db.query(models.Job).count()
    total_applications = db.query(models.Application).count()
    jobs_without_application_record = (
        db.query(models.Job)
        .outerjoin(models.Application)
        .filter(models.Application.application_id.is_(None))
        .count()
    )
    active_applications = (
        db.query(models.Application)
        .filter(func.lower(models.Application.status) != "not applied")
        .count()
    )
    unique_companies = db.query(models.Job.company_name).distinct().count()
    total_keywords = db.query(models.Keyword).count()
    upcoming_deadlines = (
        db.query(models.Job)
        .filter(models.Job.application_deadline >= today)
        .count()
    )
    overdue_deadlines = (
        db.query(models.Job)
        .filter(models.Job.application_deadline < today)
        .count()
    )

    return {
        "total_jobs": total_jobs,
        "total_applications": total_applications,
        "jobs_without_application_record": jobs_without_application_record,
        "active_applications": active_applications,
        "unique_companies": unique_companies,
        "total_keywords": total_keywords,
        "upcoming_deadlines": upcoming_deadlines,
        "overdue_deadlines": overdue_deadlines,
    }


def get_jobs_by_status_report(db: Session):
    status_label = func.coalesce(models.Application.status, "Not Applied").label(
        "label"
    )
    rows = (
        db.query(status_label, func.count(models.Job.job_id).label("count"))
        .outerjoin(models.Application)
        .group_by(status_label)
        .order_by(func.count(models.Job.job_id).desc(), status_label.asc())
        .all()
    )
    return [{"label": row.label, "count": row.count} for row in rows]


def get_jobs_by_company_report(db: Session):
    rows = (
        db.query(models.Job.company_name.label("label"), func.count().label("count"))
        .group_by(models.Job.company_name)
        .order_by(func.count().desc(), models.Job.company_name.asc())
        .all()
    )
    return [{"label": row.label, "count": row.count} for row in rows]


def get_keyword_frequency_report(db: Session):
    keyword_label = func.lower(models.Keyword.keyword).label("label")
    rows = (
        db.query(keyword_label, func.count(models.Keyword.keyword_id).label("count"))
        .group_by(keyword_label)
        .order_by(func.count(models.Keyword.keyword_id).desc(), keyword_label.asc())
        .all()
    )
    return [{"label": row.label, "count": row.count} for row in rows]


def get_salary_summary_report(db: Session):
    row = (
        db.query(
            func.count(models.Job.salary_min).label("jobs_with_salary_min"),
            func.count(models.Job.salary_max).label("jobs_with_salary_max"),
            func.avg(models.Job.salary_min).label("average_salary_min"),
            func.avg(models.Job.salary_max).label("average_salary_max"),
            func.min(models.Job.salary_min).label("lowest_salary_min"),
            func.max(models.Job.salary_max).label("highest_salary_max"),
        )
        .first()
    )
    return {
        "jobs_with_salary_min": row.jobs_with_salary_min,
        "jobs_with_salary_max": row.jobs_with_salary_max,
        "average_salary_min": row.average_salary_min,
        "average_salary_max": row.average_salary_max,
        "lowest_salary_min": row.lowest_salary_min,
        "highest_salary_max": row.highest_salary_max,
    }


def get_upcoming_deadlines_report(db: Session, limit: int = 10):
    return (
        db.query(models.Job)
        .filter(models.Job.application_deadline >= date.today())
        .order_by(models.Job.application_deadline.asc(), models.Job.job_id.desc())
        .limit(limit)
        .all()
    )


def _clean_keywords(keywords: list[str]):
    cleaned_keywords = []
    seen_keywords = set()
    for keyword in keywords:
        cleaned_keyword = keyword.strip()
        normalized_keyword = cleaned_keyword.lower()
        if not cleaned_keyword or normalized_keyword in seen_keywords:
            continue

        cleaned_keywords.append(cleaned_keyword)
        seen_keywords.add(normalized_keyword)

    return cleaned_keywords


def _apply_application_update(
    db_application: models.Application,
    application_update: schemas.ApplicationUpdate,
):
    update_data = application_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_application, key, value)
