from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from fastapi import UploadFile

from app.utils import ensure_dir, safe_resolve


class ModelManager:
    def __init__(self, model_dir: Path) -> None:
        self.model_dir = model_dir
        ensure_dir(self.model_dir)
        self.current_file = self.model_dir / ".current_model"

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
        return self._latest_model()

    def _latest_model(self) -> Optional[Path]:
        files = sorted(self.model_dir.glob("*"))
        candidates = [f for f in files if f.is_file() and not f.name.startswith(".")]
        if not candidates:
            return None
        return max(candidates, key=lambda p: p.stat().st_mtime)

    def set_current(self, path: Path) -> Path:
        resolved = safe_resolve(self.model_dir, str(path))
        if not resolved.exists():
            raise FileNotFoundError("model not found")
        self._write_current(resolved)
        return resolved

    def upload(self, upload: UploadFile, model_name: Optional[str] = None) -> str:
        ensure_dir(self.model_dir)
        name = model_name or upload.filename or "model.bin"
        safe_name = Path(name).name
        target = self.model_dir / safe_name
        content = upload.file.read()
        target.write_bytes(content)
        self._write_current(target)
        return safe_name

    def list_models(self, pattern: Optional[str] = None) -> List[str]:
        ensure_dir(self.model_dir)
        glob_pattern = pattern or "*"
        return [path.name for path in sorted(self.model_dir.glob(glob_pattern)) if path.is_file()]

    def get_model(self, model_path: str) -> Path:
        resolved = safe_resolve(self.model_dir, model_path)
        if not resolved.exists():
            raise FileNotFoundError("model not found")
        return resolved

    def delete(self, model_path: str) -> Path:
        resolved = safe_resolve(self.model_dir, model_path)
        if not resolved.exists():
            raise FileNotFoundError("model not found")
        resolved.unlink()
        self._refresh_current(resolved)
        return resolved

    def _refresh_current(self, removed: Path) -> None:
        current = self._read_current()
        if current and current.resolve() == removed.resolve():
            latest = self._latest_model()
            if latest:
                self._write_current(latest)
            elif self.current_file.exists():
                self.current_file.unlink()
