from pathlib import Path
import json
import subprocess
import sys

from app.core.config import get_settings


SCRAPERS = {
    "kariera": Path("Scrapping_KarieraMk/kariera_scraper_final.py"),
    "jobs": Path("Scrapping_Jobs/jobsMk.py"),
    "mkjob": Path("Scrapping_Agencija/mkJobs.py"),
}


def run_scraper(name: str, output_dir: Path | None = None, limit: int = 3) -> Path:
    settings = get_settings()
    if name not in SCRAPERS:
        raise ValueError(f"Unsupported scraper '{name}'. Available: {', '.join(SCRAPERS)}")
    script = settings.seed_data_dir / SCRAPERS[name]
    if not script.exists():
        raise FileNotFoundError(f"Scraper script not found: {script}")

    output_dir = output_dir or settings.scraper_data_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / f"{name}.json"

    if name == "kariera":
        args = [sys.executable, str(script), "--lazy", str(limit), "--output", str(output)]
    elif name == "jobs":
        args = [sys.executable, str(script), "--pages", str(limit), "--output", str(output)]
    else:
        args = [sys.executable, str(script)]
        completed = subprocess.run(args, cwd=str(script.parent), check=True, timeout=180, capture_output=True, text=True, encoding="utf-8")
        parsed = json.loads(completed.stdout)
        output.write_text(json.dumps(parsed, ensure_ascii=False, indent=2), encoding="utf-8")
        return output

    subprocess.run(args, cwd=str(script.parent), check=True, timeout=180)
    return output


def run_all_scrapers(output_dir: Path | None = None, limit: int = 3) -> list[Path]:
    return [run_scraper(name, output_dir=output_dir, limit=limit) for name in SCRAPERS]
