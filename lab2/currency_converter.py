import sys
from enum import Enum, auto
from pathlib import Path

from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QVBoxLayout,
    QWidget,
)

DOLLAR_TO_RUBLE = 90.0
DOLLAR_TO_EURO = 0.92
MAX_INPUT_VALUE = 10_000_000.0
DECIMAL_PLACES = 2
EMPTY_FIELD_HINT = "0.00"
APP_TITLE = "Лаб 2 | Конвертер валют"


def _parse_user_number(text: str) -> float:
    candidate = text.replace(",", ".")
    try:
        return float(candidate)
    except ValueError:
        return 0.0


def _format_amount(number: float) -> str:
    return f"{number:.{DECIMAL_PLACES}f}"


class _EditedField(Enum):
    DOLLAR = auto()
    RUBLE = auto()
    EURO = auto()


class FxTripleInputView(QWidget):
    """Связанные поля USD / RUB / EUR с пересчётом через доллар."""

    def __init__(self) -> None:
        super().__init__()
        self._dollar_input = QLineEdit()
        self._ruble_input = QLineEdit()
        self._euro_input = QLineEdit()
        self._inputs_by_kind: dict[_EditedField, QLineEdit] = {
            _EditedField.DOLLAR: self._dollar_input,
            _EditedField.RUBLE: self._ruble_input,
            _EditedField.EURO: self._euro_input,
        }
        self._compose_form()
        self._attach_listeners()
        self._prepare_window()

    def _prepare_window(self) -> None:
        self.setWindowTitle(APP_TITLE)
        self.setGeometry(100, 100, 350, 200)

    def _numeric_rule(self) -> QDoubleValidator:
        validator = QDoubleValidator(0.0, MAX_INPUT_VALUE, DECIMAL_PLACES)
        validator.setNotation(QDoubleValidator.Notation.StandardNotation)
        return validator

    def _labeled_input(self, title: str, editor: QLineEdit, validator: QDoubleValidator) -> QHBoxLayout:
        editor.setValidator(validator)
        editor.setPlaceholderText(EMPTY_FIELD_HINT)
        strip = QHBoxLayout()
        strip.addWidget(QLabel(title))
        strip.addWidget(editor)
        return strip

    def _compose_form(self) -> None:
        rule = self._numeric_rule()
        column = QVBoxLayout()
        column.addLayout(self._labeled_input("USD:", self._dollar_input, rule))
        column.addLayout(self._labeled_input("RUB:", self._ruble_input, rule))
        column.addLayout(self._labeled_input("EUR (€):", self._euro_input, rule))
        self.setLayout(column)

    def _attach_listeners(self) -> None:
        self._dollar_input.textChanged.connect(
            lambda value: self._recalculate_from(_EditedField.DOLLAR, value)
        )
        self._ruble_input.textChanged.connect(
            lambda value: self._recalculate_from(_EditedField.RUBLE, value)
        )
        self._euro_input.textChanged.connect(
            lambda value: self._recalculate_from(_EditedField.EURO, value)
        )

    @staticmethod
    def _triple_from_dollar(usd: float) -> tuple[float, float, float]:
        rub = usd * DOLLAR_TO_RUBLE
        eur = usd * DOLLAR_TO_EURO
        return usd, rub, eur

    def _triple_for_source(self, kind: _EditedField, typed: float) -> tuple[float, float, float]:
        if kind is _EditedField.DOLLAR:
            return self._triple_from_dollar(typed)
        if kind is _EditedField.RUBLE:
            usd = typed / DOLLAR_TO_RUBLE
            return self._triple_from_dollar(usd)
        eur = typed
        usd = eur / DOLLAR_TO_EURO
        return self._triple_from_dollar(usd)

    def _write_silent(self, pairs: dict[QLineEdit, str]) -> None:
        for widget, content in pairs.items():
            widget.blockSignals(True)
            widget.setText(content)
            widget.blockSignals(False)

    def _wipe_siblings(self, keep: QLineEdit) -> None:
        for widget in self._inputs_by_kind.values():
            if widget is keep:
                continue
            widget.blockSignals(True)
            widget.clear()
            widget.blockSignals(False)

    def _recalculate_from(self, kind: _EditedField, raw: str) -> None:
        active = self._inputs_by_kind[kind]
        if not raw:
            self._wipe_siblings(active)
            return

        usd, rub, eur = self._triple_for_source(kind, _parse_user_number(raw))
        formatted = {
            self._dollar_input: _format_amount(usd),
            self._ruble_input: _format_amount(rub),
            self._euro_input: _format_amount(eur),
        }
        del formatted[active]
        self._write_silent(formatted)


def launch() -> int:
    project_root = Path(__file__).resolve().parent.parent
    root_str = str(project_root)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)
    import lab2  # noqa: F401 — QT_QPA_PLATFORM_PLUGIN_PATH

    app = QApplication(sys.argv)
    view = FxTripleInputView()
    view.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(launch())
