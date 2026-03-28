from pynput.keyboard import Key
from pynput.keyboard import Controller as KeyboardController
from datetime import timedelta
from PyQt6.QtCore import QEvent
from PyQt6.QtWidgets import QPushButton

keyboard_controller = KeyboardController()

def start():    keyboard_controller.tap(Key.media_play_pause)
def stop():     keyboard_controller.tap(Key.media_play_stop)
def skip():     keyboard_controller.tap(Key.media_next)
def previous(): keyboard_controller.tap(Key.media_previous)