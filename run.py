import sys
from pathlib import Path


repo_root = Path(__file__).resolve().parent
sys.path.insert(0, str(repo_root))

from app.config import load_settings
from app.main import create_app
import uvicorn


if __name__ == "__main__":
    settings = load_settings()
    app = create_app(settings)
    uvicorn.run(app, host=settings.host, port=settings.port)
