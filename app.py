#!/usr/bin/env python3

"""
Application to label ENPH 353 license plate videos
"""

import sys

from PyQt5 import QtWidgets
from python_qt_binding import loadUi


class LabelApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("labeller.ui", self)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = LabelApp()
    window.show()
    app.exec_()
