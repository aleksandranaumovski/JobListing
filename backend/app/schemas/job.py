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
    status: str = "approved"

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


class JobSubmissionCreate(BaseModel):
    title: str = Field(min_length=3, max_length=500)
    company: str = Field(min_length=1, max_length=300)
    city: str | None = Field(default=None, max_length=120)
    location: str | None = Field(default=None, max_length=250)
    category: str | None = Field(default=None, max_length=120)
    employment_type: str | None = Field(default=None, max_length=120)
    salary: str | None = Field(default=None, max_length=250)
    url: str | None = Field(default=None, max_length=1000)
    description: str | None = Field(default=None, max_length=20000)
    active_until: date | None = None


class ModeratedJobRead(JobRead):
    submitted_by: str | None = None
    created_at: datetime | None = None


class ModeratedJobPage(BaseModel):
    items: list[ModeratedJobRead]
    meta: PageMeta
