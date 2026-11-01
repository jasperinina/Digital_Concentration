import sys

from PySide6.QtWidgets import QApplication, QLabel, QMainWindow, QTabWidget


def main() -> int:
    app = QApplication(sys.argv)

    window = QMainWindow()
    window.setWindowTitle("NormDev — учет времени и концентрация")
    tabs = QTabWidget()
    tabs.addTab(QLabel("Подсистема учета времени (Закусилов Д.)"), "Учет времени")
    tabs.addTab(QLabel("Подсистема цифровой концентрации (Григорьева А.)"), "Концентрация")
    window.setCentralWidget(tabs)
    window.resize(900, 600)
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
