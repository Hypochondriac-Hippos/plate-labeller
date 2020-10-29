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
        self._frame_num = None
        self.action_open.triggered.connect(self.open_video)
        self.next_frame_button.clicked.connect(self.next_frame)
        self.prev_frame_button.clicked.connect(self.prev_frame)

    @property
    def frame_num(self):
        return self._frame_num

    @frame_num.setter
    def frame_num(self, n):
        if n < 0 or n >= self.video.get(cv2.CAP_PROP_FRAME_COUNT):
            raise ValueError(f"There is no frame {n}")
        self._frame_num = n
        self.enable_frame_buttons()

    def open_video(self):
        f = QtWidgets.QFileDialog.getOpenFileName(
            None, "Open Video", VIDEO_LOCATION, "Video Files (*.avi)"
        )[0]

        if f == "":
            return

        self.file = f
        enable_all(self)

        self.video = cv2.VideoCapture(self.file)
        self.frame_num = 0
        self.show_frame()

    def show_frame(self):
        self.video.set(cv2.CAP_PROP_POS_FRAMES, self.frame_num)
        ret, frame = self.video.read()
        if not ret:
            print(f"Can't display frame {self.frame_num}")
            return

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pixmap = QtGui.QPixmap.fromImage(
            QtGui.QImage(
                frame, frame.shape[1], frame.shape[0], QtGui.QImage.Format_RGB888
            )
        )
        self.frame.setPixmap(pixmap)

    def next_frame(self):
        self.frame_num += 1
        self.show_frame()

    def prev_frame(self):
        self.frame_num -= 1
        self.show_frame()

    def enable_frame_buttons(self):
        self.next_frame_button.setEnabled(
            self.frame_num + 1 < self.video.get(cv2.CAP_PROP_FRAME_COUNT)
        )
        self.prev_frame_button.setEnabled(self.frame_num > 0)


def enable_all(widget):
    """Recursively enable the widget and all its children"""
    widget.setEnabled(True)
    for child in widget.findChildren(QtWidgets.QWidget):
        enable_all(child)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = LabelApp()
    window.show()
    app.exec_()
