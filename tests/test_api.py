from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app


def _build_settings(tmp_path: Path) -> Settings:
    base_dir = tmp_path
    log_dir = tmp_path / "logs"
    model_dir = tmp_path / "models"
    config_dir = tmp_path / "configs"
    history_file = tmp_path / "history" / "history.json"
    infer_binary = Path(__file__).parent / "fake_infer.py"
    return Settings(
        base_dir=base_dir,
        log_dir=log_dir,
        model_dir=model_dir,
        config_dir=config_dir,
        history_file=history_file,
        infer_binary=infer_binary,
        log_retention_days=7,
        version="0.1.0",
        build_time="2026-02-06T00:00:00Z",
        git_commit="test",
    )


def test_inference_lifecycle(tmp_path: Path) -> None:
    settings = _build_settings(tmp_path)
    model_dir = settings.model_dir
    config_dir = settings.config_dir
    model_dir.mkdir(parents=True, exist_ok=True)
    config_dir.mkdir(parents=True, exist_ok=True)
    model_path = model_dir / "model.onnx"
    config_path = config_dir / "config.yaml"
    model_path.write_text("model")
    config_path.write_text("config")

    app = create_app(settings)
    client = TestClient(app)

    response = client.post("/inference/start")
    assert response.status_code == 200
    pid = response.json()["pid"]
    assert pid is not None

    status = client.get("/inference/status").json()
    assert status["running"] is True

    stop = client.post("/inference/stop")
    assert stop.status_code == 200

    status = client.get("/inference/status").json()
    assert status["running"] is False


def test_model_config_upload_and_list(tmp_path: Path) -> None:
    settings = _build_settings(tmp_path)
    app = create_app(settings)
    client = TestClient(app)

    model_upload = client.post(
        "/model/upload",
        files={"file": ("model.onnx", b"data", "application/octet-stream")},
    )
    assert model_upload.status_code == 200

    config_upload = client.post(
        "/config/upload",
        files={"file": ("config.yaml", b"data", "text/plain")},
    )
    assert config_upload.status_code == 200

    models = client.get("/model/list").json()["models"]
    configs = client.get("/configs/list").json()["configs"]
    assert any(path.endswith("model.onnx") for path in models)
    assert any(path.endswith("config.yaml") for path in configs)


def test_system_status(tmp_path: Path) -> None:
    settings = _build_settings(tmp_path)
    app = create_app(settings)
    client = TestClient(app)

    response = client.get("/status/system")
    assert response.status_code == 200
    data = response.json()
    assert "memory_usage" in data
    assert "cpu_load" in data
