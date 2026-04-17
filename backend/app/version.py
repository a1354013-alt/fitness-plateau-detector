from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


@dataclass(frozen=True)
class VersionInfo:
    name: str
    version: str


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


@lru_cache(maxsize=1)
def get_version_info() -> VersionInfo:
    path = _repo_root() / "version.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    name = str(payload.get("name") or "PlateauBreaker").strip() or "PlateauBreaker"
    version = str(payload.get("version") or "0.0.0").strip() or "0.0.0"
    return VersionInfo(name=name, version=version)

