from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse, PlainTextResponse

from app.config import Settings, load_settings
from app.managers import (
    ConfigManager,
    HistoryManager,
    InferenceManager,
    LogManager,
    ModelManager,
    SystemMonitor,
)


def create_app(settings: Optional[Settings] = None) -> FastAPI:
    settings = settings or load_settings()

    log_manager = LogManager(settings.log_dir, settings.log_retention_days)
    history_manager = HistoryManager(settings.history_file)
    model_manager = ModelManager(settings.model_dir)
    config_manager = ConfigManager(settings.config_dir)
    inference_manager = InferenceManager(
        settings.infer_binary, log_manager, history_manager
    )
    system_monitor = SystemMonitor()

    app = FastAPI(title="PI Infer API", version=settings.version)

    @app.on_event("shutdown")
    def _shutdown() -> None:
        inference_manager.shutdown()

    @app.post("/inference/start")
    def start_inference(
        model: Optional[str] = Query(default=None),
        config: Optional[str] = Query(default=None),
    ) -> Dict[str, Any]:
        model_path = model_manager.get_current() if not model else model_manager.get_model(model)
        config_path = config_manager.get_current() if not config else config_manager.get_config(config)
        if not model_path or not config_path:
            raise HTTPException(status_code=400, detail="model or config not set")
        try:
            pid = inference_manager.start(model_path, config_path)
        except RuntimeError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc
        return {
            "pid": pid,
            "log_file": str(inference_manager.log_file) if inference_manager.log_file else None,
        }

    @app.post("/inference/stop")
    def stop_inference() -> Dict[str, Any]:
        try:
            inference_manager.stop()
        except RuntimeError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        return {"status": "stopped"}

    @app.get("/inference/status")
    def inference_status(field: Optional[str] = Query(default=None)) -> Dict[str, Any]:
        status = inference_manager.status()
        data = status.__dict__
        if field:
            if field not in data:
                raise HTTPException(status_code=400, detail="unknown field")
            return {field: data[field]}
        return data

    @app.post("/model/upload")
    def upload_model(
        model: Optional[str] = Query(default=None),
        file: UploadFile = File(...),
    ) -> Dict[str, Any]:
        try:
            target = model_manager.upload(file, model_name=model)
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return {"model": str(target)}

    @app.get("/models/list")
    def list_models(wildcard: Optional[str] = Query(default=None)) -> Dict[str, Any]:
        return {"models": model_manager.list_models(wildcard)}

    @app.get("/model/using")
    def current_model() -> Dict[str, Any]:
        current = model_manager.get_current()
        return {"model": str(current) if current else None}

    @app.get("/model/get")
    def download_model(model: str = Query(...)) -> FileResponse:
        try:
            path = model_manager.get_model(model)
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        return FileResponse(path)

    @app.post("/config/upload")
    def upload_config(
        config: Optional[str] = Query(default=None),
        file: UploadFile = File(...),
    ) -> Dict[str, Any]:
        try:
            target = config_manager.upload(file, config_name=config)
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return {"config": str(target)}

    @app.get("/configs/list")
    def list_configs(wildcard: Optional[str] = Query(default=None)) -> Dict[str, Any]:
        return {"configs": config_manager.list_configs(wildcard)}

    @app.get("/config/using")
    def current_config() -> Dict[str, Any]:
        current = config_manager.get_current()
        return {"config": str(current) if current else None}

    @app.get("/config/get")
    def download_config(config: str = Query(...)) -> FileResponse:
        try:
            path = config_manager.get_config(config)
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        return FileResponse(path)

    @app.get("/status/system")
    def system_status(field: Optional[str] = Query(default=None)) -> Dict[str, Any]:
        status = system_monitor.get_status()
        if field:
            if field not in status:
                raise HTTPException(status_code=400, detail="unknown field")
            return {field: status[field]}
        return status

    @app.get("/status/inference")
    def status_inference_alias(field: Optional[str] = Query(default=None)) -> Dict[str, Any]:
        return inference_status(field)

    @app.get("/logs", response_class=PlainTextResponse)
    def read_logs(
        since: Optional[str] = Query(default=None),
        tail: Optional[int] = Query(default=None),
    ) -> str:
        try:
            return log_manager.read_logs(since=since, tail=tail)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/history")
    def get_history(limit: int = Query(default=10, ge=1)) -> Dict[str, Any]:
        return {"history": history_manager.list_history(limit)}

    @app.get("/help", response_class=PlainTextResponse)
    def help_doc() -> str:
        return _help_text()

    @app.get("/version")
    def version_info() -> Dict[str, Any]:
        return {
            "version": settings.version,
            "git_commit": settings.git_commit,
            "build_time": settings.build_time,
        }

    return app


def _help_text() -> str:
    return """PI Infer API

POST /inference/start?model=PATH&config=PATH
POST /inference/stop
GET  /inference/status?field=running|current_model|current_config|uptime|pid|log_file|last_error|exit_code

POST /model/upload?model=NAME (multipart file)
GET  /models/list?wildcard=PATTERN
GET  /model/using
GET  /model/get?model=PATH

POST /config/upload?config=NAME (multipart file)
GET  /configs/list?wildcard=PATTERN
GET  /config/using
GET  /config/get?config=PATH

GET  /status/system?field=memory_usage|cpu_load|temperature|uptime
GET  /status/inference?field=...
GET  /logs?since=YYYY-MM-DD_HH:MM:SS&tail=N
GET  /history?limit=N
GET  /help
GET  /version
"""


app = create_app()


if __name__ == "__main__":
    import uvicorn

    settings = load_settings()
    uvicorn.run(app, host=settings.host, port=settings.port)
