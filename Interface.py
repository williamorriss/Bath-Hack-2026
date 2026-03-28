import threading
from queue import Queue
from time import sleep

import cv2
from PyQt6.QtGui import QPainter, QImage, QPixmap
from PyQt6.QtWidgets import QWidget, QMainWindow, QPushButton, QLabel, QGridLayout, QApplication
from PyQt6.QtCore import Qt, QPoint, QTimer
from PyQt6.QtMultimedia import QCamera, QMediaCaptureSession, QMediaDevices
from PyQt6.QtMultimediaWidgets import QVideoWidget
from keyboard import Recorder
from datetime import timedelta
from CameraAI.ai_vision import VisionManager
import numpy as np
from typing import cast

from app import App


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main window")
        central = QWidget()

        self.setCentralWidget(central)
        layout = QGridLayout(central)

        # video
        self.video_feed = VideoFeed(800, 600)
        layout.addWidget(self.video_feed, 0, 1)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        # start feed
        self.start = QPushButton("Start feed")
        self.start.setFixedSize(100,100)
        layout.addWidget(self.start, 1, 1)
        self.session = QMediaCaptureSession()
        self.start.clicked.connect(self.video_feed.activate)

        # bindings
        self.recorder = Recorder(duration=timedelta(seconds=5))
        layout.addWidget(self.recorder, 2, 1)

        print(f"VideoFeed geometry: {self.video_feed.geometry()}")
        print(f"VideoFeed size: {self.video_feed.size()}")

class Video:
    def __init__(self, width: int, height: int):
        self.frame_width = width
        self.frame_height = height
        self.vision = VisionManager(cap_no=1)

    def get_frame(self) -> QPixmap | None:
        bgra = self.vision.get_frame()
        if bgra is not None:
            frame = cv2.resize(bgra, (self.frame_width, self.frame_height))
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGRA2RGB)
            h, w, ch = rgb.shape
            q_image = QImage(rgb.data, w, h, ch * w, QImage.Format.Format_RGB888).copy() # type: ignore
            return QPixmap.fromImage(q_image)
        return None


class VideoFeed(QLabel):
    def __init__(self, width: int, height: int):
        super().__init__()
        self.active = False
        self.video = Video(width, height)

        self.timer = QTimer()
        self.timer.setInterval(33)
        self.timer.timeout.connect(self._update_frame)
        self.setFixedSize(width, height)
        self.setScaledContents(True)

    def _update_frame(self):
        pixmap = self.video.get_frame()
        if pixmap is not None:
            self.setPixmap(pixmap)

    def activate(self):
        self.active = True
        self.timer.start()

    def deactivate(self):
        self.active = False
        self.timer.stop()