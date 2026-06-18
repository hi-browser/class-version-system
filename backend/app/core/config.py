from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "Classroom Vision System"
    APP_ENV: str = "dev"
    HOST: str = "127.0.0.1"
    PORT: int = 8000

    MYSQL_HOST: str = "127.0.0.1"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = "123456"
    MYSQL_DATABASE: str = "classroom_vision"

    UPLOAD_DIR: str = "app/static/uploads"
    RESULT_DIR: str = "app/static/results"
    MODEL_PATH: str = "weights/scb_yolo.pt"
<<<<<<< HEAD
    PERSON_MODEL_PATH: str = "weights/person_yolo.pt"
    MOCK_ANALYSIS: bool = True
=======
    MOCK_ANALYSIS: bool = False
>>>>>>> gitee/ysy-frontend-checkversiontest
    FRAME_INTERVAL_SECONDS: int = 2
    CONF_THRESHOLD: float = 0.25
    PERSON_CONF_THRESHOLD: float = 0.25
    TRACKING_ENABLED: bool = True

    SMTP_HOST: str = "smtp.163.com"
    SMTP_PORT: int = 465
    SMTP_USER: str = "your_email@163.com"  # ← 占位符
    SMTP_PASSWORD: str = "your_auth_code"  # ← 占位符
    SMTP_FROM: str = "your_email@163.com"  # ← 占位符
    JWT_SECRET: str = "classroom-vision-jwt-secret-key-2025"  # 签名密钥
    JWT_ALGORITHM: str = "HS256"  # 签名算法
    JWT_EXPIRE_MINUTES: int = 60 * 24  # 令牌有效期（分钟）

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
            f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}?charset=utf8mb4"
        )

settings = Settings()

Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
Path(settings.RESULT_DIR).mkdir(parents=True, exist_ok=True)
Path("weights").mkdir(parents=True, exist_ok=True)