import typing
import sys
from functools import cached_property

import psutil

from src.config import LINUX_PLATFORM
from src.protocols import Metric


class CpuMetric(Metric):
    
    def get_name(self) -> str:
        return 'CPU Monitor'
    
    def get_startup_message(self) -> str:
        return f"Отслеживаем {'температуру' if self.linux_platform else 'нагрузку'}"
    
    def value_getter(self) -> typing.Callable[[], str]:
        return (
            lambda: str(int(psutil.sensors_temperatures()['coretemp'][0].current))
            if self.linux_platform
            else lambda: str(int(psutil.cpu_percent()))
        )
    
    @cached_property
    def linux_platform(self) -> bool:
        return sys.platform == LINUX_PLATFORM
 