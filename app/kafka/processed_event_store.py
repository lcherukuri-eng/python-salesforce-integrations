from app.database import async_pool


async def process_customer_activity(event: dict) -> bool:
    event_uuid = event["EventUuid"]

    insert_processed_event_sql = """
        INSERT INTO processed_events (event_uuid)
        VALUES (%s)
        ON CONFLICT (event_uuid)
        DO NOTHING
        RETURNING event_uuid
    """

    insert_activity_sql = """
        INSERT INTO customer_activity (
            event_uuid,
            customer_id,
            activity_type,
            activity_source,
            activity_status
        )
        VALUES (%s, %s, %s, %s, %s)
    """

    async with async_pool.connection() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                insert_processed_event_sql,
                (event_uuid,)
            )

            row = await cursor.fetchone()

            if row is None:
                return False           

            await cursor.execute(
                insert_activity_sql,
                (
                    event_uuid,
                    event.get("Customer_Id__c"),
                    event.get("Activity_Type__c"),
                    event.get("Activity_Source__c"),
                    event.get("Activity_Status__c")
                )
            )

    return True