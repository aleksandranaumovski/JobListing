from app.core.config import get_settings
from app.db.session import SessionLocal
from app.services.importer import import_json_files


def main() -> None:
    settings = get_settings()
    if not settings.seed_data_dir.exists():
        print(f"Seed data directory not found: {settings.seed_data_dir}")
        return
    with SessionLocal() as db:
        stats = import_json_files(db, settings.seed_data_dir)
        print(f"Seed import complete: {stats}")


if __name__ == "__main__":
    main()
