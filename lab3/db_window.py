import sys
from pathlib import Path

from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlQueryModel
from PyQt5.QtWidgets import (
    QAction,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from lab3.db_helper import SqliteSampleFactory

_TAB_COUNT = 5
_WINDOW_TITLE = "Лабораторная работа № 3"

_SQL_MASTER_ALL = "SELECT * FROM sqlite_master"
_SQL_MASTER_BRIEF = "SELECT type, name, tbl_name FROM sqlite_master"
_SQL_TABLES_DDL = "SELECT type, name, sql FROM sqlite_master WHERE type='table'"
_SQL_EXTRA_OBJECTS = (
    "SELECT type, name, sql FROM sqlite_master WHERE type IN ('index', 'trigger', 'view')"
)
_SQL_TABLE_NAMES = "SELECT name FROM sqlite_master WHERE type='table';"


class SqliteBrowserMainWindow(QMainWindow):
    """Главное окно: подключение к SQLite и вывод запросов по вкладкам."""

    def __init__(self) -> None:
        super().__init__()
        SqliteSampleFactory.ensure_fresh_database()

        self._connection: QSqlDatabase | None = None
        self._db_open = False

        self.setWindowTitle(_WINDOW_TITLE)
        self.setGeometry(100, 100, 900, 600)

        self._grid_views: list[QTableView] = []
        self._table_picker = QComboBox()
        self._open_names_btn = QPushButton("bt1 (Имена таблиц)")
        self._schema_btn = QPushButton("bt2 (Запрос Tab4)")
        self._extras_btn = QPushButton("bt3 (Запрос Tab5)")
        self._sheet_tabs = QTabWidget()

        self._build_menu()
        self._build_central()
        self._toggle_interactive(False)

    def _build_menu(self) -> None:
        bar = self.menuBar()
        connection_menu = bar.addMenu("Соединение")

        connect_act = QAction("Set connection", self)
        connect_act.triggered.connect(self._pick_and_connect)
        connection_menu.addAction(connect_act)

        disconnect_act = QAction("Close connection", self)
        disconnect_act.triggered.connect(self._disconnect_and_reset)
        connection_menu.addAction(disconnect_act)

    def _build_central(self) -> None:
        host = QWidget()
        self.setCentralWidget(host)
        root = QVBoxLayout(host)

        toolbar = QHBoxLayout()
        self._open_names_btn.clicked.connect(self._show_master_brief)
        toolbar.addWidget(self._open_names_btn)

        toolbar.addWidget(QLabel("Выбор таблицы:"))
        self._table_picker.currentIndexChanged.connect(self._on_table_selected)
        toolbar.addWidget(self._table_picker)

        self._schema_btn.clicked.connect(self._show_table_definitions)
        toolbar.addWidget(self._schema_btn)

        self._extras_btn.clicked.connect(self._show_indexes_and_views)
        toolbar.addWidget(self._extras_btn)

        root.addLayout(toolbar)

        for index in range(1, _TAB_COUNT + 1):
            page = QWidget()
            page_layout = QVBoxLayout(page)
            grid = QTableView()
            page_layout.addWidget(grid)
            self._sheet_tabs.addTab(page, f"Tab {index}")
            self._grid_views.append(grid)

        root.addWidget(self._sheet_tabs)

    def _toggle_interactive(self, enabled: bool) -> None:
        self._open_names_btn.setEnabled(enabled)
        self._schema_btn.setEnabled(enabled)
        self._extras_btn.setEnabled(enabled)
        self._table_picker.setEnabled(enabled)

    def _run_sql_on_tab(self, statement: str, tab_idx: int) -> None:
        if not self._db_open or self._connection is None:
            return

        model = QSqlQueryModel()
        model.setQuery(statement, self._connection)

        if model.lastError().isValid():
            QMessageBox.warning(
                self,
                "Ошибка БД",
                f"Ошибка выполнения запроса:\n{model.lastError().text()}",
            )
            return

        view = self._grid_views[tab_idx]
        view.setModel(model)
        view.resizeColumnsToContents()

    def _pick_and_connect(self) -> None:
        db_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите файл базы данных SQLite",
            "",
            "SQLite Databases (*.db *.sqlite *.sqlite3);;All Files (*)",
        )
        if not db_path:
            return

        if self._db_open:
            self._disconnect_and_reset()

        self._connection = QSqlDatabase.addDatabase("QSQLITE")
        self._connection.setDatabaseName(db_path)

        if not self._connection.open():
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось подключиться к базе данных!\n{self._connection.lastError().text()}",
            )
            return

        self._db_open = True
        self._toggle_interactive(True)

        self._run_sql_on_tab(_SQL_MASTER_ALL, 0)
        self._refresh_table_picker()

        QMessageBox.information(self, "Успех", "Соединение с БД успешно установлено!")

    def _refresh_table_picker(self) -> None:
        self._table_picker.blockSignals(True)
        self._table_picker.clear()

        if self._connection is None:
            self._table_picker.blockSignals(False)
            return

        names_query = QSqlQuery(_SQL_TABLE_NAMES, self._connection)
        while names_query.next():
            self._table_picker.addItem(names_query.value(0))

        self._table_picker.blockSignals(False)

        if self._table_picker.count() > 0:
            self._on_table_selected(0)

    def _disconnect_and_reset(self) -> None:
        for view in self._grid_views:
            view.setModel(None)

        self._table_picker.blockSignals(True)
        self._table_picker.clear()
        self._table_picker.blockSignals(False)

        if self._db_open and self._connection is not None:
            link_name = self._connection.connectionName()
            self._connection.close()
            self._connection = None
            QSqlDatabase.removeDatabase(link_name)
            self._db_open = False

        self._toggle_interactive(False)
        QMessageBox.information(self, "Соединение", "Соединение с БД закрыто, интерфейс очищен.")

    def _show_master_brief(self) -> None:
        self._run_sql_on_tab(_SQL_MASTER_BRIEF, 1)
        self._sheet_tabs.setCurrentIndex(1)

    def _on_table_selected(self, _index: int) -> None:
        chosen = self._table_picker.currentText()
        if chosen:
            self._run_sql_on_tab(f'SELECT * FROM "{chosen}"', 2)

    def _show_table_definitions(self) -> None:
        self._run_sql_on_tab(_SQL_TABLES_DDL, 3)
        self._sheet_tabs.setCurrentIndex(3)

    def _show_indexes_and_views(self) -> None:
        self._run_sql_on_tab(_SQL_EXTRA_OBJECTS, 4)
        self._sheet_tabs.setCurrentIndex(4)


def launch() -> int:
    project_root = Path(__file__).resolve().parent.parent
    root_str = str(project_root)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)
    import lab3  # noqa: F401 — пути к плагинам Qt / SQL

    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    frame = SqliteBrowserMainWindow()
    frame.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(launch())