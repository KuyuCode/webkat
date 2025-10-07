from abc import ABC, abstractmethod

from webkat.types import Receive, Scope, Send


class HttpBaseResponse(ABC):
    @abstractmethod
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None: ...
