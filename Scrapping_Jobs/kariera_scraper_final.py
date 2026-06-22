"""
kariera.mk Final Scraper — requests + BeautifulSoup
=====================================================
Стратегија (откриена од мрежна анализа):
  1. GET https://kariera.mk/vrabotuvanje  → парсира li[data-id] во thumbgalleries
  2. POST https://kariera.mk/APICalls.aspx/JobsLazy → lazy-load уште огласи
     Body: {"hash": "<hash од data-hash атрибутот>"}

БЕЗ Playwright. Само requests + BeautifulSoup. Брзо и едноставно.

Setup:
    pip install requests beautifulsoup4

Usage:
    python kariera_scraper_final.py
    python kariera_scraper_final.py --output jobs.json
    python kariera_scraper_final.py --location 59   # 59=Скопје
    python kariera_scraper_final.py --position 4    # 4=Програмер
    python kariera_scraper_final.py --all-lazy      # вчитај ги сите lazy страни
"""

import argparse
import json
import time
import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://kariera.mk"
MAIN_URL = "https://kariera.mk/vrabotuvanje"
LAZY_URL  = "https://kariera.mk/APICalls.aspx/JobsLazy"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "mk,en;q=0.9",
    "Referer": "https://kariera.mk/",
}

LAZY_HEADERS = {
    **HEADERS,
    "Content-Type": "application/json; charset=utf-8",
    "X-Requested-With": "XMLHttpRequest",
    "Accept": "application/json, text/javascript, */*; q=0.01",
}

# Локации (од dropdown на сајтот)
LOCATIONS = {
    "сите": -1, "скопје": 59, "охрид": 44, "цела македонија": 69,
    "струмица": 63, "битола": 3, "гевгелија": 20, "велес": 13,
    "куманово": 38, "тетово": 64, "штип": 66, "кавадарци": 30,
}

# Позиции (од dropdown)
POSITIONS = {
    "сите": -1, "програмер": 4, "менаџер": 37, "маркетинг": 43,
    "возач": 5, "економист": 6, "медицински": 2, "инженер": 21,
    "правник": 23, "дизајнер": 42, "hr": 39,
}


# ─── Парсирање на job картички ────────────────────────────────────────────────

def parse_job_card(li) -> dict | None:
    """Парсира еден <li data-id="..."> елемент."""
    job_id = li.get("data-id")
    if not job_id:
        return None

    # Линк и наслов
    a = li.select_one("a[href*='/job/']")
    if not a:
        return None

    href = a.get("href", "")
    title_el = a.select_one("h3")
    company_el = a.select_one("p.company")

    # Локација и датум од job-info
    info_el = li.select_one("p.job-info")
    location = None
    date_to = None
    salary = None

    if info_el:
        info_text = info_el.get_text(separator="|", strip=True)
        parts = [p.strip() for p in info_text.split("|") if p.strip()]

        for part in parts:
            if re.match(r"\d{2}\.\d{2}\.\d{4}", part):
                date_to = part
            elif "ден." in part or "EUR" in part or "MKD" in part:
                salary = part
            elif part and not any(c in part for c in ["активен", "плата", "од"]):
                if not location and len(part) < 40:
                    location = part

        # Побарај специфично span.date-to
        date_span = info_el.select_one("span.date-to")
        if date_span:
            val = date_span.get_text(strip=True)
            if re.match(r"\d{2}\.\d{2}\.\d{4}", val):
                date_to = val
            elif "ден." in val or "EUR" in val:
                salary = val

    is_new = bool(li.select_one(".new-job"))

    return {
        "id": job_id,
        "title": title_el.get_text(strip=True) if title_el else None,
        "company": company_el.get_text(strip=True) if company_el else None,
        "location": location,
        "active_until": date_to,
        "salary": salary,
        "is_new": is_new,
        "url": BASE_URL + href if href.startswith("/") else href,
        "scraped_at": datetime.now().isoformat(),
    }


def parse_jobs_from_html(html: str) -> tuple[list[dict], str | None]:
    """
    Парсира огласи и го враќа hash-от за lazy load.
    Враќа: (list_of_jobs, lazy_hash)
    """
    soup = BeautifulSoup(html, "html.parser")
    jobs = []

    for li in soup.select("li[data-id]"):
        job = parse_job_card(li)
        if job and job["title"]:
            jobs.append(job)

    # Земи го hash-от за lazy load
    lazy_div = soup.select_one("[data-hash]")
    lazy_hash = lazy_div.get("data-hash") if lazy_div else None

    return jobs, lazy_hash


# ─── HTTP повици ──────────────────────────────────────────────────────────────

def fetch_main_page(session: requests.Session, location_id: int = -1,
                    position_id: int = -1, keyword: str = "") -> tuple[list[dict], str | None]:
    """Вчитај ја главната страница и парсирај ги огласите."""
    params = {}
    if location_id != -1:
        params["location"] = location_id
    if position_id != -1:
        params["position"] = position_id
    if keyword:
        params["keywords"] = keyword

    print(f"GET {MAIN_URL} params={params}")
    resp = session.get(MAIN_URL, params=params, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    print(f"  Status: {resp.status_code}, Size: {len(resp.text):,} chars")

    return parse_jobs_from_html(resp.text)


def fetch_lazy(session: requests.Session, lazy_hash: str) -> tuple[list[dict], str | None]:
    """POST до JobsLazy за да вчита уште огласи."""
    payload = json.dumps({"hash": lazy_hash})
    print(f"POST {LAZY_URL} hash={lazy_hash}")

    resp = session.post(LAZY_URL, data=payload, headers=LAZY_HEADERS, timeout=15)
    resp.raise_for_status()
    print(f"  Status: {resp.status_code}, Size: {len(resp.text):,} chars")

    try:
        data = resp.json()
        html_fragment = data.get("d", "")
        jobs, next_hash = parse_jobs_from_html(html_fragment)
        return jobs, next_hash
    except Exception as e:
        print(f"  [WARN] Грешка при парсирање на lazy response: {e}")
        return [], None


# ─── Главна функција ──────────────────────────────────────────────────────────

def scrape(location_id: int = -1, position_id: int = -1,
           keyword: str = "", max_lazy: int = 5) -> list[dict]:
    """
    Scrape kariera.mk.
    max_lazy: максимален број lazy-load повици (секој ~24 огласи)
    """
    session = requests.Session()
    all_jobs = []
    seen_ids = set()

    def add_jobs(jobs):
        for job in jobs:
            if job["id"] not in seen_ids:
                seen_ids.add(job["id"])
                all_jobs.append(job)

    # 1. Главна страница
    jobs, lazy_hash = fetch_main_page(session, location_id, position_id, keyword)
    print(f"  Пронајдено: {len(jobs)} огласи (главна страница)")
    add_jobs(jobs)

    # 2. Lazy load повици
    lazy_count = 0
    while lazy_hash and lazy_count < max_lazy:
        time.sleep(1.0)  # пауза меѓу повици
        lazy_count += 1
        print(f"\nLazy load #{lazy_count}:")
        jobs, lazy_hash = fetch_lazy(session, lazy_hash)
        print(f"  Пронајдено: {len(jobs)} огласи")
        add_jobs(jobs)

        if not jobs:
            print("  Нема повеќе огласи.")
            break

    print(f"\nВкупно уникатни огласи: {len(all_jobs)}")
    return all_jobs


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="kariera.mk scraper (requests-based)")
    parser.add_argument("--location", type=int, default=-1,
                        help="Location ID (59=Скопје, 3=Битола, итн.)")
    parser.add_argument("--position", type=int, default=-1,
                        help="Position ID (4=Програмер, 37=Менаџер, итн.)")
    parser.add_argument("--keyword", type=str, default="",
                        help="Keyword за пребарување")
    parser.add_argument("--lazy", type=int, default=5,
                        help="Број на lazy-load повици (default: 5, ~120 огласи)")
    parser.add_argument("--all-lazy", action="store_true",
                        help="Вчитај сите lazy страни (може да потрае)")
    parser.add_argument("--output", type=str, default="jobs.json")
    args = parser.parse_args()

    max_lazy = 999 if args.all_lazy else args.lazy

    print("kariera.mk Scraper (requests-based)")
    print(f"Location={args.location} | Position={args.position} | Keyword='{args.keyword}'")
    print(f"Max lazy loads: {'∞' if args.all_lazy else max_lazy}")
    print("="*60)

    jobs = scrape(
        location_id=args.location,
        position_id=args.position,
        keyword=args.keyword,
        max_lazy=max_lazy,
    )

    result = {
        "scraped_at": datetime.now().isoformat(),
        "filters": {
            "location_id": args.location,
            "position_id": args.position,
            "keyword": args.keyword,
        },
        "total_jobs": len(jobs),
        "jobs": jobs,
    }

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\nЗачувано во: {args.output}")

    print("\nПреглед (први 5):")
    for job in jobs[:5]:
        new_tag = " [НОВ]" if job.get("is_new") else ""
        salary = f" | {job['salary']}" if job.get("salary") else ""
        print(f"  {job['title']}{new_tag}")
        print(f"    {job['company']} | {job['location']} | активен до: {job['active_until']}{salary}")

    print(f"\nДостапни location IDs:")
    for name, lid in LOCATIONS.items():
        print(f"  {lid}: {name}")
    print(f"\nДостапни position IDs:")
    for name, pid in POSITIONS.items():
        print(f"  {pid}: {name}")


if __name__ == "__main__":
    main()
