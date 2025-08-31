import asyncio
import uvicorn
from loguru import logger
from .api import app
from .ingestor import run_ingestor
from .config import settings

async def supervisor():
    stop_event = asyncio.Event()
    ingest_task = asyncio.create_task(run_ingestor(stop_event))

    config = uvicorn.Config(app=app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)
    api_task = asyncio.create_task(server.serve())

    try:
        await asyncio.gather(ingest_task, api_task)
    except asyncio.CancelledError:
        pass
    finally:
        stop_event.set()
        logger.info("Shutting down…")

if __name__ == "__main__":
    asyncio.run(supervisor())
