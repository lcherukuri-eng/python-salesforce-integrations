from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_data_action_success():

    payload = {
        "schemas": [
            {
                "schema": "PipelineSchema",
                "schemaId": "SCH001"
            }
        ],
        "count": 1,
        "creationDateTime": "2026-09-15T10:00:00Z",
        "events": [
            {
                "EventPublishDateTime": "2026-09-15T10:00:00Z",
                "SourceObjectDeveloperName": "Account",
                "EventType": "UPDATE",
                "PayloadMetadata": "{}",
                "EventSchemaVersion": "1",
                "EventCreationDateTime": "2026-09-15T10:00:00Z",
                "ActionDeveloperName": "PipelineUpdate",
                "EventPrompt": "Pipeline Increased",
                "Offset": "1",

                "PayloadCurrentValue": """
                {
                    "AccountPipelineInsight__cio_CustomerAccountId__c": "001",
                    "AccountPipelineInsight__cio_OpportunityCount__c": 3,
                    "AccountPipelineInsight__cio_TotalPipelineAmount__c": 150000
                }
                """,

                "PayloadPrevValue": """
                {
                    "AccountPipelineInsight__cio_CustomerAccountId__c": "001",
                    "AccountPipelineInsight__cio_OpportunityCount__c": 2,
                    "AccountPipelineInsight__cio_TotalPipelineAmount__c": 100000
                }
                """
            }
        ]
    }

    response = client.post(
        "/webhooks/data-action",
        json=payload
    )

    assert response.status_code == 200

    assert response.json() == {
        "status": "success"
    }


def test_data_action_invalid_payload():

    payload = {
        "events": [
            {
                "ActionDeveloperName": "PipelineUpdate"
            }
        ]
    }

    response = client.post(
        "/webhooks/data-action",
        json=payload
    )

    assert response.status_code == 422
