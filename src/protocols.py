import dataclasses
from abc import ABC, abstractmethod


@dataclasses.dataclass
class DBConfigData:
    color: str

class Metric(ABC):
    def __init__(self, refresh_time_out_sec: int) -> None:
        self._refresh_time_out_sec = refresh_time_out_sec

    @property
    def refresh_time_out_sec(self) -> float:
        return float(self._refresh_time_out_sec)

    @abstractmethod
    def get_name(self) -> str:
        ...

    @abstractmethod
    def get_startup_message(self) -> str:
        ...

    @abstractmethod
    def get_value(self) -> int:
        ...
    
class Database(ABC):
    @abstractmethod
    def load_config(self) -> DBConfigData:
        ...
    @abstractmethod
    def save_config(self, conf: DBConfigData) -> None:
        ...
