from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import os

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    base_dir: Path
    log_dir: Path
    model_dir: Path
    config_dir: Path
    history_file: Path
    infer_binary: Path
    log_retention_days: int
    host: str
    port: int
    version: str
    build_time: str
    git_commit: str


def load_settings() -> Settings:
    load_dotenv()
    base_dir = Path(
        os.getenv("PI_INFER_BASE_DIR", Path(__file__).resolve().parents[1])
    ).resolve()
    data_dir = Path(os.getenv("PI_INFER_DATA_DIR", base_dir / "data")).resolve()
    log_dir = Path(os.getenv("PI_INFER_LOG_DIR", data_dir / "logs")).resolve()
    model_dir = Path(os.getenv("PI_INFER_MODEL_DIR", data_dir / "models")).resolve()
    config_dir = Path(
        os.getenv("PI_INFER_CONFIG_DIR", data_dir / "configs")
    ).resolve()
    history_file = Path(
        os.getenv("PI_INFER_HISTORY_FILE", data_dir / "history" / "history.json")
    ).resolve()
    infer_binary_raw = os.getenv("PI_INFER_BINARY", str(base_dir / "infer"))
    infer_binary = Path(infer_binary_raw)
    if not infer_binary.is_absolute():
        infer_binary = (base_dir / infer_binary).resolve()

    log_retention_days = int(os.getenv("PI_INFER_LOG_RETENTION_DAYS", "7"))
    host = os.getenv("PI_INFER_HOST", "0.0.0.0")
    port = int(os.getenv("PI_INFER_PORT", "8000"))
    version = os.getenv("PI_INFER_VERSION", "0.1.0")
    build_time = os.getenv(
        "PI_INFER_BUILD_TIME", datetime.now(timezone.utc).isoformat()
    )
    git_commit = os.getenv("PI_INFER_GIT_COMMIT", "unknown")

    return Settings(
        base_dir=base_dir,
        log_dir=log_dir,
        model_dir=model_dir,
        config_dir=config_dir,
        history_file=history_file,
        infer_binary=infer_binary,
        log_retention_days=log_retention_days,
        host=host,
        port=port,
        version=version,
        build_time=build_time,
        git_commit=git_commit,
    )
