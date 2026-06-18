import os
import sys
from app.core.config import settings

if __name__ == "__main__":
    args = [
        sys.executable,
        "-m", "uvicorn", "app.main:app",
        "--host", settings.HOST,
        "--port", str(settings.PORT),
    ]
    if settings.APP_ENV == "dev":
        args.append("--reload")

    os.execv(sys.executable, args)