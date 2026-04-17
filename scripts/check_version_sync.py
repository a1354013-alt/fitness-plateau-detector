from __future__ import annotations

import json
import sys
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def main() -> int:
    root = _repo_root()
    version_json = json.loads((root / "version.json").read_text(encoding="utf-8"))
    expected = str(version_json.get("version") or "").strip()
    if not expected:
        sys.stderr.write("version.json is missing a non-empty 'version' field.\n")
        return 1

    frontend_pkg = json.loads((root / "frontend" / "package.json").read_text(encoding="utf-8"))
    frontend_version = str(frontend_pkg.get("version") or "").strip()
    if frontend_version != expected:
        sys.stderr.write(
            f"Version drift: frontend/package.json version={frontend_version!r} != version.json version={expected!r}\n"
        )
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

