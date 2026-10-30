import asyncio
import os
from dotenv import load_dotenv
from aiokafka import AIOKafkaConsumer

import json
from app.kafka.processed_event_store import process_customer_activity

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

            is_new_event = process_customer_activity(event)

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


if __name__ == "__main__":
    asyncio.run(main())
