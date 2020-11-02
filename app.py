#!/usr/bin/env python3

"""
Application to label ENPH 353 license plate videos
"""

import json
import os
import sys

import cv2
from PyQt5 import QtCore, QtGui, QtWidgets
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
        self.action_save.triggered.connect(self.save_labels)
        self.next_frame_button.clicked.connect(self.next_frame)
        self.prev_frame_button.clicked.connect(self.prev_frame)

        for widget in self.findChildren(QtWidgets.QLineEdit):
            widget.editingFinished.connect(self.update_label)

        self.labels = {"plates": dict(), "frames": dict()}

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
        self.show_visible()

    def open_video(self):
        f = QtWidgets.QFileDialog.getOpenFileName(
            None, "Open Video", VIDEO_LOCATION, "Video Files (*.avi)"
        )[0]

        if f == "":
            return

        self.file = f
        enable_all(self)
        self.labels = {"plates": dict(), "frames": dict()}

        self.video = video.VideoCapture(self.file)

        progress = QtWidgets.QProgressDialog(
            "Getting interesting frames...", "Stop", 0, len(self.video), self
        )
        progress.setModal(True)

        picker = PickFrames(self.video)
        for analyzed_frame in picker:
            progress.setValue(analyzed_frame)
            if progress.wasCanceled():
                break

        self.interesting_frames = picker.indices
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

    def update_label(self):
        i = self.sender().property("plate number")
        self.labels["plates"][i] = str(self.sender().text())

    def show_visible(self):
        """If labels are already recorded, make sure the check boxes match."""
        frame = self.interesting_frames[self.frame_num]
        if frame in self.labels["frames"]:
            labels = self.labels["frames"][frame]
            for i in range(1, 9):
                self.findChild(QtWidgets.QCheckBox, f"checkBox_{i}").setChecked(
                    labels is not None and i in labels
                )

    def record_labels(self):
        plates_in_frame = []
        for check_box in self.findChildren(QtWidgets.QCheckBox):
            if check_box.isChecked():
                plates_in_frame.append(check_box.property("plate_number"))

        if len(plates_in_frame) == 0:
            plates_in_frame = None

        self.labels["frames"][self.interesting_frames[self.frame_num]] = plates_in_frame

    def save_labels(self):
        """Write labels to a file."""
        self.record_labels()
        with open(f"{self.file}.json", "w") as f:
            json.dump(self.labels, f)


def enable_all(widget):
    """Recursively enable the widget and all its children"""
    widget.setEnabled(True)
    for child in widget.findChildren(QtWidgets.QWidget):
        enable_all(child)


class PickFrames:
    """Pick interesting frames from video, yielding a progress indicator along the way."""

    def __init__(self, video):
        self.video = video
        self.indices = None

    def __iter__(self):
        ret, frame = self.video.read()
        if not ret:
            raise RuntimeError("Couldn't read any frames")
        yield 0
        self.indices = [0]

        while self.video.isOpened() and frame is not None:
            last_frame = frame
            ret, frame = self.video.read()
            index = self.video.get(cv2.CAP_PROP_POS_FRAMES)
            yield index
            if ret and not interesting.is_similar(last_frame, frame):
                self.indices.append(index)


def pick_frames(video):
    """Return a list of indices of interesting frames."""


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = LabelApp()
    window.show()
    app.exec_()
