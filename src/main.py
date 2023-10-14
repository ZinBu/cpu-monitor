import sys

from PyQt5.QtWidgets import QApplication

from src.gui.tray_counter import TrayCounter
from src.metrics.cpu import CpuMetric


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mw = TrayCounter(metric=CpuMetric)
    mw.hide()
    sys.exit(app.exec())
