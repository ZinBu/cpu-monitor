import os
import sys
import threading


def thread(func):
    """Decorator for running functions in a thread without execution control"""
    def run(*args, **kwargs):
        target = threading.Thread(target=func, args=args, kwargs=kwargs)
        target.deamon = True
        target.start()
        return target
    return run


def executable_file_path(file_path: str) -> str:
    """Determining the file path depending on how the application is executed"""
    if getattr(sys, 'frozen', False):
        exec_path = sys._MEIPASS
        file_path = os.path.join(exec_path, file_path)
    else:
        file_path = file_path
    return file_path
