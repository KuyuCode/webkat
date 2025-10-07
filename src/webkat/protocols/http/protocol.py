import typing
import asyncio
from typing_extensions import override

from webkat.protocols.base import BaseProtocol
from webkat.types import Event, Receive, Scope, Send

from .request import Request
from .response.base import HttpBaseResponse
from .response.plain import HttpPlainResponse

if typing.TYPE_CHECKING:
    from webkat.application import Application


class HttpProtocol(BaseProtocol, type="http"):
    def __init__(
        self, app: "Application", max_body: int = 1 * 1000 * 1000, cancel_on_disconnect: bool = True
    ) -> None:
        super().__init__(app)
        self.max_body: int = max_body
        self.cancel_on_disconnect: bool = cancel_on_disconnect

    async def on_raw_request(
        self, initial_event: Event, scope: Scope, receive: Receive, send: Send
    ) -> None:
        """
        Handles low-level request
        """
        request = Request(scope, receive, initial_event)

        response = await self.on_request(request)

        if response is not None:
            await response(scope, receive, send)

    async def on_request(self, request: Request) -> HttpBaseResponse | None:
        """
        Handles abstract request and returns response
        """
        return HttpPlainResponse(
            f"<h1>Hello, {request.method} {request.path}</h1>"
            f"<p>You sent {request.content_length}</p>",
            200,
            {"content-type": "text/html"},
        )

    @override
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        event = await receive()

        if event["type"] == "http.request":
            task = asyncio.create_task(self.on_raw_request(event, scope, receive, send))
        else:
            typing.assert_never(event["type"])

        event = await receive()

        if event["type"] == "http.disconnect":
            if not task.done() and self.cancel_on_disconnect:
                task.cancel()
            return

        typing.assert_never(event["type"])
