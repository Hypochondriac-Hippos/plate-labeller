#!/usr/bin/env python3

"""
Application to label ENPH 353 license plate videos
"""

import os
import sys

from PyQt5 import QtWidgets
from python_qt_binding import loadUi

VIDEO_LOCATION = os.path.expanduser("~/Videos/353_recordings")


class LabelApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("labeller.ui", self)

        self.file = None
        self.action_open.triggered.connect(self.open_video)

    def open_video(self):
        self.file = QtWidgets.QFileDialog.getOpenFileName(
            None, "Open Video", VIDEO_LOCATION, "Video Files (*.avi)"
        )[0]

        print(f"Opening {self.file}")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = LabelApp()
    window.show()
    app.exec_()
