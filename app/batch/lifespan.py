from contextlib import asynccontextmanager
from ..batch.scheduler import scheduler


@asynccontextmanager
async def lifespan(app):
    scheduler.start()
    yield
    print("lifespan finished")
    scheduler.shutdown()
