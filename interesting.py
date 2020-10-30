#!/usr/bin/env python3

"""
Pick out frames that are sufficiently different in a video file.
"""

import os

import cv2
import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage.morphology import grey_erosion


def is_similar(a, b, threshold=0.95):
    """
    Return a measure of similarity between two frames of a video.

    a, b: cv2 images
    threshold: threshold in [0, 1] above which images are considered similar. A higher threshold
    means images must be more alike to be considered similar.

    Returns: True if the frames are similar.
    """
    return compute_similarity(a, b) > threshold


def compute_similarity(a, b):
    grey_a = cv2.cvtColor(a, cv2.COLOR_BGR2GRAY)
    grey_b = cv2.cvtColor(b, cv2.COLOR_BGR2GRAY)
    errors = grey_erosion(grey_a - grey_b, size=(3, 3))

    return 1 - np.sum(np.absolute(errors)) / (
        np.iinfo(a.dtype).max * a.shape[0] * a.shape[1]
    )


def read_to_interesting(video, frame, threshold=0.95):
    """
    Read through the video until the next sufficiently distinct frame, then return that frame.

    video: a VideoCapture object
    frame: the current frame of the video
    threshold: a number in [0, 1]. The lower it is, the more dissimilar consecutive frames must be
    to be interesting.

    Returns: a tuple of (index, frame) for the next interesting frame or None if the end of the video is reached
    """

    last_frame = frame
    while video.isOpened():
        ret, frame = video.read()
        if not ret:
            return None, None

        if not is_similar(last_frame, frame, threshold):
            return int(video.get(cv2.CAP_PROP_POS_FRAMES)), frame
    return None, None


if __name__ == "__main__":
    file = os.path.expanduser("~/Videos/353_recordings/2020-10-29T20:47:44.avi")
    video = cv2.VideoCapture(file)

    frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    similarities = np.empty((frames - 1,))

    i = 0
    _, last_frame = video.read()
    while video.isOpened():
        print(f"\r{i + 1} / {frames}", end="")
        ret, frame = video.read()
        if not ret:
            break

        similarities[i] = compute_similarity(last_frame, frame)
        i += 1
        last_frame = frame

    plt.plot(similarities)
    plt.xlabel("Frame number")
    plt.ylabel("Frame similarity (higher means more similar)")
    plt.show()
