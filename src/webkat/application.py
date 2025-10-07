import typing


from webkat.types import Receive, Scope, Send
from webkat.interfaces import ProtocolInterface
from webkat.protocols.lifespan import LifespanProtocol


class Application:
    def __init__(
        self,
        protocols: (
            list[typing.Callable[["Application"], ProtocolInterface] | ProtocolInterface] | None
        ) = None,
    ):
        if protocols is None:
            protocols = []

        self.lifespan: LifespanProtocol = LifespanProtocol(self)

        self._protocols: dict[str, ProtocolInterface] = {}
        for protocol in protocols:
            if not isinstance(protocol, ProtocolInterface):
                protocol = protocol(self)

            if protocol.type in self._protocols:
                raise ValueError(
                    "Protocol duplicate found: {protocol.type} {protocol}".format(protocol=protocol)
                )

            self._protocols[protocol.type] = protocol

        self._protocols[self.lifespan.type] = self.lifespan

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        protocol = self._protocols.get(scope["type"])
        if protocol is None:
            raise RuntimeError(f"Unsupported protocol: {scope['type']}")

        return await protocol(scope, receive, send)
