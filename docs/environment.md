# 环境与配置

English version: [docs/environment.en.md](docs/environment.en.md)

中文文档索引： [docs/README.md](docs/README.md)

## 数据布局

默认将运行数据存放在 `./data`：

- `data/models`
- `data/configs`
- `data/logs`
- `data/history/history.json`

## 安装

创建虚拟环境并安装依赖：

```bash
python3 -m venv ./.venv
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install -r requirements.txt
```

## 配置

复制模板并按需修改：

```bash
cp .env.template .env
```

### 环境变量

| 名称 | 说明 | 默认值 |
| --- | --- | --- |
| `PI_INFER_BASE_DIR` | 服务基础目录 | 仓库根目录 |
| `PI_INFER_DATA_DIR` | 数据基础目录 | `./data` |
| `PI_INFER_LOG_DIR` | 日志目录 | `./data/logs` |
| `PI_INFER_MODEL_DIR` | 模型目录 | `./data/models` |
| `PI_INFER_CONFIG_DIR` | 配置目录 | `./data/configs` |
| `PI_INFER_HISTORY_FILE` | 历史记录文件 | `./data/history/history.json` |
| `PI_INFER_BINARY` | 推理 CLI 路径 | `./infer` |
| `PI_INFER_LOG_RETENTION_DAYS` | 日志保留天数 | `7` |
| `PI_INFER_HOST` | API 监听地址 | `0.0.0.0` |
| `PI_INFER_PORT` | API 监听端口 | `8000` |
| `PI_INFER_VERSION` | API 版本 | `0.1.0` |
| `PI_INFER_GIT_COMMIT` | Git 提交哈希 | `unknown` |
| `PI_INFER_BUILD_TIME` | 构建时间 | `UTC now` |

## 运行

```bash
./.venv/bin/python run.py
```
