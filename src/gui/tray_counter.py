import typing
from functools import cached_property
from time import sleep

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QPointF
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QSystemTrayIcon, QMenu, QAction, qApp, QStyle

from src import config
from src import tools
from src.protocols import Metric, Database, DBConfigData

COLOR_TYPING = tuple[int, int, int]


class TrayCounter(QMainWindow):
    # Widget's slots
    TRAY_ICON_SLOT = QtCore.pyqtSignal(str)
    TRAY_ICON_COLOR_SLOT = QtCore.pyqtSignal(str)

    COLORS = config.Colors
    DEFAULT_COLOR = config.Colors.Auto

    _COLORS_HEAT_MAP = {
        35: config.Colors.PapayaWhip.value,
        45: config.Colors.PaleGreen.value,
        60: config.Colors.SteelBlue.value,
        75: config.Colors.DarkOrange.value,
        float('Inf'): config.Colors.Red.value
    }

    def __init__(self, metric: type[Metric], db: Database):
        # It's necessary
        QMainWindow.__init__(self)

        self.db = db
        self.metric = metric()

        self.setWindowTitle(self.metric.get_name())

        self._couple_slots_and_signals()

        self.tray_icon = QSystemTrayIcon(self)
        self.painter = QtGui.QPainter()

        self._selected_color = self.DEFAULT_COLOR
        # Set a default icon for an unpredictable situation
        self.default_icon = self.style().standardIcon(QStyle.SP_DesktopIcon)  # type: ignore
        self.set_up()
        self.run_monitoring()

    @tools.thread
    def run_monitoring(self) -> None:
        value_getter = self.metric.value_getter()
        while True:
            self.TRAY_ICON_SLOT.emit(value_getter())
            sleep(config.REFRESH_TIMEOUT_SEC)

    @cached_property
    def color_heat_map(self) -> list[tuple[int, COLOR_TYPING]]:
        return sorted(self._COLORS_HEAT_MAP.items(), key=lambda x: x[0])

    def _couple_slots_and_signals(self) -> None:
        self.TRAY_ICON_SLOT.connect(self.set_icon_in_tray)
        self.TRAY_ICON_COLOR_SLOT.connect(self.set_color)

    def set_icon_in_tray(self, digit: typing.Optional[str] = None) -> None:
        if not digit:
            self.tray_icon.setIcon(self.default_icon)
        else:
            icon = self.draw_digit(digit)
            self.tray_icon.setIcon(QIcon(icon))

    def set_color(self, color_name: str) -> None:
        previous_color_name = self._selected_color.name
        self._selected_color = self.COLORS[color_name]
        # Disable chosen color
        getattr(self, color_name).setDisabled(True)
        # Release the previous one
        getattr(self, previous_color_name).setDisabled(False)
        self._show_message(f'{config.COLOR_SET_MSG} {color_name}', config.MSG_DURATION_MS)
        self._save_config(color_name)

    def draw_digit(self, digit: str) -> QtGui.QPixmap:
        """Creates the icon and draw digits"""
        # Set digits position
        digit_place: tuple = config.ONE_DIGIT_POS if len(digit) > 1 else config.TWO_DIGIT_POS, 50
        # Creates canvas
        icon = QtGui.QPixmap(*config.MAP_SIZE)
        icon.fill(QtGui.QColor(config.ICON_BG))
        # Drawing
        self.painter.begin(icon)
        self.painter.setRenderHint(QtGui.QPainter.HighQualityAntialiasing)
        self.painter.setPen(QtGui.QColor(*self.get_digits_color(digit)))
        self.painter.setFont(QtGui.QFont(config.FONT, config.DIGIT_SIZE))
        self.painter.drawText(QPointF(*digit_place), digit)
        self.painter.end()
        return icon

    def get_digits_color(self, digit: str) -> COLOR_TYPING:
        if not self._selected_color.value:
            digit = int(digit)
            return next(color for limit, color in self.color_heat_map if digit < limit)
        return self._selected_color.value

    def set_up(self) -> None:
        self.set_icon_in_tray()
        self._load_and_set_color_config()
        tray_menu = QMenu()
        quit_action = QAction(config.CLOSE_MSG, self)
        quit_action.triggered.connect(self._close)

        # Create menu
        for color in self.COLORS:
            self._set_context_color(tray_menu, color)

        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        self._show_message(self.metric.get_startup_message())

    def _show_message(self, msg: str, time: int = config.MSG_DURATION_DEFAULT_MS) -> None:
        msg_type = QSystemTrayIcon.Information  # type: ignore
        self.tray_icon.showMessage(self.metric.get_name(), msg, msg_type, time)

    def _set_context_color(self, tray_menu: QMenu, color: config.Colors) -> None:
        color_action = QAction(color.name, self)
        if color == self._selected_color:
            color_action.setDisabled(True)
        setattr(self, color.name, color_action)
        color_action.triggered.connect(lambda: self.TRAY_ICON_COLOR_SLOT.emit(color.name))
        tray_menu.addAction(color_action)

    def _save_config(self, color: str) -> None:
        self.db.save_config(DBConfigData(color=color))

    def _load_and_set_color_config(self) -> None:
        conf = self.db.load_config()
        if conf.color:
            self._selected_color = self.COLORS[conf.color]

    def _close(self) -> None:
        self.tray_icon.hide()
        qApp.quit()
