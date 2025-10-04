# ===== Клас для автозапуску =====
import os
import sys
import win32com.client

class StartupManager:
    def __init__(self, name="KeyboardIndicator"):
        self.name = name

    def get_startup_path(self):
        return os.path.join(os.environ["APPDATA"], "Microsoft\\Windows\\Start Menu\\Programs\\Startup")

    def get_executable_path(self):
        if getattr(sys, 'frozen', False):
            return sys.executable
        else:
            return os.path.abspath(sys.argv[0])

    def is_in_startup(self):
        shortcut_path = os.path.join(self.get_startup_path(), f"{self.name}.lnk")
        exists = os.path.exists(shortcut_path)
        if exists:
            print(f"Ярлик автозапуску знайдено: {shortcut_path}")
        else:
            print(f"Ярлик автозапуску не знайдено: {shortcut_path}")
        return exists

    def create_com_shortcut(self):
        try:
            import pythoncom
            pythoncom.CoInitialize()
            return win32com.client.Dispatch("WScript.Shell")
        except:
            return win32com.client.Dispatch("WScript.Shell")

    def add_to_startup(self):
        try:
            script_path = self.get_executable_path()
            startup_dir = self.get_startup_path()
            shortcut_path = os.path.join(startup_dir, f"{self.name}.lnk")

            shell = self.create_com_shortcut()
            shortcut = shell.CreateShortcut(shortcut_path)

            if script_path.endswith(".exe"):
                shortcut.TargetPath = script_path
            else:
                shortcut.TargetPath = sys.executable
                shortcut.Arguments = f'"{script_path}"'

            shortcut.WorkingDirectory = os.path.dirname(script_path)
            shortcut.IconLocation = script_path
            shortcut.save()
            print(f"✅ Додано до автозапуску: {shortcut_path}")
        except Exception as e:
            print(f"❌ Помилка додавання до автозапуску: {e}")

    def remove_from_startup(self):
        try:
            shortcut_path = os.path.join(self.get_startup_path(), f"{self.name}.lnk")
            if os.path.exists(shortcut_path):
                os.remove(shortcut_path)
                print(f"✅ Видалено з автозапуску: {shortcut_path}")
            else:
                print(f"ℹ️  Ярлик автозапуску не знайдено: {shortcut_path}")
        except Exception as e:
            print(f"❌ Помилка видалення з автозапуску: {e}")

startup = StartupManager()