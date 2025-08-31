from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from .config import settings

engine = create_engine(settings.db_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class Base(DeclarativeBase):
    pass

def init_db():
    from .models import Tick
    Base.metadata.create_all(bind=engine)

    # Create helpful indexes once (idempotent)
    with engine.begin() as conn:
        conn.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_ticks_symbol_ts ON ticks(symbol, ts);
        CREATE INDEX IF NOT EXISTS idx_ticks_ts ON ticks(ts);
        """))
