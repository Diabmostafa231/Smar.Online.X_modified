import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-jwt-secret-change-me")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'smart_online_x.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Comma separated list of origins allowed to call the API, e.g.
    # "https://yourusername.github.io"
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*").split(",")
