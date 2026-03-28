from gesture import GestureMap
from CameraAI.ai_vision import VisionManager

from pynput.keyboard import Controller, Key

class ShortcutPlayer:
    def __init__(self, gesture_map: GestureMap):
        self.keyboard = Controller()
        self.gesture_map = gesture_map

    def regonise_play_shortcut(self):
        vision_manager = VisionManager.instance()

        frame = vision_manager.get_frame()
        landmarkers = vision_manager.get_landmarkers(frame)
        name, confidence = vision_manager.recognise_gesture(self.gesture_map.gestures, landmarkers.hand_landmarks)

        gesture, shortcut = self.gesture_map.get_gesture(name)

        self._play_shortcut(shortcut)

    def _play_shortcut(self, shortcut: list[str]):
        for k in shortcut:
            if len(k) == 1:
                self.keyboard.press(k)
                self.keyboard.release(k)
            else:
                special = getattr(Key, k, None)
                if special:
                    self.keyboard.press(special)
                    self.keyboard.release(special)