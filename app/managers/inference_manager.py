"""
推理管理器

负责管理推理进程的启动、停止和状态监控。
"""

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
    """推理状态数据类"""
    running: bool  # 是否正在运行
    pid: Optional[int]  # 进程ID
    current_model: Optional[str]  # 当前使用的模型路径
    current_config: Optional[str]  # 当前使用的配置路径
    uptime: Optional[float]  # 运行时间（秒）
    log_file: Optional[str]  # 日志文件路径
    last_error: Optional[str]  # 最后一次错误信息
    exit_code: Optional[int]  # 退出代码


class InferenceManager:
    """
    推理进程管理器

    负责启动、停止和管理推理进程，记录历史和日志。
    """

    def __init__(
        self,
        infer_binary: Path,
        log_manager: LogManager,
        history_manager: HistoryManager,
    ) -> None:
        """
        初始化推理管理器

        Args:
            infer_binary: 推理可执行文件路径
            log_manager: 日志管理器实例
            history_manager: 历史记录管理器实例
        """
        self.infer_binary = infer_binary
        self.log_manager = log_manager
        self.history_manager = history_manager
        self.process: Optional[subprocess.Popen[str]] = None  # 当前推理进程
        self.start_time: Optional[datetime] = None  # 进程启动时间
        self.current_model: Optional[str] = None  # 当前模型路径
        self.current_config: Optional[str] = None  # 当前配置路径
        self.log_file: Optional[Path] = None  # 当前日志文件
        self.last_error: Optional[str] = None  # 最后错误信息
        self.last_exit_code: Optional[int] = None  # 最后退出代码

    def start(self, model_path: Path, config_path: Path) -> int:
        """
        启动推理进程

        Args:
            model_path: 模型文件路径
            config_path: 配置文件路径

        Returns:
            启动的进程ID

        Raises:
            RuntimeError: 当推理已在运行时抛出
        """
        if self.is_running():
            raise RuntimeError("inference already running")
        self.log_manager.prune_old_logs()
        self.start_time = datetime.now()
        self.log_file = self.log_manager.create_log_file(self.start_time)
        self.current_model = model_path.name
        self.current_config = config_path.name
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
        """
        停止当前运行的推理进程

        Raises:
            RuntimeError: 当没有运行中的推理进程时抛出
        """
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
        """
        检查推理进程是否正在运行

        Returns:
            如果进程正在运行则返回True，否则返回False
        """
        return self.process is not None and self.process.poll() is None

    def status(self) -> InferenceStatus:
        """
        获取当前推理状态

        Returns:
            包含当前推理状态信息的InferenceStatus对象
        """
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
        """
        强制关闭推理进程（用于应用关闭时的清理）
        """
        if self.process and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.process.kill()
        self.process = None
        self.start_time = None

    def _build_command(self, model_path: Path, config_path: Path) -> list[str]:
        """
        构建推理命令行参数

        Args:
            model_path: 模型文件路径
            config_path: 配置文件路径

        Returns:
            命令行参数列表
        """
        binary = self.infer_binary
        if binary.suffix == ".py":
            return [sys.executable, str(binary), "--model", str(model_path), "--config", str(config_path)]
        return [str(binary), "--model", str(model_path), "--config", str(config_path)]
