from __future__ import annotations

import logging
from threading import Lock

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.config import get_settings
from app.db.session import SessionLocal
from app.services.importer import import_json_files
from app.services.scraper_runner import SCRAPERS, run_scraper

logger = logging.getLogger(__name__)

_lock = Lock()
scheduler = AsyncIOScheduler()


def run_daily_scraping() -> dict:
    if not _lock.acquire(blocking=False):
        logger.info("Scheduled scraping skipped because a previous run is still active.")
        return {"status": "skipped", "reason": "already_running"}

    settings = get_settings()
    try:
        logger.info("Starting scheduled scraping run.")
        outputs = []
        errors = []
        for scraper_name in SCRAPERS:
            try:
                outputs.append(run_scraper(scraper_name, output_dir=settings.scraper_data_dir, limit=settings.scraper_default_limit))
            except Exception as exc:
                logger.exception("Scraper '%s' failed.", scraper_name)
                errors.append({"scraper": scraper_name, "error": str(exc)})

        with SessionLocal() as db:
            stats = import_json_files(db, settings.scraper_data_dir)
        result = {
            "status": "ok" if not errors else "partial",
            "outputs": [str(path) for path in outputs],
            "errors": errors,
            "import": stats,
        }
        logger.info("Scheduled scraping completed: %s", result)
        return result
    except Exception:
        logger.exception("Scheduled scraping failed.")
        raise
    finally:
        _lock.release()


def start_scheduler() -> None:
    settings = get_settings()
    if not settings.enable_scheduler:
        logger.info("Scraping scheduler disabled.")
        return
    if scheduler.running:
        return

    scheduler.configure(timezone=settings.scheduler_timezone)
    scheduler.add_job(
        run_daily_scraping,
        CronTrigger(
            hour=settings.scraper_schedule_hour,
            minute=settings.scraper_schedule_minute,
            timezone=settings.scheduler_timezone,
        ),
        id="daily_scraping",
        name="Daily website scraping",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
        misfire_grace_time=3600,
    )
    scheduler.start()
    logger.info(
        "Scraping scheduler started: daily at %02d:%02d %s.",
        settings.scraper_schedule_hour,
        settings.scraper_schedule_minute,
        settings.scheduler_timezone,
    )


def stop_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)
