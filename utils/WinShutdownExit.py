import win32con
import win32gui
import sys
import os
import traceback
from datetime import datetime

# === Глобальна функція для виходу з програми ===
_global_shutdown_handler = None
def set_global_shutdown_handler(handler):
    global _global_shutdown_handler
    _global_shutdown_handler = handler

def app_exit():
    """Універсальний вихід з програми з логуванням (можна викликати з будь-якого місця)."""
    if _global_shutdown_handler is not None:
        _global_shutdown_handler._safe_exit()
    else:
        # Fallback: аварійний вихід
        print("[app_exit] No shutdown handler set, exiting immediately.")
        sys.exit(0)
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
        if log_path:
            self.log_path = log_path
        else:
            appdata_dir = os.environ.get('APPDATA') or os.path.expanduser('~')
            app_settings_dir = os.path.join(appdata_dir, 'Indic8tr')
            os.makedirs(app_settings_dir, exist_ok=True)
            self.log_path = os.path.join(app_settings_dir, "shutdown.log")

        self._log(f"WinShutdownExit ініціалізовано. Лог: {self.log_path}")

        # --- Tkinter protocol handlers for shutdown/logoff ---
        if self.root is not None:
            try:
                # Handle window close (Alt+F4, X button)
                self.root.protocol("WM_DELETE_WINDOW", self._safe_exit)
                # Handle Windows shutdown/logoff (WM_QUERYENDSESSION)
                import ctypes
                import ctypes.wintypes
                user32 = ctypes.windll.user32
                GWL_WNDPROC = -4
                WM_QUERYENDSESSION = 0x0011
                WM_ENDSESSION = 0x0016
                original_wndproc = None

                def py_wndproc(hwnd, msg, wparam, lparam):
                    if msg == WM_QUERYENDSESSION or msg == WM_ENDSESSION:
                        self._log("Tkinter: Отримано WM_QUERYENDSESSION/WM_ENDSESSION")
                        self._safe_exit()
                        return 0
                    return user32.CallWindowProcW(original_wndproc, hwnd, msg, wparam, lparam)

                # Get the HWND for the Tkinter root window
                hwnd = self.root.winfo_id()
                WNDPROCTYPE = ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_int, ctypes.c_uint, ctypes.c_int, ctypes.c_int)
                py_wndproc_c = WNDPROCTYPE(py_wndproc)
                original_wndproc = user32.GetWindowLongW(hwnd, GWL_WNDPROC)
                user32.SetWindowLongW(hwnd, GWL_WNDPROC, py_wndproc_c)
                self._log("Tkinter: WNDPROC перехоплено для WM_QUERYENDSESSION")
            except Exception as e:
                self._log(f"[WinShutdownExit] Не вдалося встановити WNDPROC: {e}")

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
                self.root = None
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
