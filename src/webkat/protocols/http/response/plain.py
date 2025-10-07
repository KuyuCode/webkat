from multidict import CIMultiDict
from typing_extensions import override

from .base import HttpBaseResponse
from webkat.types import Receive, Scope, Send


class HttpPlainResponse(HttpBaseResponse):
    def __init__(self, content: bytes | str, status: int, headers: dict[str, str] | None = None):
        self.content: bytes = content if isinstance(content, bytes) else content.encode("utf-8")
        self.status: int = status
        self.headers: dict[str, str] = headers or {}

    def formatted_headers(self) -> list[tuple[bytes, bytes]]:
        headers = CIMultiDict(self.headers)
        headers["content-length"] = str(len(self.content))

        return [(k.encode("utf-8"), v.encode("utf-8")) for k, v in headers.items()]

    @override
    async def __call__(self, _: Scope, receive: Receive, send: Send) -> None:
        await send(
            {
                "type": "http.response.start",
                "status": self.status,
                "headers": self.formatted_headers(),
            }
        )
        await send({"type": "http.response.body", "body": self.content, "more_body": False})
