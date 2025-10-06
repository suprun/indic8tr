import sys
import os
import tkinter as tk
from threading import Thread

from utils import single_instance, resources
from utils.SettingsManager import settings
from utils.WinShutdownExit import WinShutdownExit, set_global_shutdown_handler

from core.LayoutMonitor import LayoutMonitor
from core.TrayIcon import TrayIcon
from core.FlagOverlay import FlagOverlay
from core.KeyboardManager import keyboard

def run_shutdown_listener(handler):
    """Функція для запуску слухача системних повідомлень Windows."""
    handler._message_loop()
# ===== Main =====
def main():
    # Перевірка на єдиний екземпляр  
    instance = single_instance("Global\\KeyboardIndicatorSingletonMutex")
    if instance.already_running:
        # другий екземпляр закривається одразу
        print("Програма вже запущена!")
        sys.exit(0)

    # Перевірка існування необхідних директорій
    if not os.path.exists(resources().TRAY_FLAGS_DIR):
        print(f"УВАГА: Директорія {resources().TRAY_FLAGS_DIR} не знайдена!")
    if not os.path.exists(resources().OVERLAY_FLAGS_DIR):
        print(f"УВАГА: Директорія {resources().OVERLAY_FLAGS_DIR} не знайдена!")

    # Завантажити налаштування (з автоматичною синхронізацією автостарту)
    settings.load()
    
    # Ініціалізація Tkinter
    root = tk.Tk()
    overlay = FlagOverlay(root)
    tray = TrayIcon(overlay)
    tray.monitor = None  # Ensure monitor attribute exists
    root.withdraw()

    # Початкове оновлення іконки
    current_layout = keyboard.get_current_layout_key()
    tray.update_icon(current_layout)
    
    # Запуск моніторингу в окремому потоці
    monitor = LayoutMonitor(overlay, tray)
    tray.monitor = monitor  # Зберегти посилання для cleanup

    # Налаштування обробника завершення програми
    shutdown_handler = WinShutdownExit(
        on_exit_callback=settings.save,
        tray=tray,
        root=root
    )
    set_global_shutdown_handler(shutdown_handler)

    listener_thread = Thread(
        target=run_shutdown_listener, 
        args=(shutdown_handler,),
        daemon=True # Важливо, щоб потік не блокував sys.exit
    )
    listener_thread.start()      

    if keyboard.HOOK_AVAILABLE:
        monitor_thread = Thread(target=monitor.monitor_with_async_key_state, daemon=True)
        print("Використовується GetAsyncKeyState для детекції клавіш")
    else:
        # Fallback якщо ctypes недоступний
        monitor_thread = Thread(target=monitor.monitor_with_polling_only, daemon=True)
        print("Fallback: простий polling без детекції клавіш")
    
    '''if settings.firstrun:
        #def firstrun_notification ():   
        tray.show_notification("NDIC8TR", "Програма запущена успішно!", "info")
        settings.firstrun = False
        settings.save()
        #root.after(1000, firstrun_notification)'''  
    
    monitor_thread.start()
    # Головний цикл
    try:
        root.mainloop()
    except KeyboardInterrupt:
        tray.quit_app(None, None)
    
"""import atexit
def on_exit():
    settings.save()

atexit.register(on_exit)"""

if __name__ == "__main__":
    main()