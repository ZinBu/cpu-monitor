import dataclasses
import typing
from typing import Protocol


@dataclasses.dataclass
class DBConfigData:
    color: str


class Metric(Protocol):

    def get_name(self) -> str:
        ...

    def get_startup_message(self) -> str:
        ...
    
    def value_getter(self) -> typing.Callable[[], str]:
        ...
    

class Database(Protocol):

    def load_config(self) -> DBConfigData:
        ...

    def save_config(self, conf: DBConfigData) -> None:
        ...
