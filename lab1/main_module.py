import sys
from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QWidget

_PREVIEW_SIZE = 300
_START_MESSAGE = "Здесь будет изображение!"
_BUTTON_CAPTION = "Показать картинку"
_WINDOW_TITLE = "Лаб 1 | Замена надписи на изображение"


def _asset_path(filename: str) -> Path:
    return Path(__file__).resolve().parent / filename


class LabelImageSwitcher(QWidget):
    """Окно с текстовой меткой и кнопкой показа изображения."""

    def __init__(self) -> None:
        super().__init__()
        self._picture_file = _asset_path("gorilla.png")
        self._caption = QLabel(_START_MESSAGE)
        self._action = QPushButton(_BUTTON_CAPTION)
        self._build_layout()
        self._bind_handlers()
        self._apply_window_settings()

    def _apply_window_settings(self) -> None:
        self.setWindowTitle(_WINDOW_TITLE)
        self.setGeometry(100, 100, 400, 400)

    def _build_layout(self) -> None:
        self._caption.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root = QVBoxLayout()
        root.addWidget(self._caption)
        root.addWidget(self._action)
        self.setLayout(root)

    def _bind_handlers(self) -> None:
        self._action.clicked.connect(self._display_image_in_label)

    def _display_image_in_label(self) -> None:
        if not self._picture_file.is_file():
            self._caption.setText(f"Ошибка: файл {self._picture_file} не найден")
            return

        source = QPixmap(str(self._picture_file))
        fitted = source.scaled(
            _PREVIEW_SIZE,
            _PREVIEW_SIZE,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self._caption.setPixmap(fitted)


def run_application() -> int:
    project_root = Path(__file__).resolve().parent.parent
    root_str = str(project_root)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)
    import lab1  # noqa: F401 — QT_QPA_PLATFORM_PLUGIN_PATH

    app = QApplication(sys.argv)
    window = LabelImageSwitcher()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(run_application())
