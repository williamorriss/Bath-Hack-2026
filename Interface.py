from PyQt6.QtWidgets import QWidget, QMainWindow, QPushButton, QGridLayout
from PyQt6.QtCore import Qt
from PyQt6.QtMultimedia import QMediaCaptureSession
from keyboard import Recorder
from datetime import timedelta

from video import VideoFeed


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