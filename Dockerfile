FROM python:3.11-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential make \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN python -m pip install --upgrade pip \
    && python -m pip install -r requirements.txt

COPY . .
RUN make dummy_infer

ENV PI_INFER_BASE_DIR=/app \
    PI_INFER_DATA_DIR=/app/data \
    PI_INFER_LOG_DIR=/app/data/logs \
    PI_INFER_MODEL_DIR=/app/data/models \
    PI_INFER_CONFIG_DIR=/app/data/configs \
    PI_INFER_HISTORY_FILE=/app/data/history/history.json \
    PI_INFER_BINARY=/app/infer \
    PI_INFER_LOG_RETENTION_DAYS=7 \
    PI_INFER_HOST=0.0.0.0 \
    PI_INFER_PORT=8000

EXPOSE 8000

CMD ["sh", "-c", "python -m uvicorn app.main:app --host ${PI_INFER_HOST:-0.0.0.0} --port ${PI_INFER_PORT:-8000}"]
