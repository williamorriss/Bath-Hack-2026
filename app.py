import sys
from typing import Callable



from PyQt6.QtCore import QCameraPermission, Qt
from PyQt6.QtWidgets import QApplication

if sys.platform == "darwin":
    import objc
    NSBundle = objc.lookUpClass("NSBundle") # type: ignore
    bundle = NSBundle.mainBundle()
    info = bundle.localizedInfoDictionary() or bundle.infoDictionary()
    info["NSCameraUsageDescription"] = "Camera access is required."

class App(QApplication):
    def __init__(self, argv: list[str]):
        super().__init__(argv)
        from Interface import MainWindow
        self.window = MainWindow()
        self.window.show()

    @classmethod
    def instance(cls) -> "App":
        return super().instance()  # type: ignore

    def get_camera_permission(self):
        permission = QCameraPermission()
        status = self.checkPermission(permission)
        if status != Qt.PermissionStatus.Granted:
            self.requestPermission(permission, self.on_permission_result)

    def on_permission_result(self, permission: QCameraPermission, callback: Callable):
        status = self.checkPermission(permission)
        if status != Qt.PermissionStatus.Granted:
            self.get_camera_permission()

if __name__ == "__main__":
    print("running")
    app = App(sys.argv)
    app.exec()