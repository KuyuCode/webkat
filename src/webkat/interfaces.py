import typing

from webkat.types import Receive, Scope, Send


@typing.runtime_checkable
class ProtocolInterface(typing.Protocol):
    type: typing.ClassVar[str]

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None: ...


class ApplicationInterface(typing.Protocol):
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None: ...
