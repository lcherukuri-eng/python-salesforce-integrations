from typing import Any

from pydantic import BaseModel, field_validator


class TimelineEvent(BaseModel):
    event: str
    amount: float
    date: str

class RecentActivity(BaseModel):
    activity: str
    date: str
    channel: str

class AIAnalysis(BaseModel):
    customer_overview: str
    pipeline_assessment: str
    risk_level: str
    confidence: str
    top_opportunity: str
    recommended_action: str

    @field_validator("risk_level")
    @classmethod
    def validate_risk_level(cls, value):
    
        valid_levels = [
            "Low",
            "Medium",
            "High"
        ]
    
        if value not in valid_levels:
            raise ValueError(
                f"Invalid risk level: {value}"
            )
    
        return value

class CustomerIntelligenceResponse(BaseModel):
    account_name: str
    segment: str | None
    health_score: int
    health_status: str

    timeline: list[TimelineEvent]
    recent_activity: list[RecentActivity]

    priority_action: str
    ai_analysis: AIAnalysis

    customer_360: dict[str, Any]

    @field_validator("health_score")
    @classmethod
    def validate_health_Score(cls, value):
        if value < 0 or value > 100:
            raise ValueError(
                "Health score must be between 0 and 100"
            )
        return value

    @field_validator("health_status")
    @classmethod
    def validate_health_status(cls, value):

        valid_statuses = [
            "Healthy",
            "Attention Required",
            "At Risk"
        ]

        if value not in valid_statuses:
            raise ValueError(
                f"Invalid health status: {value}"
            )

        return value

   