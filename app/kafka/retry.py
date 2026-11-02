import asyncio
import logging

logger = logging.getLogger(__name__)


async def process_with_retry(
    event: dict,
    process_func,
    max_attempts: int = 3
):
    global _test_attempt_count 
    for attempt in range(1, max_attempts + 1):
        try:
            return await process_func(event)

        except Exception as exc:
            logger.warning(
                "Processing failed attempt=%s/%s EventUuid=%s error=%s",
                attempt,
                max_attempts,
                event.get("EventUuid"),
                exc,
            )

            if attempt == max_attempts:
                raise

            delay_seconds = 2 ** (attempt - 1)

            logger.info(
                "Retrying EventUuid=%s in %s seconds",
                event.get("EventUuid"),
                delay_seconds,
            )

            await asyncio.sleep(delay_seconds)