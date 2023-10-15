import sys

from PyQt5.QtWidgets import QApplication

from src.gui.database import ConfigDB
from src.gui.tray_counter import TrayCounter
from src.metrics.cpu import CpuMetric


if __name__ == "__main__":
    app = QApplication(sys.argv)
    db = ConfigDB()
    mw = TrayCounter(metric=CpuMetric, db=db)
    mw.hide()
    sys.exit(app.exec())
