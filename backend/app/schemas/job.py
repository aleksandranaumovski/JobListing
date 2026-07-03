from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class JobRead(BaseModel):
    id: str
    source: str
    title: str
    company: str | None = None
    city: str | None = None
    location: str | None = None
    category: str | None = None
    employment_type: str | None = None
    url: str | None = None
    posted_at: date | None = None
    active_until: date | None = None
    salary: str | None = None
    is_new: bool = False
    scraped_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class JobDetail(JobRead):
    raw_text: str | None = None
    source_payload: dict = Field(default_factory=dict)


class PageMeta(BaseModel):
    page: int
    page_size: int
    total: int
    pages: int


class JobPage(BaseModel):
    items: list[JobRead]
    meta: PageMeta


class FiltersRead(BaseModel):
    cities: list[str]
    companies: list[str]
    categories: list[str]
    employment_types: list[str]
