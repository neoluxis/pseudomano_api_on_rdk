from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from fastapi import UploadFile

from app.utils import ensure_dir, safe_resolve


class ConfigManager:
    def __init__(self, config_dir: Path) -> None:
        self.config_dir = config_dir
        ensure_dir(self.config_dir)
        self.current_file = self.config_dir / ".current_config"

    def _write_current(self, path: Path) -> None:
        self.current_file.write_text(str(path))

    def _read_current(self) -> Optional[Path]:
        if self.current_file.exists():
            return Path(self.current_file.read_text().strip())
        return None

    def get_current(self) -> Optional[Path]:
        current = self._read_current()
        if current and current.exists():
            return current
        return self._latest_config()

    def _latest_config(self) -> Optional[Path]:
        files = sorted(self.config_dir.glob("*"))
        candidates = [f for f in files if f.is_file() and not f.name.startswith(".")]
        if not candidates:
            return None
        return max(candidates, key=lambda p: p.stat().st_mtime)

    def set_current(self, path: Path) -> Path:
        resolved = safe_resolve(self.config_dir, str(path))
        if not resolved.exists():
            raise FileNotFoundError("config not found")
        self._write_current(resolved)
        return resolved

    def upload(self, upload: UploadFile, config_name: Optional[str] = None) -> str:
        ensure_dir(self.config_dir)
        name = config_name or upload.filename or "config.yaml"
        safe_name = Path(name).name
        target = self.config_dir / safe_name
        content = upload.file.read()
        target.write_bytes(content)
        self._write_current(target)
        return safe_name

    def list_configs(self, pattern: Optional[str] = None) -> List[str]:
        ensure_dir(self.config_dir)
        glob_pattern = pattern or "*"
        return [path.name for path in sorted(self.config_dir.glob(glob_pattern)) if path.is_file()]

    def get_config(self, config_path: str) -> Path:
        resolved = safe_resolve(self.config_dir, config_path)
        if not resolved.exists():
            raise FileNotFoundError("config not found")
        return resolved

    def update(self, config_path: str, content: str) -> str:
        resolved = safe_resolve(self.config_dir, config_path)
        if not resolved.exists():
            raise FileNotFoundError("config not found")
        resolved.write_text(content)
        self._write_current(resolved)
        return resolved.name

    def delete(self, config_path: str) -> Path:
        resolved = safe_resolve(self.config_dir, config_path)
        if not resolved.exists():
            raise FileNotFoundError("config not found")
        resolved.unlink()
        self._refresh_current(resolved)
        return resolved

    def _refresh_current(self, removed: Path) -> None:
        current = self._read_current()
        if current and current.resolve() == removed.resolve():
            latest = self._latest_config()
            if latest:
                self._write_current(latest)
            elif self.current_file.exists():
                self.current_file.unlink()
