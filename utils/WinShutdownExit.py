import win32con
import win32gui
import sys
import os
import threading
import traceback
from datetime import datetime


class WinShutdownExit:
    """
    Відслідковує завершення роботи Windows, вихід користувача або перезапуск.
    Зберігає налаштування, завершує tray і Tkinter.
    Веде лог у файл shutdown.log.
    """

    def __init__(self, on_exit_callback=None, tray=None, root=None, log_path=None):
        """
        :param on_exit_callback: функція для збереження (наприклад, settings.save)
        :param tray: об'єкт TrayIcon
        :param root: головне Tkinter-вікно
        :param log_path: шлях до лог-файлу (якщо None — створюється поруч із main.py)
        """
        self.on_exit_callback = on_exit_callback
        self.tray = tray
        self.root = root
        self.log_path = log_path or os.path.join(os.path.dirname(sys.argv[0]), "shutdown.log")

        self._log(f"WinShutdownExit ініціалізовано. Лог: {self.log_path}")
        self.thread = threading.Thread(target=self._message_loop, daemon=True)
        self.thread.start()

    # ========== Основна логіка ==========
    def _message_loop(self):
        """Створює приховане вікно для прийому системних повідомлень."""
        try:
            wc = win32gui.WNDCLASS()
            wc.lpfnWndProc = self._wnd_proc
            wc.lpszClassName = "WinShutdownListener"
            class_atom = win32gui.RegisterClass(wc)

            hwnd = win32gui.CreateWindowEx(
                0,
                class_atom,
                "HiddenShutdownListener",
                0,
                0, 0, 0, 0,
                0, 0, 0, None
            )

            self._log("Слухач системних подій створено.")
            win32gui.PumpMessages()
        except Exception:
            self._log("ПОМИЛКА у _message_loop():\n" + traceback.format_exc())

    def _wnd_proc(self, hwnd, msg, wparam, lparam):
        """Обробник системних повідомлень Windows."""
        if msg in (win32con.WM_QUERYENDSESSION, win32con.WM_ENDSESSION):
            if msg == win32con.WM_ENDSESSION and wparam == 1:
                self._log("Отримано WM_ENDSESSION — завершення Windows.")
                self._safe_exit()
            return True

        elif msg == win32con.WM_CLOSE:
            self._log("Отримано WM_CLOSE — завершення користувачем.")
            self._safe_exit()
            return 0

        elif msg == win32con.WM_DESTROY:
            self._log("Отримано WM_DESTROY.")
            win32gui.PostQuitMessage(0)
            return 0

        return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)

    # ========== Безпечне завершення ==========
    def _safe_exit(self):
        """Безпечне завершення програми."""
        self._log("Розпочато безпечне завершення програми.")

        try:
            if callable(self.on_exit_callback):
                self._log("→ Виклик on_exit_callback()")
                self.on_exit_callback()
        except Exception:
            self._log("ПОМИЛКА у on_exit_callback():\n" + traceback.format_exc())

        try:
            if self.tray:
                self._log("→ Завершення tray")
                self.tray.quit_app(None, None)
        except Exception:
            self._log("ПОМИЛКА у tray.quit_app():\n" + traceback.format_exc())

        try:
            if self.root:
                self._log("→ Закриття Tkinter")
                self.root.quit()
                self.root.destroy()
        except Exception:
            self._log("ПОМИЛКА у root.destroy():\n" + traceback.format_exc())

        self._log("✅ Програма завершена через системний сигнал.\n")
        sys.exit(0)

    # ========== Логування ==========
    def _log(self, message):
        """Запис повідомлення у лог-файл."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        text = f"[{timestamp}] {message}\n"
        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(text)
        except Exception:
            print("[WinShutdownExit] Помилка запису логу:", message)
