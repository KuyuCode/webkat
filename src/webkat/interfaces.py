import typing

from webkat.types import Receive, Scope, Send


class ASGIApplicationInterface(typing.Protocol):
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None: ...


@typing.runtime_checkable
class ProtocolInterface(ASGIApplicationInterface, typing.Protocol):
    type: typing.ClassVar[str]


class MiddlewareInterface(ASGIApplicationInterface, typing.Protocol):
    def __init__(self, application: ASGIApplicationInterface): ...


_MiddlewareT = typing.TypeVar("_MiddlewareT", bound=MiddlewareInterface, covariant=True)


class MiddlewareFactoryInterface(typing.Protocol[_MiddlewareT]):
    def __call__(self, application: ASGIApplicationInterface) -> _MiddlewareT: ...
