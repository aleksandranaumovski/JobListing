from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.job import Job, Source
from app.services.normalization import (
    current_date,
    first_city,
    infer_category,
    infer_employment_type,
    parse_date,
    parse_datetime,
    stable_key,
)


def _load_json_variants(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8-sig")
    try:
        return [json.loads(text)]
    except json.JSONDecodeError:
        pass

    variants: list[dict[str, Any]] = []
    if "<<<<<<<" in text:
        lines = text.splitlines()
        separator = next((i for i, line in enumerate(lines) if line.startswith("=======")), None)
        end = next((i for i, line in enumerate(lines) if line.startswith(">>>>>>>")), None)

        if separator:
            head_lines = [line for line in lines[:separator] if not line.startswith("<<<<<<<")]
            head = "\n".join(head_lines).strip()
            if head and not head.endswith("}"):
                head = head.rstrip().rstrip(",") + "\n    }\n  ]\n}"
            try:
                variants.append(json.loads(head))
            except json.JSONDecodeError:
                pass

        if separator is not None and end is not None:
            other = "\n".join(lines[separator + 1 : end] + lines[end + 1 :]).strip()
            try:
                variants.append(json.loads(other))
            except json.JSONDecodeError:
                pass

    return variants


def _source_name(path: Path, payload: dict[str, Any]) -> str:
    if "KarieraMk" in path.parts:
        return "kariera.mk"
    if "Scrapping_Jobs" in path.parts:
        return "jobs.com.mk"
    if "Agencija" in path.parts:
        return "mkjob.com"
    source = payload.get("source")
    return str(source).replace("https://", "").replace("http://", "").strip("/") if source else path.parent.name


def _base_url(source_name: str, payload: dict[str, Any]) -> str | None:
    if payload.get("source"):
        return str(payload["source"])
    if source_name == "kariera.mk":
        return "https://kariera.mk"
    if source_name == "jobs.com.mk":
        return "https://jobs.com.mk"
    if source_name == "mkjob.com":
        return "https://www.mkjob.com"
    return None


def _canonical_url(url: str | None, base_url: str | None) -> str | None:
    if not url:
        return None
    if url.startswith("http"):
        return url
    if base_url:
        return base_url.rstrip("/") + "/" + url.lstrip("/")
    return url


def _normalize_job(raw: dict[str, Any], source: Source, file_scraped_at: str | None) -> tuple[dict[str, Any] | None, str | None]:
    title = (raw.get("title") or "").strip()
    if not title:
        return None, None

    raw_text = raw.get("raw_text") or raw.get("raw")
    location = raw.get("location")
    city = first_city(raw.get("city") or location, f"{title} {raw_text or ''}")
    url = _canonical_url(raw.get("url"), source.base_url)
    source_job_id = str(raw.get("id")) if raw.get("id") else None
    source_key = source_job_id or url or stable_key(source.name, title, city, raw_text)

    posted_at = parse_date(raw.get("posted_date") or raw.get("date_posted"))
    if not posted_at and raw_text:
        posted_match = re.search(r"(\d{1,2}\s+[А-Яа-яЃѓЌќ]+\s+\d{4})", raw_text)
        posted_at = parse_date(posted_match.group(1)) if posted_match else None

    active_until = parse_date(raw.get("active_until") or raw.get("valid_until"))
    if active_until and active_until < current_date(get_settings().scheduler_timezone):
        return None, "expired"

    return {
        "source_id": source.id,
        "source_key": source_key[:700],
        "source_job_id": source_job_id,
        "title": title[:500],
        "company": raw.get("company"),
        "city": city,
        "location": str(location) if location else city,
        "category": infer_category(title, raw_text),
        "employment_type": infer_employment_type(title, raw_text, str(location) if location else None),
        "url": url,
        "posted_at": posted_at,
        "active_until": active_until,
        "salary": raw.get("salary"),
        "is_new": bool(raw.get("is_new") or title.startswith("Ново")),
        "raw_text": raw_text,
        "source_payload": raw,
        "scraped_at": parse_datetime(raw.get("scraped_at") or file_scraped_at),
    }, None


def _get_or_create_source(db: Session, name: str, base_url: str | None) -> Source:
    source = db.query(Source).filter(Source.name == name).one_or_none()
    if source:
        if base_url and not source.base_url:
            source.base_url = base_url
            db.flush()
        return source
    source = Source(name=name, base_url=base_url)
    db.add(source)
    db.flush()
    return source


def import_json_files(db: Session, data_dir: Path) -> dict[str, int]:
    stats = {"files": 0, "seen": 0, "skipped_expired": 0, "inserted_or_updated": 0, "deleted_expired": 0}
    today = current_date(get_settings().scheduler_timezone)
    for path in sorted(data_dir.rglob("*.json")):
        payloads = _load_json_variants(path)
        if not payloads:
            continue
        stats["files"] += 1
        for payload in payloads:
            jobs = payload.get("jobs", payload if isinstance(payload, list) else [])
            if not jobs:
                continue
            source_name = _source_name(path, payload)
            source = _get_or_create_source(db, source_name, _base_url(source_name, payload))
            rows = []
            for raw in jobs:
                if not isinstance(raw, dict):
                    continue
                row, skipped_reason = _normalize_job(raw, source, payload.get("scraped_at"))
                if skipped_reason == "expired":
                    stats["skipped_expired"] += 1
                if row:
                    rows.append(row)
            stats["seen"] += len(rows)
            for row in rows:
                stmt = insert(Job).values(**row)
                update_values = {key: stmt.excluded[key] for key in row if key not in {"source_id", "source_key"}}
                db.execute(stmt.on_conflict_do_update(index_elements=["source_id", "source_key"], set_=update_values))
            stats["inserted_or_updated"] += len(rows)

    deleted = (
        db.query(Job)
        .filter(Job.active_until.is_not(None), Job.active_until < today)
        .delete(synchronize_session=False)
    )
    stats["deleted_expired"] = deleted
    db.commit()
    return stats
