import os
from pathlib import Path

from PyQt5.QtCore import QObject, QMetaObject, QTimer, Q_ARG, pyqtSlot, QVariant
from PyQt5.QtQml import QQmlApplicationEngine

_AUTOSAVE_MS = 5000
_SNAPSHOT_FILE = Path(__file__).resolve().parent / "saved_canvas.png"


class CanvasAutosaveBridge(QObject):
    """Связка Python ↔ QML: периодически сохраняет холст на диск."""

    def __init__(self, engine: QQmlApplicationEngine) -> None:
        super().__init__()
        self._engine = engine

        self._interval_timer = QTimer(self)
        self._interval_timer.setInterval(_AUTOSAVE_MS)
        self._interval_timer.timeout.connect(self._flush_canvas_to_file)
        self._interval_timer.start()

    @pyqtSlot()
    def _flush_canvas_to_file(self) -> None:
        roots = self._engine.rootObjects()
        if not roots:
            print("Ошибка: Не удалось получить корневой объект QML!")
            return

        surface = roots[0].findChild(QObject, "canvas")
        if surface is None:
            print("Ошибка: Не удалось найти объект canvas в QML!")
            return

        target = str(_SNAPSHOT_FILE)
        QMetaObject.invokeMethod(
            surface,
            "saveCanvas",
            Q_ARG(QVariant, target),
        )
        print(f"[Backend] автосохранение выполнено: {target}")

    def drop_qt_env_overrides(self) -> None:
        os.environ.pop("QML2_IMPORT_PATH", None)
        os.environ.pop("QT_PLUGIN_PATH", None)
        print("[System] Переменные окружения успешно очищены!")