import asyncio
import os
from dotenv import load_dotenv
from aiokafka import AIOKafkaConsumer
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
        auto_offset_reset="earliest"
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

            logger.info(
                "Received message: %s",
                msg.value.decode("utf-8")
            )

    finally:
        await consumer.stop()


if __name__ == "__main__":
    asyncio.run(main())
