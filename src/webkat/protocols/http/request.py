from multidict import CIMultiDict
from webkat.util import parse_headers
from webkat.types import Event, Receive, Scope


class Request:
    def __init__(self, scope: Scope, receive: Receive, initial_event: Event):
        self._initial_event: Event = initial_event
        self._receive: Receive = receive
        self._scope: Scope = scope
        self.root_path: str = scope["root_path"]

        self.method: str = scope["method"]
        self.scheme: str = scope["scheme"]

        self.path: str = scope["path"]
        self.raw_path: bytes = scope["raw_path"]
        self.query_string: bytes = scope["query_string"]

        self.headers: CIMultiDict[str] = parse_headers(scope["headers"])

        self.server: tuple[str, int] = scope["server"]
        self.client: tuple[str, int] = scope["client"]
        self.http_version: str = scope["http_version"]

        content_length = self.headers.get("Content-Length", None)

        self.content_length: int | None = None
        if content_length is not None and content_length.isdigit():
            self.content_length = int(content_length)

        self._body: bytes | None = None
        self._body_read: bool = False

    @property
    def body_read(self):
        return self._body_read

    def body(self) -> bytes:
        if self.method == "GET":
            raise TypeError("GET requests doesn't have body")

        if self._body is None:
            raise ValueError("Body was not read")

        return self._body

    async def read(self) -> bytes:
        if not hasattr(self, "_initial_event") or self._body_read:
            raise Exception("Resource exhausted")

        event = self._initial_event

        if self.content_length is None:
            raise ValueError("Unable to read: don't know how much")

        body = event["body"]
        while event["type"] == "http.request" and event["more_body"]:
            event = await self._receive()
            body += event["body"]

            if len(body) > self.content_length:
                raise OverflowError("Client sent too much data")

        if event["type"] == "http.disconnect":
            raise ConnectionResetError("Client disconnected while sending request body")

        self._body = body
        self._body_read = True
        del self._initial_event

        return body
