from __future__ import annotations

from datetime import datetime
from pathlib import Path

TIMESTAMP_FORMAT = "%Y-%m-%d_%H:%M:%S"


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def safe_resolve(base_dir: Path, user_path: str) -> Path:
    if not user_path:
        raise ValueError("path is required")
    candidate = Path(user_path)
    if not candidate.is_absolute():
        candidate = base_dir / candidate
    candidate = candidate.resolve()
    if candidate != base_dir and base_dir not in candidate.parents:
        raise ValueError("path outside allowed directory")
    return candidate


def parse_timestamp(value: str) -> datetime:
    return datetime.strptime(value, TIMESTAMP_FORMAT)
