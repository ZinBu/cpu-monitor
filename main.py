import os
import shelve
import sys
import threading
from time import sleep

import psutil
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QSystemTrayIcon, \
    QMenu, QAction, qApp, QStyle


def thread(func):
    """ Декоратор для запуска функций в потоке без контроля исполнения """

    def run(*args, **kwargs):
        target = threading.Thread(target=func, args=args, kwargs=kwargs)
        # если False, то работает после завершения главного процесса
        target.setDaemon(True)
        target.start()
        return target

    return run


def executable_file_path(file_path: str):
    """
    Определение пути файла в зависимости от того как исполняется приложение
    :return: str
    """
    if getattr(sys, 'frozen', False):
        exec_path = sys._MEIPASS
        file_path = os.path.join(exec_path, file_path)
    else:
        file_path = file_path
    return file_path


class MainWindow(QMainWindow):
    TRAY_ICON_SLOT = QtCore.pyqtSignal(str)  # Слот для виджета
    TRAY_ICON_COLOR_SLOT = QtCore.pyqtSignal(str)  # Слот для виджета
    TIMEOUT = 1.5  # Период обновления виджета
    DEFAULT_COLOR = 'SteelBlue'
    DB_DIR = 'db'
    DB_NAME = os.path.join(DB_DIR, 'config')

    # Настройки значка
    MAP_SIZE = 64, 64
    DIGIT_SIZE = 45
    COLORS = dict(
        Red=(255, 0, 0),
        MediumVioletRed=(199, 21, 133),
        DeepPink=(255, 20, 147),
        OrangeRed=(255, 69, 0),
        DarkOrange=(255, 140, 0),
        PapayaWhip=(255, 239, 213),
        MediumOrchid=(186, 85, 211),
        PaleGreen=(152, 251, 152),
        Lime=(0, 255, 0),
        MediumSlateBlue=(123, 104, 238),
        DeepSkyBlue=(0, 191, 255),
        SteelBlue=(30, 144, 255)
    )

    def __init__(self):
        # Переопределяем конструктор класса
        # Обязательно нужно вызвать метод супер класса
        QMainWindow.__init__(self)
        self.setWindowTitle('CPU Monitor')
        # Связываем слоты с сигналами
        self.TRAY_ICON_SLOT.connect(self.set_icon)
        self.TRAY_ICON_COLOR_SLOT.connect(self.set_color)

        self.tray_icon = QSystemTrayIcon(self)
        self.painter = QtGui.QPainter()
        self.last_color = self.DEFAULT_COLOR
        # Задаем дефолтный цвет
        self.selected_color = self.COLORS[self.DEFAULT_COLOR]
        # Задаем дефолтную иконку, если что пойдет не так
        self.default_icon = self.style().standardIcon(QStyle.SP_DesktopIcon)
        # Ставим первоначальную иконку
        self.set_icon()
        # Выводим информационное сообщение, задаем цвет
        # и производим прочие настройки
        self.set_up()
        # Запускаем мониторинг
        self.run_monitoring()

    @thread
    def run_monitoring(self):
        """ Стар беспрерывного мониторинга """
        while True:
            # Онли линукс
            # print(psutil.sensors_temperatures())
            cpu_percent = str(psutil.cpu_percent()).split('.')[0]
            self.TRAY_ICON_SLOT.emit(cpu_percent)
            sleep(self.TIMEOUT)

    def set_icon(self, digit=None):
        """Установка иконки в трей"""
        if not digit:
            self.tray_icon.setIcon(self.default_icon)
        else:
            icon = self.draw_digit(digit)
            self.tray_icon.setIcon(QIcon(icon))

    def set_color(self, color_name):
        """
        Установка цвета, дизейблинг пункта меню
        и раздизейблинг пункта предыдущего выбора.
        """
        self.selected_color = self.COLORS[color_name]
        # Дизейблим выбранный цвет
        getattr(self, color_name).setDisabled(True)
        # И раздизейблим предыдущий
        getattr(self, self.last_color).setDisabled(False)
        self.last_color = color_name
        self._show_message(f'Установлен цвет: {color_name}', 100)
        self._save_config(color_name)

    def draw_digit(self, digit):
        """ Создание иконки и рисование цифры на ней """

        # Позиционируем цифру на виджете
        digit_place = 0 if len(digit) > 1 else 20, 50

        # Создаем холстик для рисования цифры иконку
        icon = QtGui.QPixmap(*self.MAP_SIZE)
        icon.fill(QtGui.QColor("transparent"))
        # Рисуем на холстике текст
        self.painter.begin(icon)
        self.painter.setRenderHint(QtGui.QPainter.HighQualityAntialiasing)
        self.painter.setPen(QtGui.QColor(*self.selected_color))
        self.painter.setFont(QtGui.QFont('Arial', self.DIGIT_SIZE))
        self.painter.drawText(*digit_place, digit)
        self.painter.end()
        return icon

    def set_up(self):
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
        self._show_message("Отслеживаем нагрузку")

    def _show_message(self, msg, time=2000):
        """Вывод сообщения в трее"""
        msg_type = QSystemTrayIcon.Information
        self.tray_icon.showMessage("CPU Monitor",  msg, msg_type, time)

    def _set_context_color(self, tray_menu, name):
        """
        Установка цвета в контекстное меню трея
        и создание атрибута для дисейбла.
        """
        color_action = QAction(name, self)
        if self.COLORS[name] == self.selected_color:
            color_action.setDisabled(True)
        setattr(self, name, color_action)
        color_action.triggered.connect(
            lambda: self.TRAY_ICON_COLOR_SLOT.emit(name)
        )
        tray_menu.addAction(color_action)

    def _save_config(self, color):
        db_path = executable_file_path(self.DB_NAME)
        with shelve.open(db_path) as db:
            db['color'] = color

    def _load_config(self):
        db_path = executable_file_path(self.DB_NAME)
        # Создадим папку, если ее нет
        if not os.path.exists(db_path + '.dat'):
            os.mkdir(os.path.join(os.getcwd(), self.DB_DIR))
        with shelve.open(db_path) as db:
            color = db.get('color')
            if color:
                self.selected_color = self.COLORS[color]

    def _close(self):
        self.tray_icon.hide()
        qApp.quit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.hide()
    sys.exit(app.exec())

