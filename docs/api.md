# API 参考

English version: [docs/api.en.md](docs/api.en.md)

中文文档索引： [docs/README.md](docs/README.md)

基础地址：`http://localhost:8000`

## 推理

- `POST /inference/start?model={model_path}&config={config_path}`
  - 启动推理（未运行时）。
  - 省略 `model` 或 `config` 会使用当前选择。
  - 返回 `{ "pid": number, "log_file": string }`。

- `POST /inference/stop`
  - 停止推理进程。
  - 历史记录状态标记为 `manual_stopped`。

- `GET /inference/status?field={field_name}`
  - 字段：`running`, `current_model`, `current_config`, `uptime`, `pid`, `log_file`, `last_error`, `exit_code`。
  - 省略 `field` 返回全部字段。

## 模型

- `POST /model/upload?model={new_model_path}`
  - 上传模型文件并设为当前模型。

- `GET /models/list?wildcard={pattern}`
  - 列出可用模型，支持 `*.onnx` 等通配符。

- `GET /model/using`
  - 返回当前模型路径。

- `GET /model/get?model={model_path}`
  - 按路径下载模型（在模型目录内验证）。

## 配置

- `POST /config/upload?config={new_config_path}`
  - 上传配置文件并设为当前配置。

- `GET /configs/list?wildcard={pattern}`
  - 列出可用配置，支持 `*.yaml` 等通配符。

- `GET /config/using`
  - 返回当前配置路径。

- `GET /config/get?config={config_path}`
  - 按路径下载配置（在配置目录内验证）。

## 状态与日志

- `GET /status/system?field={field_name}`
  - 字段：`memory_usage`, `cpu_load`, `temperature`, `uptime`。

- `GET /status/inference?field={field_name}`
  - `/inference/status` 的别名。

- `GET /logs?since={timestamp}&tail={tail}`
  - `timestamp` 格式：`YYYY-MM-DD_HH:MM:SS`。
  - `tail` 返回最后 N 行。

- `GET /history?limit={n}`
  - 返回最近 N 次推理记录（默认 10）。

## 其他

- `GET /help`
  - 返回接口摘要文本。

- `GET /version`
  - 返回 `{ "version", "git_commit", "build_time" }`。

## 示例

上传模型与配置：

```bash
curl -X POST "http://localhost:8000/model/upload" \
  -F "file=@/path/to/model.onnx"

curl -X POST "http://localhost:8000/config/upload" \
  -F "file=@/path/to/config.yaml"
```

Python 示例：

```python
import requests

base_url = "http://localhost:8000"

with open("/path/to/model.onnx", "rb") as model_file:
    response = requests.post(
        f"{base_url}/model/upload",
        files={"file": ("model.onnx", model_file, "application/octet-stream")},
    )
    response.raise_for_status()

with open("/path/to/config.yaml", "rb") as config_file:
    response = requests.post(
        f"{base_url}/config/upload",
        files={"file": ("config.yaml", config_file, "text/plain")},
    )
    response.raise_for_status()
```

启动推理：

```bash
curl -X POST "http://localhost:8000/inference/start"
```

Python 示例：

```python
import requests

base_url = "http://localhost:8000"
response = requests.post(f"{base_url}/inference/start")
response.raise_for_status()
print(response.json())
```

查看状态：

```bash
curl "http://localhost:8000/inference/status"
```

Python 示例：

```python
import requests

base_url = "http://localhost:8000"
response = requests.get(f"{base_url}/inference/status")
response.raise_for_status()
print(response.json())
```

查看日志：

```bash
curl "http://localhost:8000/logs?tail=100"
```

Python 示例：

```python
import requests

base_url = "http://localhost:8000"
response = requests.get(f"{base_url}/logs", params={"tail": 100})
response.raise_for_status()
print(response.text)
```

停止推理：

```bash
curl -X POST "http://localhost:8000/inference/stop"
```

Python 示例：

```python
import requests

base_url = "http://localhost:8000"
response = requests.post(f"{base_url}/inference/stop")
response.raise_for_status()
print(response.json())
```
