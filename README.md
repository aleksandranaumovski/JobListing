# NVD Jobs

Full-stack job advertisement application built from the scraped JSON files and scraper scripts in this repository.

## Structure

- `Scrapping_Agencija/`, `Scrapping_Jobs/`, `Scrapping_KarieraMk/` original scraping scripts and seed JSON.
- `backend/` FastAPI, SQLAlchemy and Alembic application.
- `frontend/` Angular standalone-components application.
- `database/` PostgreSQL initialization.
- `docker/` Dockerfiles and Nginx config.

## Run

```bash
docker compose up --build
```

Then open:

- Frontend: http://localhost:4200
- API docs: http://localhost:8000/api/docs
- Health check: http://localhost:8000/api/health

The backend runs Alembic migrations and imports all JSON seed files on startup. The importer preserves each original advertisement in `jobs.source_payload` and normalizes common fields for search and filtering.

## API

- `GET /api/jobs` lists approved jobs with pagination, search, filters and `sort=newest|oldest`.
- `GET /api/jobs/{id}` returns details (pending/rejected jobs are visible only to their owner and admins).
- `GET /api/jobs/filters` returns available filter values.
- `POST /api/jobs` submits a new job advertisement (authenticated users; created with status `pending`).
- `GET /api/jobs/mine` lists the authenticated user's own submissions with their status.
- `POST /api/admin/import` re-imports JSON seed data (admin only).
- `POST /api/admin/scrape/{scraper_name}?limit=3` runs one existing scraper (`kariera`, `jobs`, `mkjob`) and imports the output (admin only).
- `POST /api/admin/scrape-all` runs all scraper integrations immediately (admin only).
- `GET /api/admin/scheduler` shows the daily scheduler status (admin only).

## Authentication & Moderation

The app has registered users and one bootstrapped admin account. Anyone can browse jobs; logged-in users can submit job advertisements, which appear publicly only after an admin approves them.

- `POST /api/auth/register` creates an account and returns a JWT access token.
- `POST /api/auth/login` logs in and returns a JWT access token.
- `GET /api/auth/me` returns the current user.
- `GET /api/admin/jobs?status=pending|approved|rejected|all` lists user-submitted jobs for moderation (admin only).
- `POST /api/admin/jobs/{id}/approve` / `POST /api/admin/jobs/{id}/reject` moderates a submission (admin only).

Send the token as `Authorization: Bearer <token>`. Scraped jobs are imported as `approved`; user submissions start as `pending`.

The admin account is created automatically on startup and is configured with environment variables (defaults shown):

- `ADMIN_EMAIL=admin@nvdjobs.mk`
- `ADMIN_PASSWORD=admin123`
- `JWT_SECRET=change-me-in-production`
- `ACCESS_TOKEN_EXPIRE_MINUTES=720`

Change `ADMIN_PASSWORD` and `JWT_SECRET` before deploying anywhere public.

Frontend pages: `/login`, `/register`, `/submit` (add a job), `/my-jobs` (own submissions and their status) and `/admin/approvals` (admin moderation queue).

## Scheduled Scraping

The backend starts a scheduler with Docker and runs all integrated website scrapers every day at `00:00` in the `Europe/Skopje` timezone. The schedule is controlled with:

- `ENABLE_SCHEDULER=true`
- `SCHEDULER_TIMEZONE=Europe/Skopje`
- `SCRAPER_SCHEDULE_HOUR=0`
- `SCRAPER_SCHEDULE_MINUTE=0`
- `SCRAPER_DEFAULT_LIMIT=5`

The importer skips advertisements whose known `active_until` date is already in the past and deletes expired rows from the database after each import. Records without an expiry date are kept because the source did not provide enough information to prove they ended.

## Data Model

The discovered source data has one canonical advertisement shape with source-specific optional fields:

- Kariera: `id`, `title`, `company`, `location`, `active_until`, `salary`, `is_new`, `url`, `scraped_at`.
- Jobs.com.mk: `title`, `url`, `location`, `date_posted`, `raw_text`.
- MKJob: `title`, `url`, or cleaned `title`, `city`, `posted_date`, `valid_until`, `raw`.

The relational schema uses:

- `sources`: source name and base URL.
- `jobs`: normalized searchable fields plus `source_payload` JSONB for the original scraped record.

Indexes are added for pagination, source lookup, city, company, category, employment type, posted date and a PostgreSQL full-text search vector.

## Development

Backend:

```bash
cd backend
pip install -r requirements.txt
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm start
```
