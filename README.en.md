# PI Infer API

FastAPI service to manage the inference CLI.

## Documentation

Default docs (Chinese): [docs/README.md](docs/README.md).

English docs: [docs/README.en.md](docs/README.en.md).

Reference links:

- API reference: [docs/api.en.md](docs/api.en.md)
- Environment and configuration: [docs/environment.en.md](docs/environment.en.md)
- Chinese README: [README.md](README.md)
- Chinese docs index: [docs/README.md](docs/README.md)

## Quick start

```bash
python3 -m venv ./.venv
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install -r requirements.txt
cp .env.template .env
./.venv/bin/python run.py
```

Shorter command:

```bash
make run
```

## Docker Compose

Start API and WebUI with Compose:

```bash
docker compose up -d --build
```

Access:

- API: `http://localhost:8000`
- WebUI: `http://localhost:8080` (proxying API under `/api`)

## Tests

```bash
./.venv/bin/python -m pytest -q
```

