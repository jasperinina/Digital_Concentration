from app.core.main_window import MainWindow


def test_main_window_has_subsystem_tabs(qtbot, session_factory):
    window = MainWindow(session_factory)
    qtbot.addWidget(window)

    tabs = [window.tabs.tabText(i) for i in range(window.tabs.count())]
    focus_tabs = [window.focus_tabs.tabText(i) for i in range(window.focus_tabs.count())]
    assert tabs == ["Учет времени", "Концентрация"]
    assert focus_tabs == ["Профили", "Активная сессия", "История"]
    assert window.focus_status.text() == "Концентрация не активна"
