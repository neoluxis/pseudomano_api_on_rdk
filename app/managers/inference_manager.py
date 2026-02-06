from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional
import subprocess
import sys

from app.managers.history_manager import HistoryManager
from app.managers.log_manager import LogManager


@dataclass
class InferenceStatus:
    running: bool
    pid: Optional[int]
    current_model: Optional[str]
    current_config: Optional[str]
    uptime: Optional[float]
    log_file: Optional[str]
    last_error: Optional[str]
    exit_code: Optional[int]


class InferenceManager:
    def __init__(
        self,
        infer_binary: Path,
        log_manager: LogManager,
        history_manager: HistoryManager,
    ) -> None:
        self.infer_binary = infer_binary
        self.log_manager = log_manager
        self.history_manager = history_manager
        self.process: Optional[subprocess.Popen[str]] = None
        self.start_time: Optional[datetime] = None
        self.current_model: Optional[str] = None
        self.current_config: Optional[str] = None
        self.log_file: Optional[Path] = None
        self.last_error: Optional[str] = None
        self.last_exit_code: Optional[int] = None

    def start(self, model_path: Path, config_path: Path) -> int:
        if self.is_running():
            raise RuntimeError("inference already running")
        self.log_manager.prune_old_logs()
        self.start_time = datetime.now()
        self.log_file = self.log_manager.create_log_file(self.start_time)
        self.current_model = str(model_path)
        self.current_config = str(config_path)
        command = self._build_command(model_path, config_path)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        log_handle = self.log_file.open("a", encoding="utf-8")
        try:
            self.process = subprocess.Popen(
                command,
                stdout=log_handle,
                stderr=subprocess.STDOUT,
                text=True,
            )
        except Exception as exc:
            log_handle.close()
            self.last_error = str(exc)
            self.process = None
            raise
        self.last_error = None
        self.last_exit_code = None
        self.history_manager.record_start(
            self.current_model,
            self.current_config,
            str(self.log_file),
        )
        return int(self.process.pid)

    def stop(self) -> None:
        if not self.process:
            raise RuntimeError("inference not running")
        if self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
        self.last_exit_code = self.process.returncode
        self.history_manager.record_end(
            str(self.log_file) if self.log_file else "",
            "manual_stopped",
        )
        self.process = None
        self.start_time = None

    def is_running(self) -> bool:
        return self.process is not None and self.process.poll() is None

    def status(self) -> InferenceStatus:
        if self.process and self.process.poll() is not None:
            self.last_exit_code = self.process.returncode
            self.last_error = "inference process exited"
            self.history_manager.record_end(
                str(self.log_file) if self.log_file else "",
                "failed",
            )
            self.process = None
            self.start_time = None
        uptime = None
        if self.start_time and self.is_running():
            uptime = (datetime.now() - self.start_time).total_seconds()
        return InferenceStatus(
            running=self.is_running(),
            pid=self.process.pid if self.process else None,
            current_model=self.current_model,
            current_config=self.current_config,
            uptime=uptime,
            log_file=str(self.log_file) if self.log_file else None,
            last_error=self.last_error,
            exit_code=self.last_exit_code,
        )

    def shutdown(self) -> None:
        if self.process and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.process.kill()
        self.process = None
        self.start_time = None

    def _build_command(self, model_path: Path, config_path: Path) -> list[str]:
        binary = self.infer_binary
        if binary.suffix == ".py":
            return [sys.executable, str(binary), "--model", str(model_path), "--config", str(config_path)]
        return [str(binary), "--model", str(model_path), "--config", str(config_path)]
