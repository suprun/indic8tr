from threading import Thread
import pystray
from pystray import MenuItem as item, Menu
from PIL import Image
from plyer import notification

from utils.ResourceManager import ResourceManager as resources
from utils.SettingsManager import settings
from utils.StartupManager import startup
from utils.WinShutdownExit import app_exit

from core.KeyboardManager import keyboard
from core.Errors import Errors as errors
from core.lcid import LCID
from core.LayoutMonitor import LayoutMonitor
from core.AboutWindow import AboutWindow

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
               
    def show_notification(self, title="Сповіщення", message="Це сповіщення з вашого застосунку!",   type_="info"):
        """
        Відправляє toast-повідомлення Windows без створення іконки в треї.
        type_ : str — 'info', 'warning', 'error', 'success'
        """
        # Налаштування типів сповіщень (таймаути у секундах)
        config = {
            "info": 5,
            "warning": 6,
            "error": 8,
            "success": 4
        }
        timeout = config.get(type_, 5)
        try:
            notification.notify(
                title=title,
                message=message,
                timeout=timeout
                # app_icon не вказуємо → трей не створюється
            )
        except Exception as e:
            print(f"[TrayIcon Notification Error] {e}")   
       
 
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
