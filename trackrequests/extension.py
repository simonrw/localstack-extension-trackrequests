import json
from datetime import datetime

from localstack.aws.api import RequestContext
from localstack.extensions.api import Extension, http, aws
from localstack.http import Request, Response
from .tracker import Tracker

class Encoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        else:
            return repr(o)


class MyExtension(Extension):
    name = "trackrequests"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tracker = Tracker()

    def update_gateway_routes(self, router: http.Router[http.RouteHandler]):
        router.add("/stats", endpoint=self.endpoint)

    def update_response_handlers(self, handlers: aws.CompositeResponseHandler):
        handlers.append(self.response_handler)

    def response_handler(
        self, chain: aws.HandlerChain, context: RequestContext, response: Response
    ):
        if context.service is None:
            return

        self.tracker.add_response(context, response)

    def endpoint(self, request: Request, **kwargs) -> str:
        return json.dumps(self.tracker.stats(), cls=Encoder)
