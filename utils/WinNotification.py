from plyer import notification
import threading

class WinNotifier:
    """
    Клас для системних toast-повідомлень Windows без створення іконки в треї.
    Працює через plyer, не потребує AppID.
    """

    def __init__(self, app_name="NDIC8TR"):
        self.app_name = app_name
        # Налаштування типів сповіщень
        self.config = {
            "info":    {"title": "Інформація", "timeout": 5},
            "warning": {"title": "Попередження", "timeout": 6},
            "error":   {"title": "Помилка", "timeout": 8},
            "success": {"title": "Готово", "timeout": 4},
        }

    def send(self, type_: str, message: str, title: str = "None", timeout: int = 25):
        """
        Відправити toast-повідомлення.
        type_ : str — 'info', 'warning', 'error', 'success'
        message : str — текст повідомлення
        title : str — заголовок (якщо None, береться з конфігурації)
        timeout : int — час показу у секундах
        """
        if type_ not in self.config:
            type_ = "info"
        cfg = self.config[type_]
        title = title or cfg["title"]
        timeout = timeout or cfg["timeout"]

        # Запуск у окремому потоці, щоб не блокувати головний код
        threading.Thread(
            target=self._show_notification,
            args=(title, message, timeout),
            daemon=True
        ).start()

    def _show_notification(self, title, message, timeout):
        try:
            notification.notify(
                title=f"{self.app_name} — {title}",
                message=message,
                timeout=timeout
                # app_icon не вказуємо → трей не створюється
            )
        except Exception as e:
            print(f"[Notifier Error] {e}")
