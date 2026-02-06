from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable, List, Optional

from app.utils import TIMESTAMP_FORMAT, ensure_dir, parse_timestamp


class LogManager:
    def __init__(self, log_dir: Path, retention_days: int) -> None:
        self.log_dir = log_dir
        self.retention_days = retention_days
        ensure_dir(self.log_dir)

    def create_log_file(self, timestamp: datetime) -> Path:
        ensure_dir(self.log_dir)
        filename = f"inference_{timestamp.strftime(TIMESTAMP_FORMAT)}.log"
        return self.log_dir / filename

    def prune_old_logs(self) -> List[Path]:
        cutoff = datetime.now() - timedelta(days=self.retention_days)
        removed: List[Path] = []
        for path in self.log_dir.glob("inference_*.log"):
            if datetime.fromtimestamp(path.stat().st_mtime) < cutoff:
                path.unlink(missing_ok=True)
                removed.append(path)
        return removed

    def read_logs(
        self, since: Optional[str] = None, tail: Optional[int] = None
    ) -> str:
        ensure_dir(self.log_dir)
        start_time = parse_timestamp(since) if since else None
        files = sorted(self.log_dir.glob("inference_*.log"))
        selected: Iterable[Path] = files
        if start_time:
            selected = [
                path
                for path in files
                if self._timestamp_from_name(path) and self._timestamp_from_name(path) >= start_time
            ]
        lines: List[str] = []
        for path in selected:
            try:
                lines.extend(path.read_text().splitlines())
            except FileNotFoundError:
                continue
        if tail is not None and tail >= 0:
            lines = lines[-tail:]
        return "\n".join(lines)

    def _timestamp_from_name(self, path: Path) -> Optional[datetime]:
        name = path.stem
        if not name.startswith("inference_"):
            return None
        raw = name[len("inference_") :]
        try:
            return parse_timestamp(raw)
        except ValueError:
            return None
