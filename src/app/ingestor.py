import asyncio, json, contextlib
import websockets
from websockets.exceptions import ConnectionClosed
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, timezone
from loguru import logger

from .config import settings
from .db import SessionLocal
from .models import Tick
from .utils import backoff

SUB_MSG = lambda sym: json.dumps({"type": "subscribe", "symbol": sym})

async def _store_tick(db: Session, symbol: str, price: float, volume: float | None, t_ms: int):
    tick = Tick(symbol=symbol, price=price, volume=volume, source_ts_ms=t_ms)
    db.add(tick)

async def _flush(db: Session):
    with contextlib.suppress(Exception):
        db.commit()

async def run_ingestor(stop_event: asyncio.Event):
    logger.info("Ingestor starting …")
    while not stop_event.is_set():
        try:
            async with websockets.connect(settings.websocket_url, ping_interval=20) as ws:
                logger.info("Connected to Finnhub WebSocket")
                # Subscribe to symbols
                for sym in settings.subscribe_symbols:
                    await ws.send(SUB_MSG(sym))
                logger.info(f"Subscribed: {settings.subscribe_symbols}")

                db = SessionLocal()
                last_commit = datetime.now(tz=timezone.utc)
                try:
                    async for msg in ws:
                        data = json.loads(msg)
                        if data.get("type") == "trade":
                            for d in data.get("data", []):
                                await _store_tick(db, d.get("s"), float(d.get("p")), float(d.get("v")) if d.get("v") is not None else None, int(d.get("t")))
                        # Commit every ~0.5s to batch writes
                        now = datetime.now(tz=timezone.utc)
                        if (now - last_commit).total_seconds() > 0.5:
                            await _flush(db)
                            last_commit = now
                        if stop_event.is_set():
                            break
                finally:
                    await _flush(db)
                    db.close()
        except ConnectionClosed as e:
            logger.error(f"WebSocket closed: {e}")
            await backoff(settings.reconnect_min_sec, settings.reconnect_max_sec)
        except Exception as e:
            logger.exception(f"Ingestor error: {e}")
            await backoff(settings.reconnect_min_sec, settings.reconnect_max_sec)
    logger.info("Ingestor stopped.")
