"""События, которыми обмениваются подсистемы учета времени и концентрации.

Подсистемы не импортируют друг друга напрямую: учет времени испускает сигналы,
концентрация на них подписывается (см. соглашение о взаимодействии подсистем).
"""

from PySide6.QtCore import QObject, Signal


class TimerEvents(QObject):
    task_started = Signal(int)  # task_id — запуск таймера по задаче
    timer_paused = Signal(int)  # task_id
    timer_resumed = Signal(int)  # task_id
    timer_stopped = Signal(int)  # task_id
    task_switched = Signal(int, int)  # старая task_id, новая task_id
    idle_detected = Signal(int)  # длительность бездействия, с


timer_events = TimerEvents()
