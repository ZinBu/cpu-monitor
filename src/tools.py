import os
import sys
import threading


def thread(func):
    """Декоратор для запуска функций в потоке без контроля исполнения"""
    def run(*args, **kwargs):
        target = threading.Thread(target=func, args=args, kwargs=kwargs)
        # если False, то работает после завершения главного процесса
        target.setDaemon(True)
        target.start()
        return target
    return run


def executable_file_path(file_path: str) -> str:
    """Определение пути файла в зависимости от того как исполняется приложение"""
    if getattr(sys, 'frozen', False):
        exec_path = sys._MEIPASS
        file_path = os.path.join(exec_path, file_path)
    else:
        file_path = file_path
    return file_path
