from pydantic import BaseModel
import os

class Settings(BaseModel):
    app_port: int = int(os.getenv("APP_PORT", 8000))
    dashboard_port: int = int(os.getenv("DASHBOARD_PORT", 8501))

    finnhub_token: str = os.getenv("FINNHUB_TOKEN", "")
    subscribe_symbols: list[str] = [s.strip() for s in os.getenv("SUBSCRIBE_SYMBOLS", "AAPL,MSFT").split(",") if s.strip()]
    websocket_url: str = os.getenv("WEBSOCKET_URL", f"wss://ws.finnhub.io?token={os.getenv('FINNHUB_TOKEN','')}")

    db_url: str = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:postgres@db:5432/marketdata")

    reconnect_min_sec: int = int(os.getenv("RECONNECT_MIN_SEC", 1))
    reconnect_max_sec: int = int(os.getenv("RECONNECT_MAX_SEC", 30))

    candle_resolution_sec: int = int(os.getenv("CANDLE_RESOLUTION_SEC", 60))

settings = Settings()
