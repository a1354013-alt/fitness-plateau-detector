from __future__ import annotations

import argparse
from pathlib import Path
import zipfile


ALLOWED_PREFIXES = ("backend/", "frontend/dist/")
ALLOWED_ROOT_FILES = ("README.md",)

FORBIDDEN_SUBSTRINGS = (
    "/.git/",
    "/.idea/",
    "/.vscode/",
    "/.pytest_cache/",
    "/.mypy_cache/",
    "/.ruff_cache/",
    "/.venv/",
    "/venv/",
    "/node_modules/",
    "/.npm-cache/",
    "/__pycache__/",
    "/backend/tests/",
    "/backend/data/",
    "/.env",
    "/release/",
    "/release_tmp/",
)

REQUIRED_ENTRIES = (
    "README.md",
    "backend/requirements.txt",
    "backend/alembic.ini",
    "backend/alembic/env.py",
    "backend/alembic/versions/20260409_0001_initial.py",
    "frontend/dist/index.html",
)


def pick_latest_zip(out_dir: Path) -> Path:
    zips = sorted(out_dir.glob("*.zip"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not zips:
        raise SystemExit(f"No .zip found in: {out_dir}")
    return zips[0]


def validate_zip(path: Path) -> None:
    if not path.exists():
        raise SystemExit(f"Zip not found: {path}")

    with zipfile.ZipFile(path, "r") as zf:
        names = [n.replace("\\", "/") for n in zf.namelist()]

    missing = [e for e in REQUIRED_ENTRIES if e not in names]
    if missing:
        raise SystemExit(f"Release zip is missing required entries: {', '.join(missing)}")

    extra: list[str] = []
    for n in names:
        if n.endswith("/"):
            continue
        if n in ALLOWED_ROOT_FILES:
            continue
        if any(n.startswith(p) for p in ALLOWED_PREFIXES):
            continue
        extra.append(n)

    if extra:
        sample = ", ".join(sorted(extra)[:15])
        raise SystemExit(f"Release zip contains unexpected top-level content (sample): {sample}")

    violations: list[str] = []
    for n in names:
        normalized = f"/{n.lstrip('/')}"
        for bad in FORBIDDEN_SUBSTRINGS:
            if normalized.startswith(bad) or bad in normalized:
                violations.append(n)
                break

    if violations:
        sample = ", ".join(sorted(violations)[:15])
        raise SystemExit(f"Release zip contains forbidden content (sample): {sample}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate PlateauBreaker release zip contents.")
    parser.add_argument("--zip", dest="zip_path", default=None, help="Path to release zip.")
    parser.add_argument("--out-dir", default="release", help="Output directory (relative to repo root).")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    out_dir = (root / args.out_dir).resolve()

    zip_path = Path(args.zip_path).resolve() if args.zip_path else pick_latest_zip(out_dir)
    validate_zip(zip_path)
    print(f"OK: {zip_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
