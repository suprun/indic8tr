import os
import json
from utils.ResourceManager import ResourceManager as resources
from core.Errors import Errors as errors
from utils.StartupManager import startup 

class SettingsManager:
    def __init__(self, settings_file, error_messages):
        self.settings_file = settings_file
        self.error_messages = error_messages
        self.current_position = "bottom-center"
        self.show_overlay = True
        self.follow_cursor = False
        self.follow_cursor_mode = "follow-cursor"  # "follow-cursor", "follow-top", "follow-bottom"
        self.default_offset = 50
        self.offset = 50
        self.wh = 96
        self.version = "1.0.4"  # Поточна версія програми

    def load(self):
        """Завантажити налаштування з файлу та перевірити автостарт"""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.current_position = data.get("position", self.current_position)

                    self.check_json_autostart = data.get("autostart", True)
                    check_is_in_startup=startup.is_in_startup()
                    print(f"Автостарт (файл): {self.check_json_autostart}, (ярлик): {check_is_in_startup}")
                    if check_is_in_startup is False and self.check_json_autostart is True:
                        startup.add_to_startup()
                        self.autostart = self.check_json_autostart 
                        data["autostart"] = self.autostart
                    else:
                        self.autostart = check_is_in_startup
                        # Синхронізувати файл з фактичним станом
                    print(f"Автостарт (після синхронізації): {self.autostart}")

                    self.show_overlay = data.get("show_overlay", self.show_overlay)
                    self.follow_cursor = data.get("follow_cursor", False)
                    self.follow_cursor_mode = data.get("follow_cursor_mode", "follow-cursor")
                    self.default_offset = data.get("default_offset", 50)
                    self.offset = data.get("offset", 50)
                    self.wh = data.get("wh", 96)
                    self.version = data.get("version", "1.0.4")  # Додати версію, якщо потрібно
            except Exception as e:
                print(self.error_messages.settings_read.format(e=e))

    def save(self):
        """Зберегти всі налаштування в один файл"""
        data = {
            "position": self.current_position,
            "autostart": self.autostart,
            "show_overlay": self.show_overlay,
            "follow_cursor": self.follow_cursor,
            "follow_cursor_mode": self.follow_cursor_mode,
            "default_offset": self.default_offset,
            "offset": self.offset,
            "wh": self.wh
            # "version": "1.0.4"  # Додати версію, якщо потрібно
        }
        try:
            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(self.error_messages.settings_write.format(e=e))
            
settings = SettingsManager(resources().SETTINGS_FILE, errors())