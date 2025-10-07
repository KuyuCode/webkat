import typing

if typing.TYPE_CHECKING:
    from webkat.application import Application

A = typing.TypeVar("A", bound="Application", covariant=True)
P = typing.ParamSpec("P")
R = typing.TypeVar("R")


def requires_app(
    func: typing.Callable[typing.Concatenate[A, P], R],
) -> typing.Callable[P, typing.Callable[[A], R]]:
    def argument_collector(*args: P.args, **kwargs: P.kwargs) -> typing.Callable[[A], R]:
        def instantiator(app: A) -> R:
            return func(app, *args, **kwargs)

        return instantiator

    return argument_collector
