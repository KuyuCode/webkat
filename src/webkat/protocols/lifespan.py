import typing
from contextlib import AsyncExitStack

from typing_extensions import override
from fundi import CallableInfo, ainject

from webkat.types import Receive, Scope, Send
from webkat.protocols.base import BaseProtocol

if typing.TYPE_CHECKING:
    from webkat.application import Application


class LifespanProtocol(BaseProtocol, type="lifespan"):

    def __init__(
        self,
        app: "Application",
        sublifespans: list[CallableInfo[typing.Any]] | None = None,
        stack: AsyncExitStack | None = None,
    ) -> None:
        super().__init__(app)

        self._stack: AsyncExitStack = stack or AsyncExitStack()
        self._sublifespans: list[CallableInfo[typing.Any]] = []

        if sublifespans:
            for lifespan in sublifespans:
                self.include(lifespan)

    def include(self, lifespan: CallableInfo[typing.Any]):
        assert (
            lifespan.generator or lifespan.context
        ), "Lifespan connection can be made only with lifespan-dependencies"

        self._sublifespans.append(lifespan)

    def remove(self, lifespan: CallableInfo[typing.Any]):
        self._sublifespans.remove(lifespan)

    @override
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        while True:
            event = await receive()

            match event["type"]:
                case "lifespan.startup":
                    try:
                        for lifespan in self._sublifespans:
                            await ainject(
                                {**scope, "scope": {**scope}, "application": self.application},
                                lifespan,
                                self._stack,
                            )
                        await send({"type": "lifespan.startup.complete"})
                    except Exception as exc:
                        await send({"type": "lifespan.startup.failed", "message": repr(exc)})

                case "lifespan.shutdown":
                    try:
                        await self._stack.aclose()

                        await send({"type": "lifespan.shutdown.complete"})
                    except Exception as exc:
                        await send({"type": "lifespan.shutdown.failed", "message": repr(exc)})

                    return

                case _:
                    typing.assert_never(event["type"])
