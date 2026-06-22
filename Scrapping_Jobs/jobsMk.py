import argparse
import json
import time
from datetime import datetime
from typing import List, Dict

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout


BASE_URL = "https://jobs.com.mk"


# ─── URL BUILDER ──────────────────────────────────────────────────────────────

def build_url(page: int = 1, keyword: str = "") -> str:
    url = BASE_URL

    params = []
    if keyword:
        params.append(f"s={keyword.replace(' ', '+')}")
    if page > 1:
        params.append(f"page={page}")

    if params:
        url += "?" + "&".join(params)

    return url


# ─── PARSER ───────────────────────────────────────────────────────────────────

def parse_jobs(html: str) -> List[Dict]:
    soup = BeautifulSoup(html, "html.parser")
    jobs = []

    # Jobs.com.mk нема стабилни класи → користиме повеќе fallback-и
    cards = (
        soup.select("article")
        or soup.select("div.job")
        or soup.select("div[class*='job']")
        or soup.select("div")
    )

    for card in cards:
        text = card.get_text(" ", strip=True)

        # филтер за да избегнеме random div-ови
        if "Аплицирај" not in text and "Apply" not in text:
            continue

        # ── Title ──
        title_el = (
            card.find("h2")
            or card.find("h3")
            or card.find("a")
        )

        title = title_el.get_text(strip=True) if title_el else None

        # ── URL ──
        link_el = card.find("a", href=True)
        url = None
        if link_el:
            href = link_el["href"]
            url = href if href.startswith("http") else BASE_URL + href

        # ── Location (heuristic) ──
        location = None
        for word in text.split():
            if word in ["Скопје", "Bitola", "Kumanovo", "Tetovo", "Охрид"]:
                location = word
                break

        # ── Date (rough detection) ──
        date_posted = None
        if "ден" in text or "day" in text:
            date_posted = text

        if title:
            jobs.append({
                "title": title,
                "url": url,
                "location": location,
                "date_posted": date_posted,
                "raw_text": text[:300]
            })

    return jobs


# ─── TOTAL PAGES ──────────────────────────────────────────────────────────────

def get_total_pages(html: str) -> int:
    soup = BeautifulSoup(html, "html.parser")

    pages = soup.select("a")

    numbers = []
    for p in pages:
        txt = p.get_text(strip=True)
        if txt.isdigit():
            numbers.append(int(txt))

    return max(numbers) if numbers else 1


# ─── SCRAPER ──────────────────────────────────────────────────────────────────

def scrape(max_pages: int = 5, keyword: str = "", headless: bool = True):
    all_jobs = []
    seen = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context()
        page = context.new_page()

        total_pages = max_pages

        for page_num in range(1, max_pages + 1):
            url = build_url(page_num, keyword)
            print(f"[{page_num}] Fetching {url}")

            try:
                page.goto(url, timeout=30000)
                page.wait_for_load_state("networkidle")
                time.sleep(2)
            except PlaywrightTimeout:
                print("Timeout, skipping...")
                continue

            html = page.content()

            if page_num == 1:
                detected = get_total_pages(html)
                total_pages = min(detected, max_pages)
                print(f"Detected {detected} pages (scraping {total_pages})")

            jobs = parse_jobs(html)
            print(f"Found {len(jobs)} jobs")

            for job in jobs:
                key = job.get("url") or job["title"]
                if key not in seen:
                    seen.add(key)
                    all_jobs.append(job)

        browser.close()

    print(f"\nTotal jobs: {len(all_jobs)}")
    return all_jobs


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pages", type=int, default=5)
    parser.add_argument("--keyword", type=str, default="")
    parser.add_argument("--output", type=str, default="jobs.json")
    parser.add_argument("--no-headless", action="store_true")

    args = parser.parse_args()

    jobs = scrape(
        max_pages=args.pages,
        keyword=args.keyword,
        headless=not args.no_headless
    )

    data = {
        "scraped_at": datetime.now().isoformat(),
        "keyword": args.keyword,
        "total_jobs": len(jobs),
        "jobs": jobs
    }

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\nSaved to {args.output}")

    print("\nPreview:")
    for j in jobs[:5]:
        print(f"• {j['title']} ({j['location']})")


if __name__ == "__main__":
    main()