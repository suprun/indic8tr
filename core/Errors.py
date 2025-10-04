from tkinter import messagebox

class Errors:
    def __init__(self):
        self.settings_read = "Не вдалось прочитати settings.json: {e}"
        self.settings_write = "Не вдалось зберегти settings.json: {e}"
        self.tray_icon = "Не вдалось завантажити іконку для трею: {e}"
        self.overlay = "Overlay error: {e}"
        self.image_not_found = "Файл зображення не знайдено: {path}"

    def alert(message: str):
        """Показати повідомлення про помилку"""
        err_title = "Error"
        messagebox.showerror(err_title, message)