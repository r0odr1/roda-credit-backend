"""Configuración centralizada de la aplicación Flask."""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuración base."""

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")

    # PostgreSQL: usar DATABASE_URL
    _db_url = os.getenv("DATABASE_URL", "postgresql+psycopg://localhost/roda_db")
    if _db_url.startswith("postgres://"):
        _db_url = _db_url.replace("postgres://", "postgresql+psycopg://", 1)
    elif _db_url.startswith("postgresql://") and "+psycopg" not in _db_url:
        _db_url = _db_url.replace("postgresql://", "postgresql+psycopg://", 1)
    SQLALCHEMY_DATABASE_URI = _db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Tasa de interés efectiva anual configurable
    ANNUAL_INTEREST_RATE = float(os.getenv("ANNUAL_INTEREST_RATE", "0.18"))

    # CORS
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

    # Reglas de negocio
    MIN_VEHICLE_VALUE_COP = 500_000
    MIN_TERM_MONTHS = 6
    MAX_TERM_MONTHS = 60


class ProductionConfig(Config):
    DEBUG = False


class DevelopmentConfig(Config):
    DEBUG = True


def get_config():
    env = os.getenv("FLASK_ENV", "development").lower()
    return ProductionConfig if env == "production" else DevelopmentConfig