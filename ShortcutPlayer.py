from time import sleep


from components.bindings import BindingManager
from CameraAI.ai_vision import VisionManager, Frame
from pynput.keyboard import Controller, Key
from PyQt6.QtCore import QThread

class ShortcutWorker(QThread):
    def __init__(self, binding_manager: BindingManager):
        super().__init__()
        self.vision_manager = VisionManager.instance()
        self.vision_manager.frame_ready.connect(self._frame)
        self.binding_manager = binding_manager
        self.keyboard = Controller()

    def _frame(self, frame: Frame):
        landmarkers = self.vision_manager.get_landmarkers(frame)
        if landmarkers is None:
            return

        name, confidence = self.vision_manager.recognise_gesture(self.binding_manager.bindings, landmarkers.hand_landmarks)

        if not self.binding_manager.bindings or name is None:
            return

        binding = self.binding_manager.bindings[name]
        self._process(binding.shortcut)

        print(f"Name: {name}, Confidence: {confidence}")

    def _process(self, shortcut: list[str]):
        for k in shortcut:
            if len(k) == 1:
                self.keyboard.tap(k)
            else:
                special = getattr(Key, k, None)
                if special:
                    self.keyboard.tap(special)