import typing
from typing_extensions import override

from webkat.protocols.base import BaseProtocol
from webkat.types import Receive, Scope, Send

from .request import Request
from .response.plain import HttpPlainResponse

if typing.TYPE_CHECKING:
    from webkat.application import Application


class HttpProtocol(BaseProtocol, type="http"):
    def __init__(self, app: "Application", max_body: int = 1 * 1000 * 1000) -> None:
        super().__init__(app)
        self.max_body: int = max_body

    async def _middleware(self, scope: Scope, receive: Receive, send: Send) -> None:
        """
        Handles low-level request
        """

        await self._app(scope, receive, send)

    async def _app(self, scope: Scope, receive: Receive, send: Send) -> None:
        """
        Handles abstract request and returns response
        """
        request = Request(scope, receive)

        response = HttpPlainResponse(
            f"<h1>Hello, {request.method} {request.path}</h1>"
            f"<p>You sent {request.content_length}</p>",
            200,
            {"content-type": "text/html"},
        )

        await response(scope, receive, send)

    @override
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        await self._middleware(scope, receive, send)
