from math import ceil

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import asc, desc, func, or_, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.job import Job, Source
from app.schemas.job import FiltersRead, JobDetail, JobPage, JobRead, PageMeta
from app.core.config import get_settings
from app.services.normalization import current_date

router = APIRouter(prefix="/jobs", tags=["jobs"])


def _to_read(job: Job) -> JobRead:
    return JobRead(
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
    )


@router.get("", response_model=JobPage, summary="List jobs")
def list_jobs(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=100),
    q: str | None = Query(None, description="Full text search across title, company, city and raw text"),
    title: str | None = None,
    company: str | None = None,
    city: str | None = None,
    category: str | None = None,
    employment_type: str | None = None,
    sort: str = Query("newest", pattern="^(newest|oldest)$"),
) -> JobPage:
    today = current_date(get_settings().scheduler_timezone)
    filters = [or_(Job.active_until.is_(None), Job.active_until >= today)]
    if q:
        search_vector = func.to_tsvector(
            "simple",
            func.coalesce(Job.title, "")
            + " "
            + func.coalesce(Job.company, "")
            + " "
            + func.coalesce(Job.city, "")
            + " "
            + func.coalesce(Job.raw_text, ""),
        )
        term = f"%{q}%"
        filters.append(
            or_(
                search_vector.op("@@")(func.websearch_to_tsquery("simple", q)),
                Job.title.ilike(term),
                Job.company.ilike(term),
            )
        )
    if title:
        filters.append(Job.title.ilike(f"%{title}%"))
    if company:
        filters.append(Job.company.ilike(f"%{company}%"))
    if city:
        filters.append(Job.city == city)
    if category:
        filters.append(Job.category == category)
    if employment_type:
        filters.append(Job.employment_type == employment_type)

    base = select(Job).join(Job.source)
    count_query = select(func.count(Job.id))
    if filters:
        base = base.where(*filters)
        count_query = count_query.where(*filters)

    order_column = func.coalesce(Job.posted_at, func.date(Job.scraped_at), func.date(Job.created_at))
    base = base.order_by(desc(order_column) if sort == "newest" else asc(order_column), desc(Job.created_at))
    total = db.scalar(count_query) or 0
    jobs = db.scalars(base.offset((page - 1) * page_size).limit(page_size)).all()
    return JobPage(items=[_to_read(job) for job in jobs], meta=PageMeta(page=page, page_size=page_size, total=total, pages=ceil(total / page_size) if total else 0))


@router.get("/filters", response_model=FiltersRead, summary="List available filter values")
def filters(db: Session = Depends(get_db)) -> FiltersRead:
    def values(column):
        return list(db.scalars(select(column).where(column.is_not(None)).distinct().order_by(column)).all())

    return FiltersRead(
        cities=values(Job.city),
        companies=values(Job.company),
        categories=values(Job.category),
        employment_types=values(Job.employment_type),
    )


@router.get("/{job_id}", response_model=JobDetail, summary="Job details")
def job_details(job_id: str, db: Session = Depends(get_db)) -> JobDetail:
    today = current_date(get_settings().scheduler_timezone)
    job = db.get(Job, job_id)
    if not job or (job.active_until and job.active_until < today):
        raise HTTPException(status_code=404, detail="Job not found")
    data = _to_read(job).model_dump()
    return JobDetail(**data, raw_text=job.raw_text, source_payload=job.source_payload)
