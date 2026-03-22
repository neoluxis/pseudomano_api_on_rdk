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

## Access

After startup, access:

- API: `http://localhost:8000`
- WebUI: `http://localhost:8000/ui`

The frontend now uses the same service and calls the API through `/api`, so a separate WebUI process is no longer required.

## Docker Compose

Start the single service that serves both the API and WebUI:

```bash
docker compose up -d --build
```

Access:

- API: `http://localhost:8000`
- WebUI: `http://localhost:8000/ui`

## Tests

```bash
./.venv/bin/python -m pytest -q
```
