from typing import List

from pydantic import BaseModel, Field, ConfigDict


class PipelineInsight(BaseModel):

    model_config = ConfigDict(
        populate_by_name=True
    )

    customer_account_id: str = Field(
        alias="AccountPipelineInsight__cio_CustomerAccountId__c"
    )

    opportunity_count: float = Field(
        alias="AccountPipelineInsight__cio_OpportunityCount__c"
    )

    total_pipeline_amount: float = Field(
        alias="AccountPipelineInsight__cio_TotalPipelineAmount__c"
    )


class SchemaItem(BaseModel):
    schema_text: str = Field(alias="schema")
    schemaId: str


class EventItem(BaseModel):
    EventPublishDateTime: str
    PayloadCurrentValue: str
    SourceObjectDeveloperName: str
    EventType: str
    PayloadPrevValue: str
    PayloadMetadata: str
    EventSchemaVersion: str
    EventCreationDateTime: str
    EventPrompt: str
    ActionDeveloperName: str
    Offset: str


class DataActionPayload(BaseModel):
    schemas: List[SchemaItem]
    count: int
    events: List[EventItem]
    creationDateTime: str