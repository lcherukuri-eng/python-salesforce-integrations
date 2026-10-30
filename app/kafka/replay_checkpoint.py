from app.database import get_connection


def save_replay_checkpoint(
    subscription_key: str,
    replay_id: str
):
    sql = """
        INSERT INTO salesforce_replay_checkpoint (
            subscription_key,
            replay_id
        )
        VALUES (%s, %s)
        ON CONFLICT (subscription_key)
        DO UPDATE SET
            replay_id = EXCLUDED.replay_id,
            updated_at = CURRENT_TIMESTAMP
    """

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                sql,
                (subscription_key, replay_id)
            )
        

def load_replay_checkpoint(
    subscription_key: str
) -> str | None:
    sql = """
        SELECT replay_id
        FROM salesforce_replay_checkpoint
        WHERE subscription_key = %s
    """

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                sql,
                (subscription_key,) # One-item tuple; ("value") is just a string, ("value",) is a tuple. execute() expects a sequence of parameter values.
            )

            row = cursor.fetchone()

    if row is None:
        return None

    return row[0]
