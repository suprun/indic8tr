
import os
import json
from utils.ResourceManager import ResourceManager as resources
from core.Errors import Errors as errors
from utils.StartupManager import startup

class SettingsManager:
    def __init__(self, error_messages):
        appdata_dir = os.environ.get('APPDATA') or os.path.expanduser('~')
        app_settings_dir = os.path.join(appdata_dir, 'Indic8tr')
        os.makedirs(app_settings_dir, exist_ok=True)
        self.settings_file = os.path.join(app_settings_dir, 'settings.json')
        self.error_messages = error_messages
        # Load default data from settings.json in project root
        default_data = {}
        default_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'settings.json')
        if os.path.exists(default_path):
            with open(default_path, 'r', encoding='utf-8') as f:
                default_data = json.load(f)
        # If settings file does not exist in APPDATA, create it from default_data
        if not os.path.exists(self.settings_file):
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(default_data, f, indent=4, ensure_ascii=False)
        # Set attributes from default_data
        self.current_position = default_data.get("position", "bottom-center")
        self.show_overlay = default_data.get("show_overlay", True)
        self.follow_cursor = default_data.get("follow_cursor", False)
        self.follow_cursor_mode = default_data.get("follow_cursor_mode", "follow-cursor")
        self.default_offset = default_data.get("default_offset", 50)
        self.offset = default_data.get("offset", 50)
        self.wh = default_data.get("wh", 96)
        self.version="0.9.04.001"
        self.firstrun = default_data.get("firstrun", True)
        self.autostart = False  # Чи є ярлик в автозавантаженні

    def load(self):
        """Завантажити налаштування з APPDATA/settings.json та перевірити автостарт"""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.current_position = data.get("position", self.current_position)
                    self.check_json_autostart = data.get("autostart", True)
                    check_is_in_startup = startup.is_in_startup()
                    print(f"Автостарт (файл): {self.check_json_autostart}, (ярлик): {check_is_in_startup}")
                    if check_is_in_startup is False and self.check_json_autostart is True:
                        startup.add_to_startup()
                        self.autostart = self.check_json_autostart
                        data["autostart"] = self.autostart
                    else:
                        self.autostart = check_is_in_startup
                    print(f"Автостарт (після синхронізації): {self.autostart}")
                    self.show_overlay = data.get("show_overlay", self.show_overlay)
                    self.follow_cursor = data.get("follow_cursor", self.follow_cursor)
                    self.follow_cursor_mode = data.get("follow_cursor_mode", self.follow_cursor_mode)
                    self.default_offset = data.get("default_offset", self.default_offset)
                    self.offset = data.get("offset", self.offset)
                    self.wh = data.get("wh", self.wh)
                    self.version = data.get("version", self.version)
                    self.firstrun = data.get("firstrun", self.firstrun)
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
            "wh": self.wh,
            "version": self.version,  # Додати версію, якщо потрібно
            "firstrun": self.firstrun
        }
        try:
            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(self.error_messages.settings_write.format(e=e))
            
settings = SettingsManager(errors())