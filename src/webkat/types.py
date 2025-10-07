import typing
from collections.abc import Awaitable


Scope = dict[str, typing.Any]
Event = dict[str, typing.Any]

Receive = typing.Callable[[], Awaitable[Event]]
Send = typing.Callable[[Event], Awaitable[None]]
