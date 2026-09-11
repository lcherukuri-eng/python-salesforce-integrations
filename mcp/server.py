import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from mcp.server.mcpserver import MCPServer
from app.services.customer360_service import (
    get_account_360,
    get_ai_customer_360_summary,
    get_customer_graph_context,
    customer_interaction_summary
)

mcp = MCPServer(
    name="Customer360 MCP",
    version="1.0.0"
)

@mcp.tool()
async def get_customer_360(account_name: str):
    """
    Retrieve customer 360 information including
    account details, opportunities, pipeline metrics,
    and business insights.
    """
    return await get_account_360(account_name)

@mcp.tool()
async def get_customer_360_ai(
    account_name: str
):
    """
    Retrieve Customer 360 data and generate
    an AI-powered business summary.
    """

    return await get_ai_customer_360_summary(
        account_name
    )

@mcp.tool()
async def get_customer_graph(account_id: str):
    """
    Retrieve customer context using Salesforce Data Graph.
    """
    return await get_customer_graph_context(account_id)

@mcp.tool()
async def customer_interaction_ai(
    account_id: str,
    event_id: str,
    email: str,
    contact_id: str,
    event_type: str,
    product_sku: str,
    event_value: int
):

    """
    Retrieve customer context from Data Graph, log an interaction
    to Data Cloud, and generate AI-powered recommendations using Claude.
    """
    
    return await customer_interaction_summary(
        account_id=account_id,
        event_id=event_id,
        email=email,
        contact_id=contact_id,
        event_type=event_type,
        product_sku=product_sku,
        event_value=event_value
    )

if __name__ == "__main__":
    import asyncio

    asyncio.run(
        mcp.run_stdio_async()
    )
