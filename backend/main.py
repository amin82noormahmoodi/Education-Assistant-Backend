import time
import logging
from fastapi import FastAPI, Request

from core.db import Base, engine
from routes import auth_router, chat_router

app = FastAPI()

logger = logging.getLogger("app")
logging.basicConfig(
    level = logging.INFO,
    format = "%(asctime)s | %(levelname)s | %(message)s")

logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

Base.metadata.create_all(bind=engine)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start_time) * 1000
    logger.info(
        "%s %s -> %s (%.1fms)",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms)
    return response

app.include_router(auth_router)
app.include_router(chat_router)