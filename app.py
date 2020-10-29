#!/usr/bin/env python3

"""
Application to label ENPH 353 license plate videos
"""

import os
import sys

import cv2
from PyQt5 import QtGui, QtWidgets
from python_qt_binding import loadUi

VIDEO_LOCATION = os.path.expanduser("~/Videos/353_recordings")


class LabelApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("labeller.ui", self)

        self.file = None
        self.video = None
        self.action_open.triggered.connect(self.open_video)

    def open_video(self):
        self.file = QtWidgets.QFileDialog.getOpenFileName(
            None, "Open Video", VIDEO_LOCATION, "Video Files (*.avi)"
        )[0]

        self.video = cv2.VideoCapture(self.file)
        self.show_frame(0)

    def show_frame(self, n):
        if n >= self.video.get(cv2.CAP_PROP_FRAME_COUNT):
            print(f"There is no frame {n}")
            return

        self.video.set(cv2.CAP_PROP_POS_FRAMES, n)
        ret, frame = self.video.read()
        if not ret:
            print(f"Can't display frame {n}")
            return

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pixmap = QtGui.QPixmap.fromImage(
            QtGui.QImage(
                frame, frame.shape[1], frame.shape[0], QtGui.QImage.Format_RGB888
            )
        )
        print(pixmap)
        self.frame.setPixmap(pixmap)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = LabelApp()
    window.show()
    app.exec_()
