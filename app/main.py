"""
PI Infer API 主应用文件

提供基于FastAPI的REST API接口，用于管理模型推理、文件上传下载等功能。
支持模型和配置的管理，以及推理过程的控制和监控。
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import Body, FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
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
    """
    创建并配置FastAPI应用实例

    Args:
        settings: 应用配置设置，如果为None则自动加载默认设置

    Returns:
        配置完成的FastAPI应用实例
    """
    settings = settings or load_settings()

    # 初始化各个管理器
    log_manager = LogManager(settings.log_dir, settings.log_retention_days)
    history_manager = HistoryManager(settings.history_file)
    model_manager = ModelManager(settings.model_dir)
    config_manager = ConfigManager(settings.config_dir)
    inference_manager = InferenceManager(
        settings.infer_binary, log_manager, history_manager
    )
    system_monitor = SystemMonitor()

    # 创建FastAPI应用，设置根路径为/api
    app = FastAPI(title="PI Infer API", version=settings.version, root_path="/api")

    # 配置CORS中间件，允许所有来源的跨域请求
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("shutdown")
    def _shutdown() -> None:
        """应用关闭时的清理工作"""
        inference_manager.shutdown()

    @app.post("/inference/start")
    def start_inference(
        model: Optional[str] = Query(default=None),
        config: Optional[str] = Query(default=None),
    ) -> Dict[str, Any]:
        """
        启动推理进程

        Args:
            model: 模型文件名，如果为None则使用当前默认模型
            config: 配置文件名，如果为None则使用当前默认配置

        Returns:
            包含进程PID和日志文件路径的字典

        Raises:
            HTTPException: 当模型或配置不存在，或推理已在运行时抛出
        """
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
        """
        停止当前运行的推理进程

        Returns:
            包含停止状态的字典

        Raises:
            HTTPException: 当没有运行中的推理进程时抛出
        """
        try:
            inference_manager.stop()
        except RuntimeError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        return {"status": "stopped"}

    @app.get("/inference/status")
    def inference_status(field: Optional[str] = Query(default=None)) -> Dict[str, Any]:
        """
        获取推理进程的当前状态

        Args:
            field: 可选的特定字段名，如果提供则只返回该字段的值

        Returns:
            推理状态信息字典，包含运行状态、PID、模型、配置等信息
        """
        status = inference_manager.status()
        data = status.__dict__
        
        # If not running, show current defaults
        if not data.get("running"):
            current_model = model_manager.get_current()
            current_config = config_manager.get_current()
            data["current_model"] = current_model.name if current_model else None
            data["current_config"] = current_config.name if current_config else None
        
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
        """
        上传模型文件

        Args:
            model: 可选的模型文件名，如果不提供则使用原始文件名
            file: 上传的模型文件

        Returns:
            包含保存的模型文件名的字典

        Raises:
            HTTPException: 当上传失败时抛出
        """
        try:
            target = model_manager.upload(file, model_name=model)
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return {"model": target}

    @app.get("/model/list")
    def list_models(wildcard: Optional[str] = Query(default=None)) -> Dict[str, Any]:
        """
        获取模型文件列表

        Args:
            wildcard: 可选的通配符过滤条件

        Returns:
            包含模型文件名列表的字典
        """
        return {"models": model_manager.list_models(wildcard)}

    @app.get("/model/current")
    def current_model() -> Dict[str, Any]:
        """
        获取当前默认模型

        Returns:
            包含当前模型文件名的字典
        """
        current = model_manager.get_current()
        return {"model": current.name if current else None}

    @app.post("/model/select")
    def select_model(model: str = Query(...)) -> Dict[str, Any]:
        """
        设置当前默认模型

        Args:
            model: 要设置为默认的模型文件名

        Returns:
            包含设置的模型文件名的字典

        Raises:
            HTTPException: 当模型文件不存在时抛出
        """
        try:
            selected = model_manager.set_current(model)
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        return {"model": selected.name}

    @app.get("/model/download")
    def download_model(model: str = Query(...)) -> FileResponse:
        """
        下载指定的模型文件

        Args:
            model: 要下载的模型文件名

        Returns:
            模型文件的响应对象

        Raises:
            HTTPException: 当模型文件不存在时抛出
        """
        try:
            path = model_manager.get_model(model)
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        return FileResponse(path)

    @app.post("/model/delete")
    def delete_model(model: str = Query(...)) -> Dict[str, Any]:
        """
        删除指定的模型文件

        Args:
            model: 要删除的模型文件名

        Returns:
            包含删除的模型文件名的字典

        Raises:
            HTTPException: 当模型文件不存在时抛出
        """
        try:
            removed = model_manager.delete(model)
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        return {"deleted": removed.name}

    @app.post("/config/upload")
    def upload_config(
        config: Optional[str] = Query(default=None),
        file: UploadFile = File(...),
    ) -> Dict[str, Any]:
        """
        上传配置文件

        Args:
            config: 可选的配置文件名，如果不提供则使用原始文件名
            file: 上传的配置文件

        Returns:
            包含保存的配置文件名的字典

        Raises:
            HTTPException: 当上传失败时抛出
        """
        try:
            target = config_manager.upload(file, config_name=config)
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return {"config": target}

    @app.get("/config/list")
    def list_configs(wildcard: Optional[str] = Query(default=None)) -> Dict[str, Any]:
        """
        获取配置文件列表

        Args:
            wildcard: 可选的通配符过滤条件

        Returns:
            包含配置文件名列表的字典
        """
        return {"configs": config_manager.list_configs(wildcard)}

    @app.get("/config/current")
    def current_config() -> Dict[str, Any]:
        """
        获取当前默认配置

        Returns:
            包含当前配置文件名的字典
        """
        current = config_manager.get_current()
        return {"config": current.name if current else None}

    @app.post("/config/select")
    def select_config(config: str = Query(...)) -> Dict[str, Any]:
        """
        设置当前默认配置

        Args:
            config: 要设置为默认的配置文件名

        Returns:
            包含设置的配置文件名的字典

        Raises:
            HTTPException: 当配置文件不存在时抛出
        """
        try:
            selected = config_manager.set_current(config)
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        return {"config": selected.name}

    @app.get("/config/download")
    def download_config(config: str = Query(...)) -> FileResponse:
        """
        下载指定的配置文件

        Args:
            config: 要下载的配置文件名

        Returns:
            配置文件响应对象

        Raises:
            HTTPException: 当配置文件不存在时抛出
        """
        try:
            path = config_manager.get_config(config)
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        return FileResponse(path)

    @app.post("/config/update")
    def update_config(
        config: str = Query(...),
        content: str = Body(..., embed=True),
    ) -> Dict[str, Any]:
        """
        更新配置文件内容

        Args:
            config: 要更新的配置文件名
            content: 新的配置文件内容

        Returns:
            包含更新配置名的字典

        Raises:
            HTTPException: 当配置文件不存在时抛出
        """
        try:
            updated = config_manager.update(config, content)
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        return {"config": updated}

    @app.post("/config/delete")
    def delete_config(config: str = Query(...)) -> Dict[str, Any]:
        """
        删除指定的配置文件

        Args:
            config: 要删除的配置文件名

        Returns:
            包含删除配置名的字典

        Raises:
            HTTPException: 当配置文件不存在时抛出
        """
        try:
            removed = config_manager.delete(config)
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        return {"deleted": removed.name}

    @app.get("/status/system")
    def system_status(field: Optional[str] = Query(default=None)) -> Dict[str, Any]:
        """
        获取系统状态信息

        Args:
            field: 可选的特定字段名，如果提供则只返回该字段的值

        Returns:
            系统状态信息字典，包含内存、CPU、温度等信息
        """
        status = system_monitor.get_status()
        if field:
            if field not in status:
                raise HTTPException(status_code=400, detail="unknown field")
            return {field: status[field]}
        return status

    @app.get("/status/inference")
    def status_inference_alias(field: Optional[str] = Query(default=None)) -> Dict[str, Any]:
        """
        获取推理状态信息的别名端点

        Args:
            field: 可选的特定字段名

        Returns:
            推理状态信息字典
        """
        return inference_status(field)

    @app.get("/logs", response_class=PlainTextResponse)
    def read_logs(
        since: Optional[str] = Query(default=None),
        tail: Optional[int] = Query(default=None),
    ) -> str:
        """
        读取日志内容

        Args:
            since: 可选的时间戳，只返回该时间之后的日志
            tail: 可选的行数，只返回最后N行日志

        Returns:
            日志内容的纯文本字符串

        Raises:
            HTTPException: 当时间戳格式无效时抛出
        """
        try:
            return log_manager.read_logs(since=since, tail=tail)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/history")
    def get_history(limit: int = Query(default=10, ge=1)) -> Dict[str, Any]:
        """
        获取推理历史记录

        Args:
            limit: 返回的历史记录数量上限，默认10条

        Returns:
            包含历史记录列表的字典
        """
        return {"history": history_manager.list_history(limit)}

    @app.get("/help", response_class=PlainTextResponse)
    def help_doc() -> str:
        """
        获取API帮助文档

        Returns:
            帮助文档的纯文本字符串
        """
        return _help_text()

    @app.get("/version")
    def version_info() -> Dict[str, Any]:
        """
        获取版本信息

        Returns:
            包含版本、Git提交哈希和构建时间的字典
        """
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
GET  /model/list?wildcard=PATTERN
GET  /model/current
POST /model/select?model=NAME
GET  /model/download?model=NAME
POST /model/delete?model=NAME

POST /config/upload?config=NAME (multipart file)
GET  /config/list?wildcard=PATTERN
GET  /config/current
POST /config/select?config=NAME
GET  /config/download?config=NAME
POST /config/update?config=NAME (JSON body)
POST /config/delete?config=NAME

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
