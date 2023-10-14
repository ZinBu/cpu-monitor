import typing
from typing import Protocol


class Metric(Protocol):

    def get_name(self) -> str:
        ...

    def get_startup_message(self) -> str:
        ...
    
    def value_getter(self) -> typing.Callable[[], str]:
        ...
    