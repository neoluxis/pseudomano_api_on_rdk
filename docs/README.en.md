# PI Infer API Docs

Short index for detailed docs.

## Overview

PI Infer API manages a C++ inference CLI by starting and stopping a child process. It also stores models, configs, logs, and history on disk, and provides endpoints to query status and retrieve artifacts.

## Documents

- API reference: [docs/api.en.md](docs/api.en.md)
- Environment and configuration: [docs/environment.en.md](docs/environment.en.md)
- Chinese docs index: [docs/README.md](docs/README.md)

## Quick setup

```bash
python3 -m venv ./.venv
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install -r requirements.txt
cp .env.template .env
./.venv/bin/python run.py
```

## Docker Compose and WebUI

Start API and WebUI with Compose:

```bash
docker compose up -d --build
```

Access:

- API: `http://localhost:8000`
- WebUI: `http://localhost:8080` (proxying API under `/api`)
