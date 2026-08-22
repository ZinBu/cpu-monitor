import sys

from PyQt6.QtWidgets import QApplication

from src.gui.database import ConfigDB
from src.gui.tray_counter import TrayCounter
from src.metrics.cpu import CpuMetric


if __name__ == "__main__":
    app = QApplication(sys.argv)
    db = ConfigDB()
    metric = CpuMetric(refresh_time_out_sec=1)
    mw = TrayCounter(metric=metric, db=db)
    mw.hide()
    sys.exit(app.exec())
