from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
from .db import SessionLocal, init_db
from .schemas import TickOut, CandleOut
from .config import settings

app = FastAPI(title="Market Data API", version="0.1.0")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/health")
def health():
    return {"status": "ok", "symbols": settings.subscribe_symbols}

@app.get("/latest", response_model=TickOut)
def latest(symbol: str, db: Session = Depends(get_db)):
    q = text('''
        SELECT id, symbol, price, volume, source_ts_ms, ts
        FROM ticks
        WHERE symbol=:symbol
        ORDER BY ts DESC
        LIMIT 1
    ''')
    row = db.execute(q, {"symbol": symbol}).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="No data for symbol")
    return dict(row)

@app.get("/ticks", response_model=List[TickOut])
def ticks(symbol: str, limit: int = 100, db: Session = Depends(get_db)):
    limit = max(1, min(5000, limit))
    q = text('''
        SELECT id, symbol, price, volume, source_ts_ms, ts
        FROM ticks
        WHERE symbol=:symbol
        ORDER BY ts DESC
        LIMIT :limit
    ''')
    rows = db.execute(q, {"symbol": symbol, "limit": limit}).mappings().all()
    return [dict(r) for r in rows]

@app.get("/candles", response_model=List[CandleOut])
def candles(symbol: str, minutes: int = 60, db: Session = Depends(get_db)):
    minutes = max(1, min(24*60, minutes))
    # Bucket to minute and compute OHLCV
    q = text('''
        WITH src AS (
            SELECT * FROM ticks
            WHERE symbol=:symbol AND ts >= (NOW() - (:minutes || ' minutes')::interval)
        )
        SELECT date_trunc('minute', ts) AS t,
               first_value(price) OVER (PARTITION BY date_trunc('minute', ts) ORDER BY ts ASC ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS o,
               max(price)  AS h,
               min(price)  AS l,
               last_value(price)  OVER (PARTITION BY date_trunc('minute', ts) ORDER BY ts ASC ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS c,
               coalesce(sum(volume), 0) AS v
        FROM src
        GROUP BY 1
        ORDER BY 1 ASC;
    ''')
    rows = db.execute(q, {"symbol": symbol, "minutes": minutes}).mappings().all()
    return [
        {"t": r["t"], "o": float(r["o"]) if r["o"] is not None else 0.0,
         "h": float(r["h"]) if r["h"] is not None else 0.0,
         "l": float(r["l"]) if r["l"] is not None else 0.0,
         "c": float(r["c"]) if r["c"] is not None else 0.0,
         "v": float(r["v"]) if r["v"] is not None else 0.0}
        for r in rows
    ]
