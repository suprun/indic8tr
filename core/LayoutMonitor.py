import time
import win32gui
from ctypes import windll
from utils.ResourceManager import ResourceManager as resources
from utils.SettingsManager import settings
from core.Errors import Errors as errors
from core.lcid import LCID
from core.KeyboardManager import keyboard
class LayoutMonitor:
    def __init__(self, overlay, tray):
        self.overlay = overlay
        self.tray = tray
        self.last_layout = keyboard.get_current_layout_key()
        self.last_change_time = 0

    def monitor_with_async_key_state(self):
        """Основний моніторинг з використанням GetAsyncKeyState"""
        print("Використовується GetAsyncKeyState моніторинг")
        layout_change_history = []
        last_active_window = None
        
        while True:
            try:
                current_layout = keyboard.get_current_layout_key()
                current_time = time.time()
                current_window = win32gui.GetForegroundWindow()
                # Перевіряємо стан модифікаторів
                modifiers_pressed = keyboard.check_modifier_keys_pressed()
            except Exception as e:
                print(f"Monitor error: {e}")
                current_layout = self.last_layout
                current_time = time.time()
                current_window = None
                modifiers_pressed = False
            try:
                if current_layout != self.last_layout:
                    self.tray.update_icon(current_layout)
                    window_changed = (current_window != last_active_window)
                    layout_change_history.append({
                        'time': current_time,
                        'layout': current_layout,
                        'modifiers_at_change': modifiers_pressed,
                        'window_changed': window_changed,
                        'window_handle': current_window
                    })
                    if len(layout_change_history) > 5:
                        layout_change_history.pop(0)
                    show_overlay_flag = False
                    if settings.show_overlay:
                        if modifiers_pressed:
                            show_overlay_flag = True
                            print("Overlay: модифікатори натиснуті зараз")
                        elif hasattr(self, '_recent_modifier_activity') and (current_time - self._recent_modifier_activity < 0.5):
                            show_overlay_flag = True
                            print("Overlay: недавня активність модифікаторів")
                        elif not window_changed and len(layout_change_history) >= 2:
                            time_diff = current_time - layout_change_history[-2]['time']
                            if time_diff < 1.0:
                                show_overlay_flag = True
                                print(f"Overlay: швидка зміна без зміни вікна ({time_diff:.2f}s)")
                        if show_overlay_flag:
                            iso_code = LCID[current_layout]["iso_code"]
                            try:
                                self.overlay.root.after(0, self.overlay.show_flag, f"{iso_code}.png")
                            except Exception as e:
                                print(errors().overlay.format(e=e))
                        else:
                            print(f"Overlay НЕ показано: window_changed={window_changed}, modifiers={modifiers_pressed}")
                    self.last_layout = current_layout
                # Відстежувати активність модифікаторів навіть без зміни розкладки
                if modifiers_pressed:
                    self._recent_modifier_activity = current_time
                # Оновити останнє активне вікно
                last_active_window = current_window
                # Очищати стару історію
                if len(layout_change_history) > 0:
                    layout_change_history = [change for change in layout_change_history 
                                           if current_time - change['time'] < 10.0]
            except Exception as e:
                print(f"Monitor error: {e}")
            # Динамічна затримка: частіше перевіряти коли є активність модифікаторів
            if modifiers_pressed or (hasattr(self, '_recent_modifier_activity') and 
                                   current_time - self._recent_modifier_activity < 1.0):
                time.sleep(0.02)  # 20ms при активності
            else:
                time.sleep(0.05)  # 50ms в звичайному режимі

    def monitor_with_polling_only(self):
        """Простий polling без детекції клавіш (запасний варіант)"""
        print("Використовується простий polling моніторинг")
        while True:
            try:
                current_layout = keyboard.get_current_layout_key()
                
                if current_layout != self.last_layout:
                    self.tray.update_icon(current_layout)
                    
                    # Завжди показувати overlay при зміні
                    if settings.show_overlay:
                        iso_code = LCID[current_layout]["iso_code"]
                        try:
                            self.overlay.root.after(0, self.overlay.show_flag, f"{iso_code}.png")
                        except Exception as e:
                            print(errors().overlay.format(e=e))
                    
                    self.last_layout = current_layout
                    
            except Exception as e:
                print(f"Monitor error: {e}")
            
            time.sleep(0.05)

    def cleanup(self):
        """Очистка ресурсів (залишено для сумісності)"""
        pass