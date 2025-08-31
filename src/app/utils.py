import asyncio, random
from loguru import logger

async def backoff(min_s: int, max_s: int):
    delay = min(max_s, max(min_s, int(random.random() * (max_s - min_s + 1))))
    logger.warning(f"Reconnecting in {delay}s …")
    await asyncio.sleep(delay)
