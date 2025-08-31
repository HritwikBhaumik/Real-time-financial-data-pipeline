from sqlalchemy import Column, Integer, String, Float, BigInteger, DateTime, func
from .db import Base

class Tick(Base):
    __tablename__ = "ticks"
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(32), index=True, nullable=False)
    price = Column(Float, nullable=False)
    volume = Column(Float, nullable=True)
    source_ts_ms = Column(BigInteger, nullable=False)  # Finnhub epoch ms
    ts = Column(DateTime(timezone=True), server_default=func.now(), index=True)  # server ingest time
