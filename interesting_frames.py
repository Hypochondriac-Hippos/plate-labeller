#!/usr/bin/env python3

"""
Pick out frames that are sufficiently different in a video file.
"""

import os

import cv2
import matplotlib.pyplot as plt
import numpy as np

if __name__ == "__main__":
    file = os.path.expanduser("~/Videos/353_recordings/2020-10-29T21:22:56.avi")
    video = cv2.VideoCapture(file)

    frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    similarities = np.empty((frames - 1,))

    i = 0
    _, last_frame = video.read()
    while video.isOpened():
        print(f"\r {i + 1} / {frames}", end="")
        ret, frame = video.read()
        if not ret:
            break

        similarities[i] = cv2.matchTemplate(
            last_frame, frame, cv2.TM_CCORR_NORMED
        ).max()
        i += 1
        last_frame = frame

    plt.plot(similarities)
    plt.xlabel("Frame number")
    plt.ylabel("Frame similarity (higher means more similar)")
    plt.show()
