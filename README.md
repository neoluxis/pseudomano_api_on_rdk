# PI Infer API

用于管理推理 CLI 的 FastAPI 服务。

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

## Docker Compose

使用 Compose 启动 API 与 WebUI：

```bash
docker compose up -d --build
```

访问：

- API: `http://localhost:8000`
- WebUI: `http://localhost:8080`（通过 `/api` 反向代理 API）

## 测试

```bash
./.venv/bin/python -m pytest -q
```
