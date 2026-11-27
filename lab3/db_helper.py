import sqlite3
from pathlib import Path

_DEFAULT_DB = Path(__file__).resolve().parent / "test_db_lab3.db"

_USER_ROWS = (
    ("Иван Иванов", "ivan@example.com", "admin"),
    ("Анна Смирнова", "anna@example.com", "user"),
    ("Петр Петров", "petr@example.com", "user"),
    ("Елена Сидорова", "elena@example.com", "manager"),
)

_PRODUCT_ROWS = (
    ("Ноутбук", 75000.00, 10),
    ("Смартфон", 45000.50, 25),
    ("Беспроводные наушники", 8900.00, 50),
    ("Клавиатура", 3500.00, 15),
)

_ORDER_ROWS = (
    (1, 1, 1),
    (2, 2, 2),
    (3, 3, 1),
    (2, 4, 1),
)


class SqliteSampleFactory:
    """Создаёт учебную SQLite-БД с тремя связанными таблицами."""

    @staticmethod
    def ensure_fresh_database(target: Path | str = _DEFAULT_DB) -> Path:
        db_file = Path(target)
        if db_file.is_file():
            db_file.unlink()
            print(f"Старый файл {db_file} удален.")

        with sqlite3.connect(db_file) as conn:
            cur = conn.cursor()

            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    role TEXT DEFAULT 'user'
                )
                """
            )
            cur.executemany(
                "INSERT INTO users (name, email, role) VALUES (?, ?, ?)",
                _USER_ROWS,
            )

            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    price REAL NOT NULL,
                    stock INTEGER DEFAULT 0
                )
                """
            )
            cur.executemany(
                "INSERT INTO products (title, price, stock) VALUES (?, ?, ?)",
                _PRODUCT_ROWS,
            )

            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    product_id INTEGER,
                    quantity INTEGER NOT NULL,
                    order_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (product_id) REFERENCES products (id)
                )
                """
            )
            cur.executemany(
                "INSERT INTO orders (user_id, product_id, quantity) VALUES (?, ?, ?)",
                _ORDER_ROWS,
            )

            conn.commit()

        print(f"База данных '{db_file}' успешно создана и заполнена тестовыми данными!")
        return db_file