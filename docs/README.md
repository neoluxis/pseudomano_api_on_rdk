# PI Infer API 文档

文档索引。

## 概述

PI Infer API 通过启动/停止子进程来管理 C++ 推理 CLI，同时在磁盘上保存模型、配置、日志和历史记录，并提供查询状态与下载接口。

## 文档列表

- API 参考： [docs/api.md](docs/api.md)
- 环境与配置： [docs/environment.md](docs/environment.md)
- English index: [docs/README.en.md](docs/README.en.md)

## 快速设置

```bash
python3 -m venv ./.venv
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install -r requirements.txt
cp .env.template .env
./.venv/bin/python run.py
```

## Docker Compose 与 WebUI

使用 Compose 启动 API 与 WebUI：

```bash
docker compose up -d --build
```

访问地址：

- API: `http://localhost:8000`
- WebUI: `http://localhost:8080`（通过 `/api` 访问 API）
