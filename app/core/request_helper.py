import logging
from httpx import AsyncClient

from collections.abc import Callable

logger = logging.getLogger(__name__)

HTTP_TIMEOUT = 30

client: AsyncClient | None = None

async def initialize_client():
    global client

    client = AsyncClient(timeout=HTTP_TIMEOUT)
    
    logger.info("Async HTTP client initialized")

async def close_client():
    global client

    if client is not None:
        await client.aclose()

        logger.info("Async HTTP client closed")

async def salesforce_request(
    method: str,
    url: str,
    headers: dict,
    params=None,
    json=None,
    data=None,
    timeout=30,
    refresh_token: Callable | None = None
):

    if client is None:
        raise RuntimeError(
            "HTTP client has not been initialized"
        )
    
    logger.info(
        f"Salesforce {method} request"
    )

    response = await client.request(
        method=method,
        url=url,
        headers=headers,
        params=params,
        json=json,
        data=data,
        timeout=timeout
    )

    if (
        response.status_code == 401
        and refresh_token is not None
    ):
        logger.warning(
            "Salesforce returned 401. "
            "Refreshing token and retrying once."
        )

        new_token_data = refresh_token()

        logger.info("Retrying request with refreshed token")

        retry_headers = headers.copy()

        retry_headers["Authorization"] = (
            f"Bearer {new_token_data['access_token']}"
        )

        response = await client.request(
            method=method,
            url=url,
            headers=retry_headers,
            params=params,
            json=json,
            data=data,
            timeout=timeout
        )

    response.raise_for_status()

    return response

async def data_cloud_request(
    method: str,
    url: str,
    headers: dict,
    params=None,
    json=None,
    data=None,
    timeout=30,
    refresh_token: Callable | None = None
):

    if client is None:
            raise RuntimeError(
                "HTTP client has not been initialized"
            )
    
    logger.info(
        f"Data Cloud {method} request"
    )

    response = await client.request(
        method=method,
        url=url,
        headers=headers,
        params=params,
        json=json,
        data=data,
        timeout=timeout
    )

    if (
        response.status_code == 401
        and refresh_token is not None
    ):
        logger.warning(
            "Data Cloud returned 401. "
            "Refreshing token and retrying once."
        )

        new_token_data = refresh_token()

        logger.info("Retrying request with refreshed token")

        retry_headers = headers.copy()

        retry_headers["Authorization"] = (
            f"Bearer {new_token_data['access_token']}"
        )

        response = await client.request(
            method=method,
            url=url,
            headers=retry_headers,
            params=params,
            json=json,
            data=data,
            timeout=timeout
        )

    response.raise_for_status()

    return response