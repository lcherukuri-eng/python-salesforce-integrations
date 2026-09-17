import time

from app.logger import get_logger

logger = get_logger(__name__)

async def timing_middleware(request, call_next):
    start_time = time.time()

    response = await call_next(request)

    process_time = time.time() - start_time

    logger.info(
        f"{request.method} {request.url.path} "
        f"-> {response.status_code} "
        f"completed in {process_time:.2f} seconds"
    )

    response.headers["X-Process-Time"] = str(round(process_time, 2))

    return response