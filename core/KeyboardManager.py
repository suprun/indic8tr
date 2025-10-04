import win32api
import win32gui
import win32con
import win32process

from ctypes import windll

from core.lcid import LCID
from core.Errors import Errors as errors

class KeyboardLayoutManager:
    def __init__(self):
        try:
            self.HOOK_AVAILABLE = True
        except ImportError:
            self.HOOK_AVAILABLE = False

    def get_key_state(self, vk_code: int) -> bool:
        """Перевірити стан клавіші через GetAsyncKeyState"""
        try:
            if self.HOOK_AVAILABLE:
                state = windll.user32.GetAsyncKeyState(vk_code)
                # 0x8000 = натиснута зараз, 0x0001 = була натиснута з останньої перевірки
                return (state & 0x8000) != 0 or (state & 0x0001) != 0
            return False
        except:
            return False

    def check_modifier_keys_pressed(self) -> bool:
        """Перевірити чи натиснуті модифікатори"""
        if not self.HOOK_AVAILABLE:
            return False
        try:
            keys_to_check = [
                0xA0,  # VK_LSHIFT
                0xA1,  # VK_RSHIFT
                0xA2,  # VK_LCONTROL
                0xA3,  # VK_RCONTROL
                0xA4,  # VK_LMENU (Alt)
                0xA5,  # VK_RMENU (Alt)
                0x5B,  # VK_LWIN
                0x5C,  # VK_RWIN
            ]
            return any(self.get_key_state(key) for key in keys_to_check)
        except:
            return False

    def get_current_layout_key(self) -> str:
        """Отримати поточну розкладку"""
        try:
            hwnd = win32gui.GetForegroundWindow()
            tid = win32process.GetWindowThreadProcessId(hwnd)[0]
            layout_id = win32api.GetKeyboardLayout(tid) & 0xffff
            hex_id = f"0x{layout_id:04x}"
            return hex_id if hex_id in LCID else "0x0409"
        except:
            return "0x0409"

    def get_default_keyboard_layout(self) -> str:
        """Отримати розкладку клавіатури за замовчуванням з реєстру"""
        try:
            key = win32api.RegOpenKeyEx(
                win32con.HKEY_CURRENT_USER,
                r"Keyboard Layout\Preload",
                0,
                win32con.KEY_READ
            )
            default_layout_id, _ = win32api.RegEnumValue(key, 0)
            win32api.RegCloseKey(key)
            return f"0x{default_layout_id:04x}"
        except Exception as e:
            print(f"Помилка отримання розкладки за замовчуванням: {e}")
            return "0x0409"  # Англійська (США)

keyboard = KeyboardLayoutManager()