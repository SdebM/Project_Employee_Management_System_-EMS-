from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

class BackgroundWorker(QObject):
    """Универсальный класс для выполнения задач в фоновом потоке."""
    
    # Сигнал отправляется при успешном завершении (передает результат функции)
    finished = pyqtSignal(object)
    # Сигнал отправляется при ошибке (передает строку с текстом ошибки)
    error = pyqtSignal(str)

    def __init__(self, task, *args, **kwargs):
        """
        Args:
            task: Функция, которую нужно выполнить в фоне
            *args, **kwargs: Аргументы для этой функции
        """
        super().__init__()
        self.task = task
        self.args = args
        self.kwargs = kwargs

    @pyqtSlot()
    def run(self):
        """Выполняет задачу и эмитит сигналы."""
        try:
            result = self.task(*self.args, **self.kwargs)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))