from pydantic import BaseModel
from datetime import datetime

class TickOut(BaseModel):
    id: int
    symbol: str
    price: float
    volume: float | None
    source_ts_ms: int
    ts: datetime

    class Config:
        from_attributes = True

class CandleOut(BaseModel):
    t: datetime  # period start
    o: float
    h: float
    l: float
    c: float
    v: float
