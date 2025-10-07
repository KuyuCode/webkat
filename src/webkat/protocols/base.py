import typing
from typing import ClassVar
from abc import ABC, abstractmethod

from webkat.types import Receive, Scope, Send

if typing.TYPE_CHECKING:
    from webkat.application import Application

P = typing.ParamSpec("P")
T = typing.TypeVar("T")


class BaseProtocol(ABC):
    type: ClassVar[str]

    def __init__(self, application: "Application") -> None:
        self.application: "Application" = application
        super().__init__()

    def __init_subclass__(cls, **kwargs: typing.Any) -> None:
        if "type" in kwargs:
            cls.type = kwargs.pop("type")

    @classmethod
    def factory(
        cls: typing.Callable[typing.Concatenate["Application", P], T],
    ) -> typing.Callable[P, typing.Callable[["Application"], T]]:
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> typing.Callable[["Application"], T]:
            return lambda app: cls(app, *args, **kwargs)

        return wrapper

    @abstractmethod
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None: ...
