import sys
from pathlib import Path

from PyQt5.QtCore import QUrl
from PyQt5.QtQml import QQmlApplicationEngine
from PyQt5.QtWidgets import QApplication

from lab4.autosave_bridge import CanvasAutosaveBridge

_QML_ROOT = Path(__file__).resolve().parent / "qml_views" / "PaintRoot.qml"


def launch() -> int:
    project_root = Path(__file__).resolve().parent.parent
    root_str = str(project_root)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)
    import lab4  # noqa: F401 — пути к QML и плагинам Qt

    app = QApplication(sys.argv)
    qml_engine = QQmlApplicationEngine()
    bridge = CanvasAutosaveBridge(qml_engine)
    qml_engine.rootContext().setContextProperty("_backend", bridge)

    qml_engine.load(QUrl.fromLocalFile(str(_QML_ROOT)))
    if not qml_engine.rootObjects():
        print("Ошибка: Не удалось загрузить QML!")
        return -1

    app.aboutToQuit.connect(bridge.drop_qt_env_overrides)
    return app.exec()


if __name__ == "__main__":
    sys.exit(launch())