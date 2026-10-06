import json
import os
from dotenv import load_dotenv
from aiokafka import AIOKafkaProducer
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

logger = logging.getLogger(__name__)

load_dotenv()

kafka_bootstrap_server = os.getenv("KAFKA_BOOTSTRAP_SERVERS")

class KafkaProducer:

    def __init__(self):
        self.producer = None

    async def start(self):
        self.producer = AIOKafkaProducer(
            bootstrap_servers=kafka_bootstrap_server
        )

        await self.producer.start()

        logger.info("Kafka producer started")

    async def stop(self):
        if self.producer:
            await self.producer.stop()

    async def publish(
        self,
        topic: str,
        message: dict
    ):
        await self.producer.send_and_wait(
            topic,
            json.dumps(message).encode("utf-8")
        )

        logger.info(
            "Published message to topic=%s", 
            topic
        )