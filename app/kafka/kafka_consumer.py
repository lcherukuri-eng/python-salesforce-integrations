import asyncio
import os
from dotenv import load_dotenv
from aiokafka import AIOKafkaConsumer

import json
from app.kafka.processed_event_store import process_customer_activity
from app.kafka.retry import process_with_retry
from app.kafka.kafka_producer import KafkaProducer
from app.database import async_pool

import selectors

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

logger = logging.getLogger(__name__)

load_dotenv()

kafka_bootstrap_server = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
kafka_topic = os.getenv("KAFKA_TOPIC")


async def main():
    await async_pool.open()
    await async_pool.wait() 

    dlq_producer = KafkaProducer()
    await dlq_producer.start()

    consumer = AIOKafkaConsumer(
        kafka_topic,
        bootstrap_servers=kafka_bootstrap_server,
        group_id="customer-group",
        auto_offset_reset="earliest",
        enable_auto_commit=False
    )

    await consumer.start()

    try:
        logger.info("Consumer started")

        async for msg in consumer:

            logger.info(
                "Topic=%s Partition=%s Offset=%s",
                msg.topic,
                msg.partition,
                msg.offset,
            )

            event = json.loads(
                msg.value.decode("utf-8")
            )

            logger.info(
                "Received message: %s",
                event
            )

            event_uuid = event.get("EventUuid")

            if not event_uuid:
                logger.error(
                    "EventUuid missing; message cannot be processed idempotently. "
                    "Topic=%s Partition=%s Offset=%s",
                    msg.topic,
                    msg.partition,
                    msg.offset,
                )

                # Do not commit. This record can be retried or handled later.
                continue
            try:
                is_new_event = await process_with_retry(
                    event,
                    process_customer_activity,
                    max_attempts=3
                )

            except Exception as exc:
                logger.error(
                    "Processing failed after retries EventUuid=%s error=%s",
                    event_uuid,
                    exc,
                )
                dlq_message = {
                    "original_event": event,
                    "original_topic": msg.topic,
                    "original_partition": msg.partition,
                    "original_offset": msg.offset,
                    "error": str(exc),
                }

                await dlq_producer.publish(
                    "customer-activity-dlq",
                    dlq_message,
                    key=event.get("Customer_Id__c")
                )

                logger.info(
                    "Event sent to DLQ EventUuid=%s",
                    event_uuid
                )
                await consumer.commit()

                logger.info(
                    "Committed original offset after DLQ publish offset=%s",
                    msg.offset
                )

                continue

            if not is_new_event:
                logger.info(
                    "Duplicate event skipped EventUuid=%s",
                    event_uuid 
                )

                await consumer.commit()

                logger.info(
                    "Committed offset for duplicate event offset=%s",
                    msg.offset
                )

                continue

            logger.info(
                "Processed customer activity EventUuid=%s",
                event_uuid
            )            

            await consumer.commit()

            logger.info(
                "Committed offset after processing message offset=%s",
                msg.offset
            )

    finally:
        await consumer.stop()
        await dlq_producer.stop()
        await async_pool.close()


if __name__ == "__main__":
    asyncio.run(
        main(),
        loop_factory=lambda: asyncio.SelectorEventLoop(
            selectors.SelectSelector()
        )
    )
