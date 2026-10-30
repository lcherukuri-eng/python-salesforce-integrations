from app.database import get_connection


def process_customer_activity(event: dict) -> bool:
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
            activity_source
        )
        VALUES (%s, %s, %s, %s)
    """

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                insert_processed_event_sql,
                (event_uuid,)
            )

            row = cursor.fetchone()

            if row is None:
                return False           

            cursor.execute(
                insert_activity_sql,
                (
                    event_uuid,
                    event.get("Customer_Id__c"),
                    event.get("Activity_Type__c"),
                    event.get("Activity_Source__c"),
                )
            )

    return True