import asyncio

from app.kafka.kafka_producer import KafkaProducer


async def main():
    producer = KafkaProducer()

    await producer.start()

    await producer.publish(
        "customer-activity",
        {
            "customerId": "001",
            "activity": "Page Visit"
        }
    )

    await producer.stop()


if __name__ == "__main__":
    asyncio.run(main())
