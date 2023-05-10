
from __future__ import annotations
from events.models import Event
import json
import requests
from collections.abc import MutableMapping
from typing import Any
from requests import RequestException, Response as RequestsResponse


def get_event_info(events: Event):
    event_info = {}
    for event in events:
        event_info = {
            'id': event.id,
            'title': event.title,
            'description': event.description,
            'attendee': event.attendee,
            'start_at': event.start_at,
            'end_at': event.end_at,
            'location': event.location
        }

    return event_info
    
    

class ThirdPartyAPIConnectionError(Exception):
    def __init__(self, response_code: int, response_data: dict[str, Any]):
        """Set response code and response data."""
        self.response_code = response_code
        self.response_data = response_data
        super().__init__('ThirdPartyAPIConnectionError')


class Response:
    """Data class for response third party request response."""
    response_data: Any
    status_code: int
    headers: MutableMapping[str, str] | None

    def __init__(
            self,
            response_data: Any,
            status_code: int,
            headers: MutableMapping[str, str] | None = None,
            response_object: RequestsResponse | None = None,
    ):
        """Set data."""
        self.response_data = response_data
        self.status_code = status_code
        self.headers = headers
        self.response_object = response_object


def request_wrapper(
        method: str,
        url: str,
        headers: MutableMapping[str, str] | None,
        params: MutableMapping[str, str] | None = None,
        post_data: dict[str, Any] | None = None,
        verify: bool = True,
        conn_timeout: int = 30,
        read_timeout: int = 45,
):
    """Requests wrapper library used to handle HTTP requests to third party libraries."""
    _conn_timeout = conn_timeout if conn_timeout else conn_timeout
    _read_timeout = read_timeout if read_timeout else read_timeout

    if post_data is None:
        post_data = {}

    try:
        response = requests.request(
            method,
            url,
            headers=headers,
            json=post_data,
            timeout=(_conn_timeout, _read_timeout),
            params=params,
            verify=verify,
        )

        status_code = response.status_code

        try:
            response_data = response.json()
            headers = response.headers
        except json.JSONDecodeError:
            response_data = {}

        return Response(
            response_data=response_data, headers=headers, status_code=status_code, response_object=response
        )
    except RequestException as request_error:
        raise ThirdPartyAPIConnectionError(
            response_code=request_error.response.status_code if request_error.response else 0,
            response_data={'message': str(request_error)},
        ) from request_error
 