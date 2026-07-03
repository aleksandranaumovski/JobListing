from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db
from app.services.importer import import_json_files
from app.services.scheduler import run_daily_scraping, scheduler
from app.services.scraper_runner import run_scraper

router = APIRouter(prefix="/admin", tags=["admin"])


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
