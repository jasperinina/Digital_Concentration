"""Главное окно приложения и значок в области уведомлений."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QCloseEvent
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QMenu,
    QStyle,
    QSystemTrayIcon,
    QTabWidget,
    QWidget,
)
from sqlalchemy.orm import sessionmaker

APP_TITLE = "NormDev — учет времени и концентрация"


def placeholder(text: str) -> QWidget:
    label = QLabel(text)
    label.setAlignment(Qt.AlignCenter)
    label.setStyleSheet("color: palette(placeholder-text)")
    return label


class MainWindow(QMainWindow):
    def __init__(self, session_factory: sessionmaker) -> None:
        super().__init__()
        self.session_factory = session_factory
        self.setWindowTitle(APP_TITLE)
        self.resize(1000, 640)

        self.tabs = QTabWidget()
        self.tabs.addTab(placeholder("Подсистема учета времени — в разработке"), "Учет времени")
        self.tabs.addTab(self._build_focus_tab(), "Концентрация")
        self.tabs.setCurrentIndex(1)
        self.setCentralWidget(self.tabs)

        self.focus_status = QLabel("Концентрация не активна")
        self.statusBar().addPermanentWidget(self.focus_status)

        self.tray = self._build_tray()

    def _build_focus_tab(self) -> QWidget:
        self.focus_tabs = QTabWidget()
        self.focus_tabs.addTab(placeholder("Профили концентрации"), "Профили")
        self.focus_tabs.addTab(placeholder("Нет активной сессии"), "Активная сессия")
        self.focus_tabs.addTab(placeholder("История сессий"), "История")
        return self.focus_tabs

    def _build_tray(self) -> QSystemTrayIcon:
        icon = self.style().standardIcon(QStyle.SP_ComputerIcon)
        self.setWindowIcon(icon)
        tray = QSystemTrayIcon(icon, self)
        tray.setToolTip(APP_TITLE)

        menu = QMenu(self)
        open_action = QAction("Открыть", self)
        open_action.triggered.connect(self.show_and_raise)
        quit_action = QAction("Выход", self)
        quit_action.triggered.connect(QApplication.quit)
        menu.addAction(open_action)
        menu.addSeparator()
        menu.addAction(quit_action)
        tray.setContextMenu(menu)
        tray.activated.connect(self._on_tray_activated)
        tray.show()
        return tray

    def _on_tray_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason in (QSystemTrayIcon.Trigger, QSystemTrayIcon.DoubleClick):
            self.show_and_raise()

    def show_and_raise(self) -> None:
        self.showNormal()
        self.raise_()
        self.activateWindow()

    def notify(self, title: str, message: str) -> None:
        self.tray.showMessage(title, message, QSystemTrayIcon.Information, 5000)

    def closeEvent(self, event: QCloseEvent) -> None:
        self.tray.hide()
        super().closeEvent(event)
