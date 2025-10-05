import sys
from threading import Thread
import pystray
from pystray import MenuItem as item, Menu
from PIL import Image

from utils.ResourceManager import ResourceManager as resources
from utils.SettingsManager import settings
from utils.StartupManager import startup
from utils.WinShutdownExit import app_exit

from core.KeyboardManager import keyboard
from core.Errors import Errors as errors
from core.lcid import LCID
from core.LayoutMonitor import LayoutMonitor
from core.AboutWindow import AboutWindow

from threading import Timer

from windows_toasts import Toast, WindowsToaster, ToastImage, ToastButton
# Примітка: TOASTER має бути ініціалізований поза класом або як атрибут класу
TOASTER = WindowsToaster("KeyboardLayoutIndicator")
class TrayIcon:  
    def __init__(self, overlay):
        self.icon = None
        self.overlay = overlay
        self.current_layout = "0x0409"  # default en-US
        self.default_layout = keyboard.get_default_keyboard_layout()
        print(f"Default layout: {self.default_layout}")
        self._icon_thread_started = False
        self.monitor = None  # type: LayoutMonitor | None
        
    def load_icon(self, icon_path, default_size=(16, 16)):
        """Завантажити іконку з файлу або створити пусту, якщо файл відсутній"""  
        try:
            icon = Image.open(icon_path).resize(default_size, Image.Resampling.LANCZOS)
            return icon
        except Exception as e:
            print(f"Failed to load icon {icon_path}: {e}")
            # Створюємо пусту іконку, якщо не вдалося завантажити
            empty_icon = Image.new('RGBA', default_size, (0, 0, 0, 0))
            return empty_icon
               
    def show_notification(self, icon, title="Сповіщення", message="Це сповіщення з вашого застосунку!"):
        """Відправляє системне сповіщення (Toast Notification) з заданими заголовком та текстом."""
        # Fix: Забезпечуємо, що метод приймає аргументи title та message
        icon.notify(message, title)
        print(f"Сповіщення '{title}' надіслано.")

    
    def handle_toast_action_with_image(self, action_id):
        """Обробник, який викликається при натисканні кнопки у сповіщенні."""
        print(f"Дія виконана зі сповіщення з зображенням: {action_id}")
        
        if action_id == "show_current_layout":
            # Приклад: показати оверлей
            self.overlay.show() 
            print("Оверлей показано.")
        elif action_id == "settings_from_toast":
            # Приклад: функція, яка відкриває налаштування
            # Замініть на ваш реальний метод відкриття налаштувань
            print("Відкриття налаштувань...") 
    
    # --- Метод надсилання сповіщення з зображенням та кнопками ---
    def show_notification_with_image_and_buttons(self, image_path, title, message):
        """Надсилає сповіщення Windows Toast Notification з довільним зображенням та кнопками."""
        
        # 1. Створення об'єкта сповіщення (Toast)
        new_toast = Toast()
        new_toast.text_fields = [title, message]
        
        # 2. Додавання зображення (App Logo Override - маленький логотип)
        try:
            # Зображення буде відображатися як маленький круглий значок
            new_toast.app_logo_override = ToastImage(src=image_path, alt="Layout Flag")
            
            # Якщо вам потрібне велике "героїчне" зображення, використовуйте:
            # new_toast.hero_image = ToastImage(src=image_path, alt="Layout Hero")
            
        except Exception as e:
            # Це може статися, якщо шлях до файлу неправильний
            print(f"Помилка при додаванні зображення до сповіщення: {e}")
            
        # 3. Додавання кнопок
        new_toast.buttons = [
            ToastButton(
                text="Показати розкладку", 
                arguments="show_current_layout", 
                on_activated=self.handle_toast_action_with_image
            ),
            ToastButton(
                text="Налаштування", 
                arguments="settings_from_toast", 
                on_activated=self.handle_toast_action_with_image
            )
        ]
        
        # 4. Надсилання сповіщення у фоновому потоці
        # Це запобігає блокуванню головного циклу Tkinter
        def send_toast():
            try:
                TOASTER.show_toast(new_toast)
            except Exception as e:
                print(f"Помилка при відправці тосту через WindowsToaster: {e}")

        threading.Thread(target=send_toast, daemon=True).start()
    
    def update_icon(self, layout_key):
        if layout_key not in LCID:
            return
        self.current_layout = layout_key
        iso_code = LCID[layout_key]["iso_code"]
        flag_filename = f"{iso_code}.png"
        
        try:
            image = resources.load_image_safe(resources().TRAY_FLAGS_DIR, flag_filename, (32, 32))
            if self.icon is None:
                self.icon = pystray.Icon("LangTray", image, "Keyboard Layout", menu=self.create_menu())
                if not self._icon_thread_started:
                    Thread(target=self.icon.run, daemon=True).start()
                    self._icon_thread_started = True
            else:
                self.icon.icon = image
        except Exception as e:
            print(errors().tray_icon.format(e=e))

    def handle_toast_action_with_image(self, args):
        """
        Обробник, який викликається при натисканні кнопки або тіла сповіщення.
        Args - це словник {'arguments': '...', 'user_input': {...}}
        """
        action_id = args.get('arguments', '')
        print(f"Дія виконана зі сповіщення з зображенням: {action_id}")
        
        # Обробка дій
        if action_id == "show_current_layout":
            print(f"Поточна розкладка: {self.current_layout}")
            self.overlay.show()
        elif action_id == "open_settings":
            self.open_about(None, None)
            print("Відкриття налаштувань з тосту...")
            
    def show_notification_with_image_and_buttons(self, image_path, title, message):
        """
        Надсилає сповіщення Windows Toast Notification з довільним зображенням та кнопками.
        """
        
        # 1. Визначення зображення (як App Logo Override)
        # Використовуємо словник для визначення розміщення
        icon_config = {
            'src': image_path, 
            'placement': 'appLogoOverride'
        }
        
        # 2. Визначення кнопок
        buttons_config = [
            # Кнопка 1: Викликає вашу функцію
            {
                'activationType': 'protocol', 
                'arguments': 'show_current_layout', # Ідентифікатор дії
                'content': 'Показати розкладку'
            },
            # Кнопка 2: Викликає вашу функцію
            {
                'activationType': 'protocol', 
                'arguments': 'open_settings', # Ідентифікатор дії
                'content': 'Налаштування'
            }
        ]
        
        try:
            # 3. Надсилання сповіщення
            # Використовуємо 'on_click' для обробки натискань кнопок
            toast(
                title=title,
                body=message,
                icon=icon_config, # Передаємо іконку
                buttons=buttons_config, # Передаємо кнопки
                on_click=self.handle_toast_action_with_image # Обробник
            )
            
        except Exception as e:
            print(f"Помилка при відправці тосту через win11toast: {e}")


    def toggle_autostart(self, icon, item):
        """Перемикання автостарту"""
        settings.autostart = not settings.autostart
        startup_mgr = startup
        if settings.autostart:
            startup_mgr.add_to_startup()
        else:
            startup_mgr.remove_from_startup()
        settings.save()
        icon.update_menu()

    def toggle_follow_cursor(self, icon, item, pos_key):
        if settings.follow_cursor_mode == pos_key and settings.follow_cursor:
        # Якщо вибрано вже активний режим, нічого не робимо
            return
        
        settings.follow_cursor = not settings.follow_cursor or (settings.follow_cursor_mode != pos_key)
        settings.follow_cursor_mode = pos_key        
        settings.save()
        icon.update_menu()

    def toggle_overlay(self, icon, item):
        settings.show_overlay = not settings.show_overlay
        settings.save()
        icon.update_menu()

    def set_position(self, pos_key):
        settings.current_position = pos_key
        settings.follow_cursor = False
        settings.save()

    def open_about(self, icon, item):
        about_window=AboutWindow(
        root=self.overlay.root,
        wh=[420, 530],
        about_url=resources().ABOUT_URLS['about'],
        license_url=resources().ABOUT_URLS['license'],
        help_url=resources().ABOUT_URLS['help'],
        links_urls=[resources().ABOUT_URLS['icons8'], resources().ABOUT_URLS['roadui']]
        )
        about_window.show()

    def quit_app(self, icon, item):
                # Fallback: старий спосіб
        if self.monitor is not None:
            self.monitor.cleanup()
        if self.icon:
            self.icon.stop()
        try:
            self.overlay.root.quit()
            self.overlay.root.destroy()
        except Exception:
            pass
        app_exit()

    def create_menu(self):
        lang = LCID.get(self.default_layout, LCID["0x0409"])
        
        position_menu = Menu(
            # Пункт "Show Overlay" на початку
            item(
                lang.get("show_overlay", "Show Overlay"),
                lambda icon, item: self.toggle_overlay(icon, item),
                checked=lambda item: settings.show_overlay
            ),

            # Сепаратор після "Show Overlay"
            Menu.SEPARATOR,

            # Група чекбоксів для позицій (неактивні, якщо "Show Overlay" вимкнено)
            item(
                lang.get("top_left", "Top Left"),
                lambda icon, item: self.set_position("top-left"),
                checked=lambda item: settings.current_position == "top-left" and not settings.follow_cursor,
                enabled=lambda item: settings.show_overlay
            ),
            item(
                lang.get("bottom_left", "Bottom Left"),
                lambda icon, item: self.set_position("bottom-left"),
                checked=lambda item: settings.current_position == "bottom-left" and not settings.follow_cursor,
                enabled=lambda item: settings.show_overlay
            ),
            item(
                lang.get("top_right", "Top Right"),
                lambda icon, item: self.set_position("top-right"),
                checked=lambda item: settings.current_position == "top-right" and not settings.follow_cursor,
                enabled=lambda item: settings.show_overlay
            ),
            item(
                lang.get("bottom_right", "Bottom Right"),
                lambda icon, item: self.set_position("bottom-right"),
                checked=lambda item: settings.current_position == "bottom-right" and not settings.follow_cursor,
                enabled=lambda item: settings.show_overlay
            ),
            item(
                lang.get("top_center", "Top Center"),
                lambda icon, item: self.set_position("top-center"),
                checked=lambda item: settings.current_position == "top-center" and not settings.follow_cursor,
                enabled=lambda item: settings.show_overlay
            ),
            item(
                lang.get("bottom_center", "Bottom Center"),
                lambda icon, item: self.set_position("bottom-center"),
                checked=lambda item: settings.current_position == "bottom-center" and not settings.follow_cursor,
                enabled=lambda item: settings.show_overlay
            ),
            item(
                lang.get("center", "Center"),
                lambda icon, item: self.set_position("center"),
                checked=lambda item: settings.current_position == "center" and not settings.follow_cursor,
                enabled=lambda item: settings.show_overlay
            ),

            # Сепаратор перед "Follow Cursor"
            Menu.SEPARATOR,

            # Пункт "Follow Cursor" (неактивний, якщо "Show Overlay" вимкнено)
            item(
                lang.get("follow_cursor", "Follow Cursor"),
                lambda icon, item: self.toggle_follow_cursor(icon, item, "follow-cursor"),
                checked=lambda item: settings.follow_cursor_mode == "follow-cursor" and settings.follow_cursor,
                enabled=lambda item: settings.show_overlay
            ),
            item(
                lang.get("follow_cursor_top", "Follow Cursor (Top)"),
                lambda icon, item: self.toggle_follow_cursor(icon, item, "follow-top"),
                checked=lambda item: settings.follow_cursor_mode == "follow-top" and settings.follow_cursor,
                enabled=lambda item: settings.show_overlay
            ),
            item(
                lang.get("follow_cursor_bottom", "Follow Cursor (Bottom)"),
                lambda icon, item: self.toggle_follow_cursor(icon, item, "follow-bottom"),
                checked=lambda item: settings.follow_cursor_mode == "follow-bottom" and settings.follow_cursor,
                enabled=lambda item: settings.show_overlay
            )    
        )
        options_menu = Menu(
            
            item(lang.get("run_at_startup", "Run at Startup"), self.toggle_autostart, 
                 checked=lambda item: settings.autostart),
           
        )
        menu = Menu(
            item(lang.get("options", "Options"), options_menu),
            item(lang.get("position", "Position"), position_menu),
            item(lang.get("about", "About"), self.open_about),
            
            Menu.SEPARATOR,
            item(lang.get("exit", "Exit"), self.quit_app)
        )
        return menu
