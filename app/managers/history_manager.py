from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import json

from app.utils import TIMESTAMP_FORMAT, ensure_dir


class HistoryManager:
    def __init__(self, history_file: Path) -> None:
        self.history_file = history_file
        ensure_dir(self.history_file.parent)

    def _load(self) -> List[Dict[str, Optional[str]]]:
        if not self.history_file.exists():
            return []
        try:
            return json.loads(self.history_file.read_text())
        except json.JSONDecodeError:
            return []

    def _save(self, items: List[Dict[str, Optional[str]]]) -> None:
        ensure_dir(self.history_file.parent)
        self.history_file.write_text(json.dumps(items, indent=2))

    def record_start(self, model: str, config: str, log_file: str) -> Dict[str, Optional[str]]:
        items = self._load()
        record = {
            "start_time": datetime.now().strftime(TIMESTAMP_FORMAT),
            "end_time": None,
            "model": model,
            "config": config,
            "log_file": log_file,
            "status": "running",
        }
        items.append(record)
        self._save(items)
        return record

    def record_end(self, log_file: str, status: str) -> None:
        items = self._load()
        for record in reversed(items):
            if record.get("log_file") == log_file and record.get("end_time") is None:
                record["end_time"] = datetime.now().strftime(TIMESTAMP_FORMAT)
                record["status"] = status
                break
        self._save(items)

    def list_history(self, limit: int = 10) -> List[Dict[str, Optional[str]]]:
        items = self._load()
        return items[-limit:]
