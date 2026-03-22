# PI Infer API

用于管理推理 CLI 的 FastAPI 服务。

学习 FastAPI 和 WebUI 构建所用，灵巧手项目所用

## 文档

默认文档索引见 [docs/README.md](docs/README.md)。

英文文档索引见 [docs/README.en.md](docs/README.en.md)。

参考链接：

- API 参考（中文）：[docs/api.md](docs/api.md)
- 环境与配置（中文）：[docs/environment.md](docs/environment.md)
- API reference (EN)：[docs/api.en.md](docs/api.en.md)
- Environment (EN)：[docs/environment.en.md](docs/environment.en.md)

## 快速开始

```bash
python3 -m venv ./.venv
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install -r requirements.txt
cp .env.template .env
./.venv/bin/python run.py
```

更短的启动命令：

```bash
make run
```

## 访问

启动后可直接访问：

- API: `http://localhost:8000`
- WebUI: `http://localhost:8000/ui`

前端默认通过同一服务下的 `/api` 访问接口，因此不再需要单独启动 WebUI。

## Docker Compose

使用 Compose 启动单个服务（同时提供 API 与 WebUI）：

```bash
docker compose up -d --build
```

访问：

- API: `http://localhost:8000`
- WebUI: `http://localhost:8000/ui`

## 测试

```bash
./.venv/bin/python -m pytest -q
```
