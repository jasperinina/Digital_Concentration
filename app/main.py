import sys

from PySide6.QtWidgets import QApplication, QMessageBox

from app.core.db import default_db_path, init_db
from app.core.main_window import APP_TITLE, MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("NormDev")

    try:
        session_factory = init_db()
    except Exception as exc:  # без БД приложение работать не может
        QMessageBox.critical(
            None, APP_TITLE, f"Не удалось открыть базу данных:\n{default_db_path()}\n\n{exc}"
        )
        return 1

    window = MainWindow(session_factory)
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
