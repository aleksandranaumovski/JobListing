from datetime import date, datetime
import hashlib
import re
from zoneinfo import ZoneInfo


MACEDONIAN_MONTHS = {
    "јануари": 1,
    "февруари": 2,
    "март": 3,
    "април": 4,
    "мај": 5,
    "јуни": 6,
    "јули": 7,
    "август": 8,
    "септември": 9,
    "октомври": 10,
    "ноември": 11,
    "декември": 12,
}

CITIES = [
    "Скопје", "Битола", "Штип", "Тетово", "Куманово", "Охрид", "Гостивар",
    "Прилеп", "Велес", "Кочани", "Струмица", "Кавадарци", "Гевгелија",
    "Крушево", "Remote", "Цела Македонија",
]

CATEGORY_RULES = {
    "Информатичка технологија": ["developer", "програмер", "software", "data", "engineer", "инженер", "it ", "qa", "devops"],
    "Продажба": ["продаж", "sales", "касир", "комерцијал"],
    "Маркетинг": ["marketing", "маркетинг", "social media"],
    "Финансии": ["сметковод", "финанс", "кредит", "банкар", "плата"],
    "Администрација": ["админист", "office", "координатор", "асистент"],
    "Логистика": ["возач", "дистрибутер", "магацин", "логист"],
    "Здравство": ["медицин", "фармац", "доктор"],
    "Угостителство": ["келнер", "готвач", "бариста", "кујна"],
}

EMPLOYMENT_RULES = {
    "Full-time": ["full-time", "full time", "полно работно", "целосно"],
    "Part-time": ["part-time", "part time", "скратено"],
    "Internship": ["intern", "практикант", "приправник"],
    "Remote": ["remote", "далечина"],
}


def parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def parse_date(value: str | None) -> date | None:
    if not value:
        return None
    value = value.strip()
    for fmt in ("%d.%m.%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            pass
    match = re.search(r"(\d{1,2})\s+([А-Яа-яЃѓЌќ]+)\s+(\d{4})", value)
    if match:
        day, month_name, year = match.groups()
        month = MACEDONIAN_MONTHS.get(month_name.lower())
        if month:
            return date(int(year), month, int(day))
    return None


def current_date(timezone: str = "Europe/Skopje") -> date:
    return datetime.now(ZoneInfo(timezone)).date()


def first_city(value: object, fallback_text: str = "") -> str | None:
    if isinstance(value, list) and value:
        return str(value[0])
    if isinstance(value, str) and value.strip():
        return value.strip()
    haystack = fallback_text or ""
    for city in CITIES:
        if re.search(rf"\b{re.escape(city)}\b", haystack, flags=re.IGNORECASE):
            return city
    return None


def infer_category(title: str, raw_text: str | None = None) -> str | None:
    text = f"{title} {raw_text or ''}".lower()
    for category, needles in CATEGORY_RULES.items():
        if any(needle in text for needle in needles):
            return category
    return None


def infer_employment_type(title: str, raw_text: str | None = None, location: str | None = None) -> str | None:
    text = f"{title} {raw_text or ''} {location or ''}".lower()
    for employment_type, needles in EMPLOYMENT_RULES.items():
        if any(needle in text for needle in needles):
            return employment_type
    return None


def stable_key(*parts: object) -> str:
    text = "|".join("" if part is None else str(part) for part in parts)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
