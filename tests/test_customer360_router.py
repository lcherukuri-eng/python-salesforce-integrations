from fastapi.testclient import TestClient
from unittest.mock import patch

from app.main import app
from app.security import verify_request

app.dependency_overrides[verify_request] = (
    lambda: True
)
client = TestClient(app)

@patch("app.api.customer360.get_customer_360")
def test_customer_360_endpoint(
    mock_get_customer_360
):
    mock_get_customer_360.return_value = {
        "email": "test@gmail.com",
        "profile_found": True,
        "total_events": 1,
        "profile": [],
        "events": []
    }

    response = client.get(
        "/customer360/customer-360/test@gmail.com"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["email"] == "test@gmail.com"

    assert data["profile_found"] is True
    

@patch("app.api.customer360.get_account_360")
def test_account_customer_360_endpoint(
    mock_get_account_360
):

    mock_get_account_360.return_value = {
        "account": {
            "id": "001",
            "name": "Acme Corp"
        }
    }

    response = client.get(
        "/customer360/customer-360/account/Acme Corp"
    )

    assert response.status_code == 200

    assert (
        response.json()["account"]["name"]
        == "Acme Corp"
    )


@patch(
    "app.api.customer360.get_ai_customer_360_summary"
)
def test_account_customer_360_summary_endpoint(
    mock_summary
):

    mock_summary.return_value = {
        "account_name": "Acme Corp",
        "summary": "Healthy customer"
    }

    response = client.get(
        "/customer360/customer-360/account/Acme Corp/summary"
    )

    assert response.status_code == 200

    assert (
        response.json()["summary"]
        == "Healthy customer"
    )

@patch(
    "app.api.customer360.get_customer_graph_context"
)
def test_customer_graph_endpoint(
    mock_graph
):

    mock_graph.return_value = {
        "account_id": "001",
        "account_name": "Acme Corp"
    }

    response = client.get(
        "/customer360/customer-graph/001"
    )

    assert response.status_code == 200

    assert (
        response.json()["account_id"]
        == "001"
    )

@patch(
    "app.api.customer360.get_customer_intelligence"
)
def test_customer_intelligence_endpoint(
    mock_customer_intelligence
):

    mock_customer_intelligence.return_value = {
        "account_name": "Acme Corp",
        "segment": "High Pipeline Accounts",
        "health_score": 80,
        "health_status": "Healthy",
        "timeline": [],
        "recent_activity": [],
        "priority_action": "Contact customer",
        "ai_analysis": {
            "customer_overview": "Strong account",
            "pipeline_assessment": "Healthy",
            "risk_level": "Low",
            "confidence": "High",
            "top_opportunity": "Renewal",
            "recommended_action": "Follow up"
        },
        "customer_360": {}
    }

    response = client.get(
        "/customer360/customer-intelligence/Acme Corp"
    )    

    assert response.status_code == 200

    assert (
        response.json()["account_name"]
        == "Acme Corp"
    )