import typing
from time import sleep

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QPointF
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QSystemTrayIcon, QMenu, QAction, qApp, QStyle

from src import config
from src import tools
from src.protocols import Metric, Database, DBConfigData


# TODO Translate !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
class TrayCounter(QMainWindow):
    TRAY_ICON_SLOT = QtCore.pyqtSignal(str)  # Слот для виджета
    TRAY_ICON_COLOR_SLOT = QtCore.pyqtSignal(str)  # Слот для виджета
    TIMEOUT = 2  # Период обновления виджета
    DEFAULT_COLOR = 'Auto'

    # Настройки значка
    COLORS = config.COLORS

    def __init__(self, metric: type[Metric], db: Database):
        # Переопределяем конструктор класса
        # Обязательно нужно вызвать метод супер класса
        self.db = db
        self.metric = metric()
        QMainWindow.__init__(self)
        self.setWindowTitle(self.metric.get_name())
        # Связываем слоты с сигналами
        self.TRAY_ICON_SLOT.connect(self.set_icon)
        self.TRAY_ICON_COLOR_SLOT.connect(self.set_color)

        self.tray_icon = QSystemTrayIcon(self)
        self.painter = QtGui.QPainter()
        self._last_color_name = self.DEFAULT_COLOR
        # Задаем дефолтный цвет
        self._selected_color_value = self.COLORS[self.DEFAULT_COLOR]
        # Задаем дефолтную иконку, если что пойдет не так
        self.default_icon = self.style().standardIcon(QStyle.SP_DesktopIcon)  # type: ignore
        # Ставим первоначальную иконку
        self.set_icon()
        # Выводим информационное сообщение, задаем цвет
        # и производим прочие настройки
        self.set_up()
        # Запускаем мониторинг
        self.run_monitoring()

    @tools.thread
    def run_monitoring(self) -> None:
        """ Старт беспрерывного мониторинга """
        value_getter = self.metric.value_getter()
        while True:
            self.TRAY_ICON_SLOT.emit(value_getter())
            sleep(config.REFRESH_TIMEOUT_SEC)

    def set_icon(self, digit: typing.Optional[str] = None) -> None:
        """Установка иконки в трей"""
        if not digit:
            self.tray_icon.setIcon(self.default_icon)
        else:
            icon = self.draw_digit(digit)
            self.tray_icon.setIcon(QIcon(icon))

    def set_color(self, color_name: str) -> None:
        """Установка цвета, дизейблинг пункта меню и раздизейблинг пункта предыдущего выбора."""
        self._selected_color_value = self.COLORS[color_name]
        # Дизейблим выбранный цвет
        getattr(self, color_name).setDisabled(True)
        # И раздизейблим предыдущий
        getattr(self, self._last_color_name).setDisabled(False)
        self._last_color_name = color_name
        self._show_message(f'{config.COLOR_SET_MSG} {color_name}', 100)
        self._save_config(color_name)

    def draw_digit(self, digit: str) -> QtGui.QPixmap:
        """Создание иконки и рисование цифры на ней"""
        # Позиционируем цифру на виджете
        digit_place: tuple = 0 if len(digit) > 1 else 20, 50
        # Создаем холстик для рисования цифры иконку
        icon = QtGui.QPixmap(*config.MAP_SIZE)
        icon.fill(QtGui.QColor("transparent"))
        # Рисуем на холстике текст
        self.painter.begin(icon)
        self.painter.setRenderHint(QtGui.QPainter.HighQualityAntialiasing)
        self.painter.setPen(QtGui.QColor(*self.get_digits_color(digit)))
        self.painter.setFont(QtGui.QFont('Arial', config.DIGIT_SIZE))
        self.painter.drawText(QPointF(*digit_place), digit)
        self.painter.end()
        return icon

    def get_digits_color(self, digit: str) -> tuple[int, int, int]:
        if not self._selected_color_value:
            digit = int(digit)
            if digit < 40:
                return self.COLORS['PaleGreen']
            elif digit < 55:
                return self.COLORS['SteelBlue']
            elif digit < 75:
                return self.COLORS['DarkOrange']
            else:
                return self.COLORS['Red']
        return self._selected_color_value

    def set_up(self) -> None:
        """Вывод информационного окна"""
        # Объявим и добавим действия для работы с иконкой системного трея
        self._load_config()
        tray_menu = QMenu()
        quit_action = QAction("Закрыть", self)
        quit_action.triggered.connect(self._close)
        # Строим меню всех цветов
        for name in self.COLORS:
            self._set_context_color(tray_menu, name)

        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        self._show_message(self.metric.get_startup_message())

    def _show_message(self, msg: str, time: int = 2000) -> None:
        """Вывод сообщения в трее"""
        msg_type = QSystemTrayIcon.Information  # type: ignore
        self.tray_icon.showMessage(self.metric.get_name(), msg, msg_type, time)

    def _set_context_color(self, tray_menu: QMenu, name: str) -> None:
        """
        Установка цвета в контекстное меню трея
        и создание атрибута для дисейбла.
        """
        color_action = QAction(name, self)
        if self.COLORS[name] == self._selected_color_value:
            color_action.setDisabled(True)
        setattr(self, name, color_action)
        color_action.triggered.connect(lambda: self.TRAY_ICON_COLOR_SLOT.emit(name))
        tray_menu.addAction(color_action)

    def _save_config(self, color: str) -> None:
        self.db.save_config(DBConfigData(color=color))

    def _load_config(self) -> None:
        conf = self.db.load_config()
        if conf.color:
            self._selected_color_value = self.COLORS[conf.color]
            self._last_color_name = conf.color

    def _close(self) -> None:
        self.tray_icon.hide()
        qApp.quit()
