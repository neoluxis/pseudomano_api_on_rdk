# Environment and Configuration

Chinese version: [docs/environment.md](docs/environment.md)

Docs index (ZH): [docs/README.md](docs/README.md)

## Data layout

By default, runtime data is stored under `./data`:

- `data/models`
- `data/configs`
- `data/logs`
- `data/history/history.json`

## Setup

Create a virtual environment and install dependencies:

```bash
python3 -m venv ./.venv
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install -r requirements.txt
```

## Configuration

Copy the template and edit as needed:

```bash
cp .env.template .env
```

### Environment variables

| Name | Description | Default |
| --- | --- | --- |
| `PI_INFER_BASE_DIR` | Base directory for the service | repo root |
| `PI_INFER_DATA_DIR` | Base directory for data storage | `./data` |
| `PI_INFER_LOG_DIR` | Log directory | `./data/logs` |
| `PI_INFER_MODEL_DIR` | Model directory | `./data/models` |
| `PI_INFER_CONFIG_DIR` | Config directory | `./data/configs` |
| `PI_INFER_HISTORY_FILE` | History JSON file | `./data/history/history.json` |
| `PI_INFER_BINARY` | Path to inference CLI binary | `./infer` |
| `PI_INFER_LOG_RETENTION_DAYS` | Log retention days | `7` |
| `PI_INFER_HOST` | API host | `0.0.0.0` |
| `PI_INFER_PORT` | API port | `8000` |
| `PI_INFER_VERSION` | API version string | `0.1.0` |
| `PI_INFER_GIT_COMMIT` | Git commit hash | `unknown` |
| `PI_INFER_BUILD_TIME` | Build time string | `UTC now` |

## Run

```bash
./.venv/bin/python run.py
```
