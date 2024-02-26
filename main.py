
import os
import shutil
import subprocess
import tempfile
import time
import traceback
from types import TracebackType
import zipfile
from win32event import CreateMutex
from win32api import CloseHandle, GetLastError
from winerror import ERROR_ALREADY_EXISTS
from PyQt5.QtWidgets import QApplication, QMainWindow, qApp, QWidget
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QMovie
import sys
import multiprocessing
import json
import requests
import psutil

from datetime import datetime

from windows.HomeWindow import HomeWindow


def myexcepthook(type, value, tb: TracebackType):

    formatted_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    with open("errorslog.txt", "a", encoding='utf-8') as f:
        f.write(f"==>> Time: {formatted_time}\n")
        f.write(f"==>> Type: {type}\n")
        f.write(f"==>> Value: {value}\n")
        f.write("==>> Traceback:\n")
        traceback.print_tb(tb, file=f)
        f.write("\n")

    print(f"==>> Type: {type}")
    print(f"==>> Value: {value}")
    traceback.print_tb(tb)


def main():
    pass


if __name__ == '__main__':
    multiprocessing.freeze_support()

    app = QApplication([])
    from ui.sapp import style
    app.setStyleSheet(style)
    homeWd = HomeWindow()
    homeWd.show()

    sys.excepthook = myexcepthook
    sys.exit(app.exec_())
