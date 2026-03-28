import sys
from PyQt6.QtWidgets import QWidget, QMainWindow, QPushButton, QLabel, QGridLayout, QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtMultimedia import QCamera, QMediaCaptureSession, QMediaDevices
from PyQt6.QtMultimediaWidgets import QVideoWidget


class Main_Window(QMainWindow):
  def __init__(self):
    super().__init__()
    self.setWindowTitle("Main window")
    central = QWidget()
    self.setCentralWidget(central)
    layout = QGridLayout(central)
    self.video_feed = QVideoWidget()
    self.video_feed.setFixedSize(800,500)
    layout.addWidget(self.video_feed, 0, 1)
    layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
    self.start = QPushButton("Start feed")
    self.start.setFixedSize(100,100)
    layout.addWidget(self.start, 1, 1)
    self.camera = None
    self.session = QMediaCaptureSession()

    self.start.clicked.connect(self.start_video)

  def start_video(self):
    device = QMediaDevices.defaultVideoInput()
    self.camera = QCamera(device)
    self.session.setCamera(self.camera)
    self.session.setVideoOutput(self.video_feed)
    self.camera.start()

app = QApplication(sys.argv)
window = Main_Window()
window.show()
app.exec()



