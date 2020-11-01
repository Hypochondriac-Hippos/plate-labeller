#!/usr/bin/env python3

"""
Application to label ENPH 353 license plate videos
"""

import os
import sys

import cv2
from PyQt5 import QtGui, QtWidgets
from python_qt_binding import loadUi

import interesting
import video

VIDEO_LOCATION = os.path.expanduser("~/Videos/353_recordings")


class LabelApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("labeller.ui", self)

        self.file = None
        self._frame_num = None
        self.video = None
        self.interesting_frames = None

        self.action_open.triggered.connect(self.open_video)
        self.next_frame_button.clicked.connect(self.next_frame)
        self.prev_frame_button.clicked.connect(self.prev_frame)

        self.labels = {}

    @property
    def frame_num(self):
        return self._frame_num

    @frame_num.setter
    def frame_num(self, n):
        if n < 0 or n >= len(self.interesting_frames):
            raise ValueError(f"There is no frame {n}")
        self._frame_num = n
        self.setWindowTitle(
            f"{os.path.basename(self.file)} [{self._frame_num + 1}/{len(self.interesting_frames)}]"
        )
        self.enable_frame_buttons()
        self.show_frame()

    def open_video(self):
        f = QtWidgets.QFileDialog.getOpenFileName(
            None, "Open Video", VIDEO_LOCATION, "Video Files (*.avi)"
        )[0]

        if f == "":
            return

        self.file = f
        enable_all(self)

        self.video = video.VideoCapture(self.file)
        self.interesting_frames = pick_frames(self.video)

        self.frame_num = 0

    def show_frame(self):
        frame = cv2.cvtColor(
            self.video[self.interesting_frames[self.frame_num]], cv2.COLOR_BGR2RGB
        )
        pixmap = QtGui.QPixmap.fromImage(
            QtGui.QImage(
                frame, frame.shape[1], frame.shape[0], QtGui.QImage.Format_RGB888
            )
        )
        self.frame.setPixmap(pixmap)

    def next_frame(self):
        self.record_labels()
        self.frame_num += 1

    def prev_frame(self):
        self.record_labels()
        self.frame_num -= 1

    def enable_frame_buttons(self):
        self.next_frame_button.setEnabled(
            self.frame_num + 1 < len(self.interesting_frames)
        )
        self.prev_frame_button.setEnabled(self.frame_num > 0)

    def record_labels(self):
        plates_in_frame = dict()
        for text_box in self.findChildren(QtWidgets.QLineEdit):
            i = int(text_box.objectName()[5])
            text = text_box.text()
            if text != "":
                plates_in_frame[i] = text

        if len(plates_in_frame) == 0:
            plates_in_frame = None

        self.labels[self.interesting_frames[self.frame_num]] = plates_in_frame


def enable_all(widget):
    """Recursively enable the widget and all its children"""
    widget.setEnabled(True)
    for child in widget.findChildren(QtWidgets.QWidget):
        enable_all(child)


def pick_frames(video):
    """Return a list of indices of interesting frames."""
    ret, frame = video.read()
    if not ret:
        raise RuntimeError("Couldn't read any frames")
    indices = [0]
    i, frame = interesting.read_to_interesting(video, frame)
    l = len(video)
    while frame is not None:
        print(f"\r{i} / {l}", end="")
        indices.append(i)
        i, frame = interesting.read_to_interesting(video, frame)

    return indices


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = LabelApp()
    window.show()
    app.exec_()
