from math import ceil

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.core.config import get_settings
from app.db.session import get_db
from app.models.job import Job
from app.models.user import User
from app.schemas.job import ModeratedJobPage, ModeratedJobRead, PageMeta
from app.services.importer import import_json_files
from app.services.scheduler import run_daily_scraping, scheduler
from app.services.scraper_runner import run_scraper

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_admin)])


def _to_moderated(job: Job, submitter_email: str | None) -> ModeratedJobRead:
    return ModeratedJobRead(
        id=job.id,
        source=job.source.name,
        title=job.title,
        company=job.company,
        city=job.city,
        location=job.location,
        category=job.category,
        employment_type=job.employment_type,
        url=job.url,
        posted_at=job.posted_at,
        active_until=job.active_until,
        salary=job.salary,
        is_new=job.is_new,
        scraped_at=job.scraped_at,
        status=job.status,
        submitted_by=submitter_email,
        created_at=job.created_at,
    )


@router.get("/jobs", response_model=ModeratedJobPage, summary="List user-submitted jobs for moderation")
def moderation_queue(
    db: Session = Depends(get_db),
    status: str = Query("pending", pattern="^(pending|approved|rejected|all)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=100),
) -> ModeratedJobPage:
    filters = [Job.created_by_id.is_not(None)]
    if status != "all":
        filters.append(Job.status == status)
    total = db.scalar(select(func.count(Job.id)).where(*filters)) or 0
    rows = db.execute(
        select(Job, User.email)
        .join(User, Job.created_by_id == User.id, isouter=True)
        .where(*filters)
        .order_by(desc(Job.created_at))
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return ModeratedJobPage(
        items=[_to_moderated(job, email) for job, email in rows],
        meta=PageMeta(page=page, page_size=page_size, total=total, pages=ceil(total / page_size) if total else 0),
    )


def _set_status(db: Session, job_id: str, status: str) -> ModeratedJobRead:
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    job.status = status
    db.commit()
    db.refresh(job)
    submitter = db.get(User, job.created_by_id) if job.created_by_id else None
    return _to_moderated(job, submitter.email if submitter else None)


@router.post("/jobs/{job_id}/approve", response_model=ModeratedJobRead, summary="Approve a submitted job")
def approve_job(job_id: str, db: Session = Depends(get_db)) -> ModeratedJobRead:
    return _set_status(db, job_id, Job.STATUS_APPROVED)


@router.post("/jobs/{job_id}/reject", response_model=ModeratedJobRead, summary="Reject a submitted job")
def reject_job(job_id: str, db: Session = Depends(get_db)) -> ModeratedJobRead:
    return _set_status(db, job_id, Job.STATUS_REJECTED)


@router.post("/import", summary="Import all JSON seed files")
def import_seed_data(db: Session = Depends(get_db)):
    return import_json_files(db, get_settings().seed_data_dir)


@router.post("/scrape/{scraper_name}", summary="Run an existing scraper and import its output")
def scrape_and_import(scraper_name: str, limit: int = Query(3, ge=1, le=20), db: Session = Depends(get_db)):
    output = run_scraper(scraper_name, limit=limit)
    stats = import_json_files(db, output.parent)
    return {"output": str(output), "import": stats}


@router.post("/scrape-all", summary="Run all existing scrapers and import active advertisements")
def scrape_all():
    return run_daily_scraping()


@router.get("/scheduler", summary="Show scraper scheduler status")
def scheduler_status():
    jobs = [
        {"id": job.id, "name": job.name, "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None}
        for job in scheduler.get_jobs()
    ]
    return {"running": scheduler.running, "jobs": jobs}
