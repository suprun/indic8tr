import tkinter as tk
from PIL import ImageTk
from utils.ResourceManager import ResourceManager as resources
from utils.SettingsManager import settings
from core.Errors import Errors as errors

class FlagOverlay:
    def __init__(self, root):
        self.root = root
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-transparentcolor", "black")
        self.root.configure(bg="black")
        self.label = tk.Label(self.root, bg="black")
        self.label.pack()
        self.screen_w = self.root.winfo_screenwidth()
        self.screen_h = self.root.winfo_screenheight()
        self.fade_job = None
        self.POSITIONS = {
            "top-left": (settings.offset, settings.offset),
            "bottom-left": (settings.offset, -settings.offset),
            "top-right": (-settings.offset, settings.offset),
            "bottom-right": (-settings.offset, -settings.offset),
            "top-center": ("center", settings.offset),
            "bottom-center": ("center", -settings.offset),
            "center": ("center", "center")
              # Placeholder, actual position is dynamic
        }
        self.cursor_positions = {
            "follow-cursor": ("follow", "follow"),
            "follow-top": ("follow", settings.offset),
            "follow-bottom": ("follow", -settings.offset),
        }

    def show_flag(self, filename, wh=settings.wh):
        default_offset=settings.default_offset
        
        if self.fade_job:
            self.root.after_cancel(self.fade_job)
            self.fade_job = None
        img = resources.load_image_safe(resources().OVERLAY_FLAGS_DIR, filename, (wh, wh))
        self.tk_img = ImageTk.PhotoImage(img)
        self.label.config(image=self.tk_img)
        print(f"{self.cursor_positions[settings.follow_cursor_mode]}")
        if settings.follow_cursor:
            x_offset, y_offset = self.cursor_positions[settings.follow_cursor_mode]
        else:
            x_offset, y_offset = self.POSITIONS[settings.current_position] 
        
        # Обробка x координати
        if x_offset == "center":
            x = (self.screen_w // 2) - wh // 2
        elif x_offset == "follow":
            cursor_x = self.root.winfo_pointerx()
            x = cursor_x - wh // 2
            x = max(default_offset, min(x, self.screen_w - wh - default_offset))
        else:
            x = x_offset if x_offset >= 0 else self.screen_w + x_offset - wh
        # Обробка y координати
        if y_offset == "center":
            y = (self.screen_h // 2) - wh // 2
        elif y_offset == "follow":
            cursor_y = self.root.winfo_pointery()
            y = cursor_y - wh + default_offset-100
            y = max(default_offset, min(y, self.screen_h - wh - default_offset))
        else:
            y = y_offset if y_offset >= 0 else self.screen_h + y_offset - wh
            
        self.root.geometry(f"+{x}+{y}")
        self.root.deiconify()
        self.root.attributes("-alpha", 0.0)
        self.fade_in(0.0)

    def fade_in(self, alpha):
        if alpha < 1.0:
            self.root.attributes("-alpha", alpha)
            self.fade_job = self.root.after(30, self.fade_in, alpha + 0.1)
        else:
            self.root.attributes("-alpha", 1.0)
            self.fade_job = self.root.after(800, self.fade_out, 1.0)

    def fade_out(self, alpha):
        if alpha > 0:
            self.root.attributes("-alpha", alpha)
            self.fade_job = self.root.after(30, self.fade_out, alpha - 0.1)
        else:
            self.root.withdraw()
            self.fade_job = None