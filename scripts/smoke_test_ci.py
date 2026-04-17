from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from zoneinfo import ZoneInfo


REPO_ROOT = Path(__file__).resolve().parents[1]


def _http_json(method: str, url: str, payload: dict | None = None) -> tuple[int, dict]:
    data = None
    headers = {"Accept": "application/json"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = Request(url, data=data, method=method, headers=headers)
    try:
        with urlopen(req, timeout=5) as resp:
            raw = resp.read().decode("utf-8")
            return resp.status, json.loads(raw) if raw else {}
    except HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        return exc.code, {"_error": raw}


def _http_text(url: str) -> tuple[int, str]:
    req = Request(url, method="GET", headers={"Accept": "text/html"})
    try:
        with urlopen(req, timeout=5) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            return resp.status, raw
    except HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        return exc.code, raw


def _http_raw(url: str, *, accept: str) -> tuple[int, dict[str, str], str]:
    req = Request(url, method="GET", headers={"Accept": accept})
    try:
        with urlopen(req, timeout=5) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            return resp.status, dict(resp.headers), raw
    except HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        return exc.code, dict(exc.headers), raw


def _wait_for(url: str, *, timeout_s: int = 30) -> None:
    start = time.time()
    while True:
        try:
            status, _ = _http_json("GET", url)
            if status == 200:
                return
        except URLError:
            pass

        if time.time() - start > timeout_s:
            raise RuntimeError(f"Timed out waiting for {url}")
        time.sleep(0.25)


def _terminate(proc: subprocess.Popen) -> None:
    if proc.poll() is not None:
        return

    try:
        proc.send_signal(signal.SIGTERM)
        proc.wait(timeout=10)
    except Exception:
        proc.kill()
        proc.wait(timeout=10)


def main() -> int:
    backend_url = "http://127.0.0.1:8000"

    dist_dir = REPO_ROOT / "frontend" / "dist"
    if not dist_dir.exists():
        raise SystemExit("frontend/dist not found. Run `npm --prefix frontend run build` first.")

    db_path = Path(os.environ.get("RUNNER_TEMP", "/tmp")) / "plateaubreaker_integration.sqlite3"
    if db_path.exists():
        db_path.unlink()

    backend_env = os.environ.copy()
    backend_env["PLATEAUBREAKER_DB_PATH"] = str(db_path)
    backend_env.setdefault("APP_TIMEZONE", "Asia/Taipei")
    backend_env["PLATEAUBREAKER_FRONTEND_DIST_DIR"] = str(dist_dir.resolve())

    backend_proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "app.main:app",
            "--app-dir",
            "backend",
            "--host",
            "127.0.0.1",
            "--port",
            "8000",
        ],
        cwd=str(REPO_ROOT),
        env=backend_env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    try:
        start = time.time()
        while True:
            if backend_proc.poll() is not None:
                out = ""
                if backend_proc.stdout is not None:
                    try:
                        out = backend_proc.stdout.read()
                    except Exception:
                        out = ""
                raise RuntimeError(f"Backend exited before /health was ready.\n\n{out[-4000:]}")

            try:
                status, _ = _http_json("GET", f"{backend_url}/health")
                if status == 200:
                    break
            except URLError:
                pass

            if time.time() - start > 60:
                out = ""
                if backend_proc.stdout is not None:
                    try:
                        out = backend_proc.stdout.read()
                    except Exception:
                        out = ""
                raise RuntimeError(f"Timed out waiting for {backend_url}/health.\n\n{out[-4000:]}")

            time.sleep(0.25)

        # Create one record safely in the past under APP_TIMEZONE semantics.
        tz = ZoneInfo(backend_env["APP_TIMEZONE"])
        record_date = (datetime.now(timezone.utc).astimezone(tz).date() - timedelta(days=1)).isoformat()
        status, payload = _http_json(
            "POST",
            f"{backend_url}/api/health-records",
            {
                "record_date": record_date,
                "weight": 75.0,
                "sleep_hours": 7.0,
                "calories": 2000,
                "protein": 120,
                "exercise_minutes": 30,
                "exercise_type": "Walking",
                "steps": 8000,
                "note": "smoke",
            },
        )
        assert status == 201, payload
        assert str(payload.get("created_at", "")).endswith("Z")
        assert str(payload.get("updated_at", "")).endswith("Z")

        status, payload = _http_json("GET", f"{backend_url}/api/health-records")
        assert status == 200, payload
        assert payload.get("total", 0) >= 1

        status, payload = _http_json("GET", f"{backend_url}/api/analytics/summary?calorie_target=2000")
        assert status == 200, payload
        assert "summary" in payload and "plateau" in payload and "reasons" in payload

        # Backend serves SPA static files + history fallback.
        for path in ("/", "/records", "/analysis"):
            status, body = _http_text(f"{backend_url}{path}")
            assert status == 200, (path, status, body[:200])
            assert "<title>" in body, (path, body[:200])

        # /api/* must never be polluted by SPA fallback even when Accept prefers HTML.
        status, headers, body = _http_raw(f"{backend_url}/api/does-not-exist", accept="text/html")
        assert status == 404
        assert "application/json" in (headers.get("Content-Type") or headers.get("content-type") or "")
        assert "Not Found" in body
    finally:
        _terminate(backend_proc)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
