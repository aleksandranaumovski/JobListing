from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, select

from app.api.admin import router as admin_router
from app.api.auth import router as auth_router
from app.api.jobs import router as jobs_router
from app.core.config import get_settings
from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.user import ROLE_ADMIN, User
from app.services.scheduler import start_scheduler, stop_scheduler

settings = get_settings()


def ensure_admin_user() -> None:
    email = settings.admin_email.strip().lower()
    with SessionLocal() as db:
        admin = db.scalar(select(User).where(func.lower(User.email) == email))
        if not admin:
            db.add(
                User(
                    email=email,
                    full_name=settings.admin_full_name,
                    hashed_password=hash_password(settings.admin_password),
                    role=ROLE_ADMIN,
                )
            )
            db.commit()
        elif admin.role != ROLE_ADMIN:
            admin.role = ROLE_ADMIN
            db.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_admin_user()
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(title=settings.app_name, version="1.0.0", openapi_url="/api/openapi.json", docs_url="/api/docs", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api")
app.include_router(jobs_router, prefix="/api")
app.include_router(admin_router, prefix="/api")


@app.get("/api/health", tags=["health"])
def health():
    return {"status": "ok"}
