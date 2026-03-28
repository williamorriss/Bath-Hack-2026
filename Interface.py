import threading
from queue import Queue

import cv2
from PyQt6.QtGui import QPainter, QImage
from PyQt6.QtWidgets import QWidget, QMainWindow, QPushButton, QLabel, QGridLayout, QApplication
from PyQt6.QtCore import Qt, QPoint, QTimer
from PyQt6.QtMultimedia import QCamera, QMediaCaptureSession, QMediaDevices
from PyQt6.QtMultimediaWidgets import QVideoWidget
from keyboard import Recorder
from datetime import timedelta
from CameraAI.ai_vision import VisionManager

from app import App


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main window")
        central = QWidget()

        self.setCentralWidget(central)
        layout = QGridLayout(central)

        # video
        self.camera = None
        self.video_feed = ImageWidget()
        self.video_feed.setFixedSize(800,500)
        layout.addWidget(self.video_feed, 0, 1)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        # start feed
        self.start = QPushButton("Start feed")
        self.start.setFixedSize(100,100)
        layout.addWidget(self.start, 1, 1)
        self.session = QMediaCaptureSession()
        self.start.clicked.connect(self.start_video)

        # bindings
        self.recorder = Recorder(duration=timedelta(seconds=5))
        layout.addWidget(self.recorder, 2, 1)

        # camera
        self.vision = VisionManager()


    def start_video(self):
        self.timer = QTimer(self)


        self.timer.timeout.connect(self.set_image())
        self.timer.start(10)
        self.capture_thread = threading.Thread(target=grab_images)
        self.capture_thread.start()

    def set_image(self):
        self.video_feed.setImage(self.vision.get_frame())


    def cam(self, permission: Qt.PermissionStatus):
        if permission != Qt.PermissionStatus.Granted:
            print("Access denied")
            return

        device = QMediaDevices.defaultVideoInput()

        if device.isNull():
            print("No camera device detected.")
            return

        self.camera = QCamera(device)
        self.session.setCamera(self.camera)
        self.session.setVideoOutput(self.video_feed)
        self.camera.start()

class Video(QImage):
    def __init__(self, vision: VisionManager):
        super().__init__()
        self.vision = vision
        self.buffer = Queue()

    def get_frames(self):
        self.buffer.put(self.vision.get_frame())

    def set_frame(self, image):
        self.image = image
        self.setMinimumSize(image.size())
        self.update()