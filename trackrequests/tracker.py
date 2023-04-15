from typing import List, TypedDict, Optional
from localstack.extensions.api.aws import (
    RequestContext,
    ServiceRequest,
    ServiceResponse,
)
from localstack.http import Response


class InternalRequest(TypedDict):
    service: str
    operation: str
    payload: Optional[ServiceRequest]


class InternalResponse(TypedDict):
    status_code: int
    payload: Optional[ServiceResponse]


class Event(TypedDict):
    request: InternalRequest
    response: InternalResponse


class Tracker:
    events: List[Event]

    def __init__(self):
        self.events = []

    def add_response(self, context: RequestContext, response: Response) -> None:
        if context.service is None or context.operation is None:
            return

        self.events.append(
            {
                "request": {
                    "service": context.service.service_name,
                    "operation": context.operation.name,
                    "payload": context.service_request,
                },
                "response": {
                    "status_code": response.status_code,
                    "payload": context.service_response,
                },
            }
        )

    def stats(self) -> List[Event]:
        return self.events
