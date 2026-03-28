import json
import os
from datetime import timedelta
from os import name

import numpy as np
from PyQt6.QtCore import QTimer
from CameraAI.ai_vision import VisionManager
from keyboard import Recorder


class Gesture:
    def __init__(self, name: str, gesture: np.ndarray, shortcut: list[str]):
        self.name = name
        self.gesture = gesture
        self.shortcut = shortcut

    def nice(self) -> dict:
        return {
            "name" : self.name,
            "gesture" : self.gesture.tolist(),
            "shortcut" : self.shortcut
        }

class GestureMap:
    def __init__(self, keyboard_recorder: Recorder):
        self.current_gesture = None
        self.current_shortcut = None
        self.gestures = []
        self.record_timer = QTimer()
        self.record_timer.timeout.connect(self._ss_gesture)
        self.keyboard_recorder = keyboard_recorder
        self.keyboard_recorder.finished.connect(self._read_recording)

    def save_gestures_to_json(self) -> bool:
        try:
            with open("maps.json", 'w') as f:
                json.dump(self.gestures, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving gestures to json: {e}")
            return False


    def _ss_gesture(self, name: str):
        vision = VisionManager.instance()
        frame = vision.get_frame()
        landmarks = (vision.get_landmarkers(frame))

        return vision.record_gesture(name, landmarks)

    def _read_recording(self, binding: str):
        self.current_shortcut = binding

    def record_gesture(self, delay: timedelta):
        self.record_timer.start(delay.seconds * 1000)

    def add_gesture(self) -> bool:
        if self.current_gesture is None or self.current_shortcut is None:
            return False

        self.gestures.append(Gesture(self.current_gesture, self.current_shortcut))
        return True

    def load_gestures(self):
        try:
            with open("maps.json", 'r') as f:
                data = json.loads(f.read())
                print(data)
        except Exception as e:
            print(f"Error saving gestures to json: {e}")