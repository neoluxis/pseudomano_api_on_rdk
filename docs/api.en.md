# API Reference

Chinese version: [docs/api.md](docs/api.md)

Docs index (ZH): [docs/README.md](docs/README.md)

Base URL: `http://localhost:8000`

## Inference

- `POST /inference/start?model={model_path}&config={config_path}`
  - Starts inference if not running.
  - If `model` or `config` is omitted, uses current selections.
  - Returns `{ "pid": number, "log_file": string }`.

- `POST /inference/stop`
  - Stops the inference process.
  - Records history status as `manual_stopped`.

- `GET /inference/status?field={field_name}`
  - Fields: `running`, `current_model`, `current_config`, `uptime`, `pid`, `log_file`, `last_error`, `exit_code`.
  - If `field` is omitted, returns all fields.

## Models

- `POST /model/upload?model={new_model_name}`
  - Uploads a model file and sets it as current.

- `GET /model/list?wildcard={pattern}`
  - Lists available models, supports glob patterns such as `*.onnx`.

- `GET /model/current`
  - Returns the current model file name.

- `POST /model/select?model={model_name}`
  - Selects the current model.

- `GET /model/download?model={model_name}`
  - Downloads a model file by name.

- `POST /model/delete?model={model_name}`
  - Deletes a model file.

## Configs

- `POST /config/upload?config={new_config_name}`
  - Uploads a config file and sets it as current.

- `GET /config/list?wildcard={pattern}`
  - Lists available configs, supports glob patterns such as `*.yaml`.

- `GET /config/current`
  - Returns the current config file name.

- `POST /config/select?config={config_name}`
  - Selects the current config.

- `GET /config/download?config={config_name}`
  - Downloads a config file by name.

- `POST /config/update?config={config_name}`
  - Updates config content (JSON body: `{"content": "yaml_string"}`).

- `POST /config/delete?config={config_name}`
  - Deletes a config file.

## Status and logs

- `GET /status/system?field={field_name}`
  - Fields: `memory_usage`, `cpu_load`, `temperature`, `uptime`.

- `GET /status/inference?field={field_name}`
  - Alias of `/inference/status`.

- `GET /logs?since={timestamp}&tail={tail}`
  - `timestamp` format: `YYYY-MM-DD_HH:MM:SS`.
  - `tail` returns last N lines.

- `GET /history?limit={n}`
  - Returns recent inference runs (default 10).

## Misc

- `GET /help`
  - Returns a text summary of endpoints.

- `GET /version`
  - Returns `{ "version", "git_commit", "build_time" }`.

## Examples

Upload model and config:

```bash
curl -X POST "http://localhost:8000/model/upload" \
  -F "file=@/path/to/model.onnx"

curl -X POST "http://localhost:8000/config/upload" \
  -F "file=@/path/to/config.yaml"
```

List models and configs:

```bash
curl "http://localhost:8000/model/list"
curl "http://localhost:8000/config/list"
```

Start inference:

```bash
curl -X POST "http://localhost:8000/inference/start?model=model.onnx&config=config.yaml"
```

Python example:

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

Start inference:

```bash
curl -X POST "http://localhost:8000/inference/start"
```

Python example:

```python
import requests

base_url = "http://localhost:8000"
response = requests.post(f"{base_url}/inference/start")
response.raise_for_status()
print(response.json())
```

Check status:

```bash
curl "http://localhost:8000/inference/status"
```

Python example:

```python
import requests

base_url = "http://localhost:8000"
response = requests.get(f"{base_url}/inference/status")
response.raise_for_status()
print(response.json())
```

Tail logs:

```bash
curl "http://localhost:8000/logs?tail=100"
```

Python example:

```python
import requests

base_url = "http://localhost:8000"
response = requests.get(f"{base_url}/logs", params={"tail": 100})
response.raise_for_status()
print(response.text)
```

Stop inference:

```bash
curl -X POST "http://localhost:8000/inference/stop"
```

Python example:

```python
import requests

base_url = "http://localhost:8000"
response = requests.post(f"{base_url}/inference/stop")
response.raise_for_status()
print(response.json())
```
