# import argparse
# import json
# import time
# from datetime import datetime
#
# from bs4 import BeautifulSoup
# from playwright.sync_api import sync_playwright
#
#
# BASE_URL = "https://www.mkjob.com/"
#
#
# # ─────────────────────────────────────────────
# # SCROLL FUNCTION (loads dynamic content)
# # ─────────────────────────────────────────────
#
# def scroll_page(page, steps=6):
#     for _ in range(steps):
#         page.mouse.wheel(0, 3000)
#         time.sleep(2)
#
#
# # ─────────────────────────────────────────────
# # SMART PARSER (no fragile selectors)
# # ─────────────────────────────────────────────
#
# def parse_jobs(html):
#     soup = BeautifulSoup(html, "html.parser")
#     jobs = []
#
#     links = soup.find_all("a")
#
#     seen = set()
#
#     for a in links:
#         text = a.get_text(" ", strip=True)
#         href = a.get("href")
#
#         if not text or len(text) < 25:
#             continue
#
#         # filter noise
#         if "login" in text.lower() or "register" in text.lower():
#             continue
#
#         if text in seen:
#             continue
#
#         seen.add(text)
#
#         jobs.append({
#             "title": text,
#             "url": href
#         })
#
#     return jobs
#
#
# # ─────────────────────────────────────────────
# # SCRAPER
# # ─────────────────────────────────────────────
#
# def scrape(pages=3, headless=True):
#     all_jobs = []
#     seen_urls = set()
#
#     with sync_playwright() as p:
#         browser = p.chromium.launch(headless=headless)
#         page = browser.new_page()
#
#         print("Opening site...")
#         page.goto(BASE_URL)
#
#         # IMPORTANT: do NOT use networkidle (breaks on JS sites)
#         page.wait_for_selector("body")
#         time.sleep(5)
#
#         for i in range(pages):
#             print(f"\n[Page {i+1}] scrolling & scraping...")
#
#             scroll_page(page)
#
#             html = page.content()
#
#             # DEBUG (optional)
#             # print(html[:1000])
#
#             jobs = parse_jobs(html)
#
#             print(f"  Found candidates: {len(jobs)}")
#
#             for job in jobs:
#                 key = job["title"]
#
#                 if key not in seen_urls:
#                     seen_urls.add(key)
#                     all_jobs.append(job)
#
#         browser.close()
#
#     print(f"\nTotal jobs scraped: {len(all_jobs)}")
#     return all_jobs
#
#
# # ─────────────────────────────────────────────
# # MAIN
# # ─────────────────────────────────────────────
#
# def main():
#     parser = argparse.ArgumentParser()
#     parser.add_argument("--pages", type=int, default=3)
#     parser.add_argument("--output", type=str, default="mk_jobs.json")
#     parser.add_argument("--no-headless", action="store_true")
#
#     args = parser.parse_args()
#
#     jobs = scrape(
#         pages=args.pages,
#         headless=not args.no_headless
#     )
#
#     result = {
#         "scraped_at": datetime.now().isoformat(),
#         "source": BASE_URL,
#         "total_jobs": len(jobs),
#         "jobs": jobs
#     }
#
#     with open(args.output, "w", encoding="utf-8") as f:
#         json.dump(result, f, ensure_ascii=False, indent=2)
#
#     print(f"\nSaved to {args.output}")
#
#     print("\nPreview:")
#     for j in jobs[:5]:
#         print("•", j["title"])
#
#
# if __name__ == "__main__":
#     main()
# import json
# import time
# import re
# import argparse
# from datetime import datetime
#
# from bs4 import BeautifulSoup
# from playwright.sync_api import sync_playwright
#
# BASE_URL = "https://www.mkjob.com/"
#
# CITIES = [
#     "Скопје", "Штип", "Битола", "Тетово",
#     "Куманово", "Охрид", "Гостивар",
#     "Прилеп", "Велес", "Кочани"
# ]
#
#
# # ─────────────────────────────────────────────
# # CITY EXTRACTION (FIXED)
# # ─────────────────────────────────────────────
#
# def extract_city(text):
#     # најважно: најди најпрецизно по редослед
#     found = []
#     for city in CITIES:
#         if re.search(rf"\b{re.escape(city)}\b", text):
#             found.append(city)
#
#     return found if found else None
#
#
# def extract_posted_date(text):
#     match = re.search(r"Објавен на:\s*([0-9]{2}\.[0-9]{2}\.[0-9]{4})", text)
#     return match.group(1) if match else None
#
#
# def extract_valid_until(text):
#     match = re.search(r"Валиден до:\s*([0-9]{2}\.[0-9]{2}\.[0-9]{4})", text)
#     return match.group(1) if match else None
#
#
# def clean_title(text):
#     text = re.sub(r"Ново", "", text)
#     text = re.sub(r"Објавен на:.*?Валиден до:.*", "", text)
#     text = re.sub(r"\d+\s*дена", "", text)
#
#     for city in CITIES:
#         text = text.replace(city, "")
#
#     return " ".join(text.split()).strip()
#
#
# def parse_job(text):
#     return {
#         "title": clean_title(text),
#         "city": extract_city(text),
#         "posted_date": extract_posted_date(text),
#         "valid_until": extract_valid_until(text),
#         "raw": text
#     }
#
#
# # ─────────────────────────────────────────────
# # SCROLL
# # ─────────────────────────────────────────────
#
# def scroll_page(page):
#     for _ in range(6):
#         page.mouse.wheel(0, 3000)
#         time.sleep(1.5)
#
#
# # ─────────────────────────────────────────────
# # SCRAPER
# # ─────────────────────────────────────────────
#
# def scrape(pages=3, headless=True):
#     jobs = []
#     seen = set()
#
#     with sync_playwright() as p:
#         browser = p.chromium.launch(headless=headless)
#         page = browser.new_page()
#
#         print("Opening site...")
#         page.goto(BASE_URL, timeout=60000)
#         page.wait_for_selector("body")
#         time.sleep(4)
#
#         for i in range(pages):
#             print(f"\n[Page {i+1}] scraping...")
#
#             scroll_page(page)
#
#             soup = BeautifulSoup(page.content(), "html.parser")
#
#             # 🔥 FIX: земаме директно job cards ако постојат
#             cards = soup.find_all("a")
#
#             count = 0
#
#             for c in cards:
#                 text = c.get_text(" ", strip=True)
#
#                 if len(text) < 30:
#                     continue
#
#                 if "login" in text.lower():
#                     continue
#
#                 key = text[:80]
#                 if key in seen:
#                     continue
#                 seen.add(key)
#
#                 job = parse_job(text)
#
#                 if job["title"]:
#                     jobs.append(job)
#                     count += 1
#
#             print(f"  Found: {count}")
#
#         browser.close()
#
#     print(f"\nTotal jobs: {len(jobs)}")
#     return jobs
#
#
# # ─────────────────────────────────────────────
# # MAIN
# # ─────────────────────────────────────────────
#
# def main():
#     parser = argparse.ArgumentParser()
#     parser.add_argument("--pages", type=int, default=3)
#     parser.add_argument("--output", type=str, default="mkjobs_clean.json")
#     parser.add_argument("--no-headless", action="store_true")
#
#     args = parser.parse_args()
#
#     jobs = scrape(
#         pages=args.pages,
#         headless=not args.no_headless
#     )
#
#     result = {
#         "scraped_at": datetime.now().isoformat(),
#         "source": BASE_URL,
#         "total_jobs": len(jobs),
#         "jobs": jobs
#     }
#
#     with open(args.output, "w", encoding="utf-8") as f:
#         json.dump(result, f, ensure_ascii=False, indent=2)
#
#     print(f"\nSaved to {args.output}")
#
#     print("\nPreview:")
#     for j in jobs[:5]:
#         print(f"• {j['title']} | {j['city']} | {j['posted_date']}")
#
#
# if __name__ == "__main__":
#     main()
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json

BASE_URL = "https://www.mkjob.com/"


def scrape_jobs():
    jobs = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # ✔ FIX: не networkidle (тоа ти правеше timeout)
        page.goto(BASE_URL, wait_until="domcontentloaded")

        # ✔ чекај да се рендерира React/Next.js содржината
        page.wait_for_timeout(6000)

        # земи финален HTML
        soup = BeautifulSoup(page.content(), "html.parser")

        # ✔ job cards selector (fallback approach за динамични сајтови)
        cards = soup.find_all("div")

        for card in cards:
            text = card.get_text(" ", strip=True)

            # филтер: избегнувај navbar/footer/skeleton
            if len(text) < 30:
                continue

            if "Објави оглас" in text or "Најави се" in text:
                continue

            # image
            img_tag = card.find("img")
            image = img_tag["src"] if img_tag and img_tag.has_attr("src") else None

            # crude extraction (бидејќи нема clean HTML structure)
            parts = text.split(" ")

            title = text[:80]  # fallback title

            jobs.append({
                "title": title,
                "location": None,
                "days_posted": None,
                "image": image
            })

        browser.close()

    return jobs


if __name__ == "__main__":
    data = scrape_jobs()

    print(json.dumps(data, indent=4, ensure_ascii=False))