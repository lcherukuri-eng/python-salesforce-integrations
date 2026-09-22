import pytest
from unittest.mock import AsyncMock

import json
import io

from fastavro import schemaless_writer
from app.event_consumer.customer_activity_consumer import CustomerActivityConsumer

import logging

def test_save_replay_id(tmp_path):
    consumer = CustomerActivityConsumer()

    consumer.REPLAY_FILE = tmp_path / "replay_id.txt"

    consumer.save_replay_id("abc123")

    assert consumer.REPLAY_FILE.read_text() == "abc123"

def test_get_last_replay_id(tmp_path):
    consumer = CustomerActivityConsumer()

    replay_file = tmp_path / "replay_id.txt"
    replay_file.write_text("abc123")

    consumer.REPLAY_FILE = replay_file

    assert consumer.get_last_replay_id() == "abc123"

def test_get_last_replay_id_when_file_missing(tmp_path):
    consumer = CustomerActivityConsumer()

    consumer.REPLAY_FILE = tmp_path / "missing.txt"

    assert consumer.get_last_replay_id() is None

def test_invalid_replay_id():
    with pytest.raises(ValueError):
        bytes.fromhex("invalidhex")

@pytest.mark.asyncio
async def test_get_schema_json_uses_cache():
    consumer = CustomerActivityConsumer()

    mock_response = AsyncMock()
    mock_response.schema_json = '{"type":"record"}'

    consumer.get_schema = AsyncMock(
        return_value=mock_response
    )

    await consumer.get_schema_json("schema1")
    await consumer.get_schema_json("schema1")

    consumer.get_schema.assert_awaited_once()

@pytest.mark.asyncio
async def test_decode_payload():
    consumer = CustomerActivityConsumer()

    schema = {
        "type": "record",
        "name": "CustomerActivity",
        "fields": [
            {
                "name": "Customer_Id__c",
                "type": "string"
            },
            {
                "name": "Activity_Type__c",
                "type": "string"
            },
            {
                "name": "Activity_Source__c",
                "type": "string"
            }
        ]
    }

    record = {
        "Customer_Id__c": "123",
        "Activity_Type__c": "Login",
        "Activity_Source__c": "Salesforce"
    }

    buffer = io.BytesIO()

    schemaless_writer(
        buffer,
        schema,
        record
    )

    payload = buffer.getvalue()

    decoded = await consumer.decode_payload(
        payload,
        json.dumps(schema)
    )

    assert decoded == record

@pytest.mark.asyncio
async def test_process_event(caplog):
    consumer = CustomerActivityConsumer()

    event = {
        "Customer_Id__c": "123",
        "Activity_Type__c": "Login",
        "Activity_Source__c": "Salesforce"
    }

    with caplog.at_level(logging.INFO):
        await consumer.process_event(event)

    assert "Customer=123" in caplog.text
    

