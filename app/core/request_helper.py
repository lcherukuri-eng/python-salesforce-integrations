import logging
import requests

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from collections.abc import Callable

logger = logging.getLogger(__name__)

session = requests.session()

retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[
        429,
        500,
        502,
        503,
        504
    ]
)

adapter = HTTPAdapter(
    max_retries=retry_strategy
)

session.mount(
    "https://",
    adapter
)

session.mount(
    "http://",
    adapter
)

logger.info(
    "Session initialized with retry strategy"
)


def salesforce_request(
    method: str,
    url: str,
    headers: dict,
    params=None,
    json=None,
    data=None,
    timeout=30,
    refresh_token: Callable | None = None
):
    logger.info(
        f"Salesforce {method} request"
    )

    response = session.request(
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

        retry_headers = headers.copy()

        retry_headers["Authorization"] = (
            f"Bearer {new_token_data['access_token']}"
        )

        response = session.request(
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

def data_cloud_request(
    method: str,
    url: str,
    headers: dict,
    params=None,
    json=None,
    data=None,
    timeout=30,
    refresh_token: Callable | None = None
):
    logger.info(
        f"Data Cloud {method} request"
    )

    response = session.request(
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

        retry_headers = headers.copy()

        retry_headers["Authorization"] = (
            f"Bearer {new_token_data['access_token']}"
        )

        response = session.request(
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