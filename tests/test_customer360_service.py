import pytest
from unittest.mock import patch
from pydantic import ValidationError
from app.models.customer_intelligence import (
    AIAnalysis,
    CustomerIntelligenceResponse
)

from app.services.customer360_service import  (    
    get_customer_360,
    get_ai_customer_360_summary,
    customer_interaction_summary,
    get_customer_intelligence,
    calculate_health_score
)


@pytest.fixture
def sample_account_360():
    return {
        "account": {
            "id": "001",
            "name": "Acme"
        },
        "pipeline_insight": {
            "opportunity_count": 1,
            "total_pipeline_amount": 150000
        },
        "opportunities": [],
        "insights": {
            "closed_won_amount": 10000,
            "open_pipeline_amount": 150000,
            "opportunity_count": 1,
            "total_opportunities": 3
        }
    }

@pytest.fixture
def sample_engagements():
    return {
        "data": [
            [
                "Website",
                "Object",
                "MCP",
                "2026-09-11",
                "Product_View",
                None,
                "/products/generator",
                "Fall Campaign",
                "EVT010"
            ]
        ]
    }

@pytest.mark.asyncio
@patch("app.services.customer360_service.get_website_engagements")
@patch("app.services.customer360_service.get_unified_profile_by_email")
async def test_get_customer_360(
    mock_profile,
    mock_engagements,
    sample_engagements
):

    mock_profile.return_value = {
        "data": [
            [
                "test@gmail.com",
                "12345",
                "2026-01-01"
            ]
        ]
    }

    mock_engagements.return_value = sample_engagements

    result = await get_customer_360(
        "test@gmail.com"
    )

    assert result["email"] == "test@gmail.com"

    assert result["profile_found"] is True

    assert result["total_events"] == 1

    assert result["profile"][0]["party_id"] == "12345"

    assert (
        result["events"][0]["engagement_type"]
        == "Product_View"
    )

@pytest.mark.asyncio
@patch("app.services.customer360_service.get_website_engagements")
@patch("app.services.customer360_service.get_unified_profile_by_email")
async def test_get_customer_360_no_profile_found(
    mock_profile,
    mock_engagements,
    sample_engagements
):
    mock_profile.return_value = {
        "data": []
    }

    mock_engagements.return_value = sample_engagements

    result = await get_customer_360(
        "test@gmail.com"
    )

    assert result["email"] == "test@gmail.com"

    assert result["profile_found"] is False

    assert result["total_events"] == 1

    assert result["events"][0]["engagement_id"] == "EVT010"

    assert result["events"][0]["engagement_type"] == "Product_View"

    assert result["events"][0]["campaign_name"] == "Fall Campaign"


@pytest.mark.asyncio
@patch("app.services.customer360_service.ask_claude")
@patch("app.services.customer360_service.get_account_360")
async def test_get_ai_customer_360_summary(
    mock_account_360,
    mock_ask_claude,
    sample_account_360
):
    mock_account_360.return_value = sample_account_360

    mock_ask_claude.return_value = (
        "Healthy customer with strong pipeline."
    )

    result = await get_ai_customer_360_summary(
        "Acme"
    )

    assert result["account_name"] == "Acme"

    assert (
        result["summary"]
        == "Healthy customer with strong pipeline."
    )

    mock_account_360.assert_called_once_with(
        "Acme"
    )

    mock_ask_claude.assert_called_once()
    mock_ask_claude.assert_awaited_once()

    prompt_sent = mock_ask_claude.call_args[0][0]

    assert "Customer 360 data" in prompt_sent
    assert "Acme" in prompt_sent


@pytest.mark.asyncio
@patch("app.services.customer360_service.ask_claude")
@patch("app.services.customer360_service.log_customer_event")
@patch("app.services.customer360_service.get_customer_graph_context")
async def test_customer_interaction_summary(
    mock_get_customer,
    mock_log_event,
    mock_ask_claude
):
    mock_get_customer.return_value = {
        "account_name": "Acme Corp"
    }

    mock_log_event.return_value = {
        "success": True,
        "event_id": "EVT001"
    }

    mock_ask_claude.return_value = (
        "Strong buying intent detected."
    )

    result = await customer_interaction_summary(
        account_id="001",
        event_id="EVT001",
        email="test@gmail.com",
        contact_id="003",
        event_type="Product_View",
        product_sku="GEN-100",
        event_value=100
    )

    assert result["customer"]["account_name"] == "Acme Corp"

    assert result["event_result"]["success"] is True

    assert result["summary"] == (
        "Strong buying intent detected."
    )


@pytest.mark.asyncio
@patch("app.services.customer360_service.ask_claude")
@patch("app.services.customer360_service.get_website_engagements")
@patch("app.services.customer360_service.get_account_360")
async def test_get_customer_intelligence(    
    mock_account_360,    
    mock_engagements,
    mock_claude,
    sample_account_360,
    sample_engagements
):

    mock_account_360.return_value = sample_account_360

    mock_engagements.return_value = sample_engagements

    mock_claude.side_effect = [
        """
        {
            "customer_overview": "Strong account",
            "pipeline_assessment": "Healthy pipeline",
            "risk_level": "Low",
            "confidence": "High",
            "top_opportunity": "Renewal",
            "recommended_action": "Schedule follow up"
        }
        """,
        "Contact customer this week"
    ]

    result = await get_customer_intelligence(
        "Acme Corp"
    )

    assert result.account_name == "Acme Corp"

    assert (
        result.segment
        == "High Pipeline Accounts"
    )

    assert result.ai_analysis.risk_level == "Low"

    assert result.ai_analysis.confidence == "High"

    assert (
        result.priority_action
        == "Contact customer this week"
    )

@pytest.mark.asyncio
@patch("app.services.customer360_service.get_account_360")
async def test_get_customer_intelligence_account_not_found(
    mock_account_360
):
    mock_account_360.return_value = None

    with pytest.raises(ValueError) as exc_info:
        await get_customer_intelligence("Bad Account")

    assert "Account not found" in str(exc_info.value)

@pytest.mark.asyncio
@patch("app.services.customer360_service.ask_claude")
@patch("app.services.customer360_service.get_website_engagements")
@patch("app.services.customer360_service.get_account_360")
async def test_get_customer_intelligence_invalid_ai_json(
    mock_account_360,
    mock_engagements,
    mock_claude,
    sample_account_360
):
    mock_account_360.return_value = sample_account_360

    mock_engagements.return_value = {
        "data": []
    }

    mock_claude.side_effect = [
        "this is not json",
        "Contact customer this week"
    ]

    with pytest.raises(ValueError) as exc_info:
        await get_customer_intelligence(
            "Acme Corp"
        )

    assert str(exc_info.value) == (
        "Invalid AI analysis JSON response"
    )

def test_invalid_health_score():
    with pytest.raises(ValidationError):
        CustomerIntelligenceResponse(
            account_name="Acme",
            health_score=200,
            health_status="Healthy",
            timeline=[],
            recent_activity=[],
            ai_analysis=...
        )

def test_invalid_risk_level():

    with pytest.raises(ValidationError):

        AIAnalysis(
            customer_overview="Overview",
            pipeline_assessment="Healthy",
            risk_level="Very Low",
            confidence="High",
            top_opportunity="Renewal",
            recommended_action="Follow up"
        )

@pytest.mark.parametrize(
    "insights,expected_status",
    [
        (
            {
                "closed_won_amount": 10000,
                "open_pipeline_amount": 150000,
                "total_opportunities": 3
            },
            "Healthy"
        ),
        (
            {
                "closed_won_amount": 10000,
                "open_pipeline_amount": 0,
                "total_opportunities": 0
            },
            "Attention Required"
        ),
        (
            {
                "closed_won_amount": 0,
                "open_pipeline_amount": 0,
                "total_opportunities": 0
            },
            "At Risk"
        )
    ]
)
def test_calculate_health_score(
    insights,
    expected_status
):
    result = calculate_health_score(insights)

    assert result["health_status"] == expected_status