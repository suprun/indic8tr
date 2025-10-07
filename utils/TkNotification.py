import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw
import os
import win32api
import win32gui
import winreg as reg

from utils.ResourceManager import ResourceManager as resources
# --- Налаштування ---
NOTIFICATION_WIDTH = 350
NOTIFICATION_HEIGHT = 300
CORNER_RADIUS = 16
FADE_STEP = 0.05
FADE_DELAY = 25
PADDING = 15
ALPHA_TRANSPARENCY = 0.9
TASKBAR_DETECTION_THRESHOLD = 20 # Допуск у пікселях для надійнішого визначення краю

# --- Функції для Windows API ---

def get_system_theme():
    """Визначає системну тему Windows за допомогою реєстру."""
    try:
        key = reg.OpenKey(reg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Themes\Personalize')
        theme_value = reg.QueryValueEx(key, 'AppsUseLightTheme')[0]
        return "dark" if theme_value == 0 else "light"
    except Exception:
        return "light"

def get_taskbar_position(width, height):
    """
    Визначає фінальну позицію (x_end, y_end) сповіщення.
    (x_start, y_start) повертається як плейсхолдер, але для fade-in не використовується.
    """
    
    taskbar_hwnd = win32gui.FindWindow("Shell_TrayWnd", None)
    screen_width = win32api.GetSystemMetrics(0)
    screen_height = win32api.GetSystemMetrics(1)

    # Позиції за замовчуванням (Assume bottom-right)
    x_end = screen_width - width - PADDING
    y_end = screen_height - height - PADDING
    
    # Для Fade-in початкова позиція = кінцева позиція
    x_start = x_end
    y_start = y_end

    if not taskbar_hwnd:
        return (x_start, y_start), (x_end, y_end)
        
    left, top, right, bottom = win32gui.GetWindowRect(taskbar_hwnd)
    
    # Визначення пристиковки до краю екрана
    is_docked_bottom = abs(screen_height - bottom) < TASKBAR_DETECTION_THRESHOLD
    is_docked_top = abs(top) < TASKBAR_DETECTION_THRESHOLD and (bottom - top) < screen_height / 5
    is_docked_right = abs(screen_width - right) < TASKBAR_DETECTION_THRESHOLD and (right - left) < screen_width / 5
    is_docked_left = abs(left) < TASKBAR_DETECTION_THRESHOLD and (right - left) < screen_width / 5

    # 1. Панель завдань ЗНИЗУ (Найпоширеніший випадок)
    if is_docked_bottom:
        x_end = screen_width - width - PADDING
        y_end = top - height - PADDING # З'являється над панеллю
    # 2. Панель завдань ЗВЕРХУ
    elif is_docked_top:
        x_end = screen_width - width - PADDING
        y_end = bottom + PADDING # З'являється під панеллю
    # 3. Панель завдань СПРАВА
    elif is_docked_right:
        x_end = left - width - PADDING # З'являється ліворуч від панелі
        y_end = screen_height - height - PADDING
    # 4. Панель завдань ЗЛІВА
    elif is_docked_left:
        x_end = right + PADDING # З'являється праворуч від панелі
        y_end = screen_height - height - PADDING
        
    # Для Fade-in кінцева позиція є і початковою
    return (x_end, y_end), (x_end, y_end)

# --- Створення скругленого фонового зображення ---
def create_rounded_background(width, height, radius, fill_color, header_image_path=None):
    """Створює зображення з круглими кутами та хедером за допомогою PIL."""
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    header_height = 150 

    draw.rounded_rectangle([0, 0, width, height], radius, fill=fill_color)

    if header_image_path and os.path.exists(header_image_path):
        header_img = Image.open(header_image_path).resize((width, header_height), Image.Resampling.LANCZOS).convert("RGBA")
        mask = Image.new('L', (width, height), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.rounded_rectangle([0, 0, width, height], radius, fill=255)
        header_area_mask = mask.crop((0, 0, width, header_height))
        img.paste(header_img, (0, 0), header_area_mask)
    
    shape = Image.new('L', (width, height), 0)
    draw_shape = ImageDraw.Draw(shape)
    draw_shape.rounded_rectangle([0, 0, width, height], radius, fill=255)
    img.putalpha(shape)
    
    return ImageTk.PhotoImage(img)

# --- Клас Сповіщення ---
class CustomNotification(tk.Toplevel):
    def __init__(self, master, title="Сповіщення"):
        super().__init__(master)
        
        self.notification_width = NOTIFICATION_WIDTH
        self.notification_height = NOTIFICATION_HEIGHT
        self.corner_radius = CORNER_RADIUS
        self.max_alpha = ALPHA_TRANSPARENCY
        self.system_theme = get_system_theme()

        if self.system_theme == "dark":
            self.base_color = "#333333"
            self.opposite_base_color = "#E0E0E0"
            self.fg_color = "white"
            self.header_image_path = resources().IMAGES['firstrun_header'] 
        else:
            self.base_color = "#E0E0E0"
            self.opposite_base_color = "#333333"
            self.fg_color = "black"
            self.header_image_path = resources().IMAGES['firstrun_header'] 
            
        self._create_dummy_images()
        
        # Визначення позицій (для fade-in x_start, y_start = x_end, y_end)
        (self.x_start, self.y_start), (self.x_end, self.y_end) = get_taskbar_position(
            self.notification_width,
            self.notification_height
        )

        # 1. Налаштування вікна
        self.title(title)
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.attributes("-alpha", 0.0) # 💡 Починаємо з повної прозорості (0.0)
        
        # Колір прозорості (для скруглення)
        self.transparency_color = '#010101'
        try:
            self.wm_attributes("-transparentcolor", self.transparency_color)
        except tk.TclError:
            self.transparency_color = self.base_color

        # Встановлення ФІНАЛЬНОЇ позиції (вікно з'явиться тут, але прозоре)
        self.geometry(f'{self.notification_width}x{self.notification_height}+{int(self.x_end)}+{int(self.y_end)}')

        # Створення віджетів
        self._create_widgets()

        # Початок анімації: fade-in
        self.fade_in()
        
    def _create_dummy_images(self):
        """Створення заглушок для фонових зображень та іконок."""
        for path, color in [(self.header_image_path, "#4A90E2" if self.system_theme == "dark" else "#A8D8F7")]:
            if not os.path.exists(path):
                img = Image.new('RGB', (NOTIFICATION_WIDTH, 60), color=color)
                draw = ImageDraw.Draw(img)
                draw.text((10, 20), "HEADER", fill="white", font=None)
                img.save(path)
                
        close_img = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
        draw = ImageDraw.Draw(close_img)
        line_color = "white" if self.system_theme == "dark" else "black"
        draw.line((3, 3, 13, 13), fill=line_color, width=2)
        draw.line((3, 13, 13, 3), fill=line_color, width=2)
        self.close_icon = ImageTk.PhotoImage(close_img)


    def _create_widgets(self):
        """Створення всіх елементів сповіщення."""
        
        # 1. Canvas для скругленого фону
        self.bg_image = create_rounded_background(
            self.notification_width, self.notification_height, self.corner_radius,
            self.base_color, self.header_image_path
        )
        
        self.canvas = tk.Canvas(
            self, width=self.notification_width, height=self.notification_height,
            highlightthickness=0, bg=self.transparency_color
        )
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_image(0, 0, image=self.bg_image, anchor="nw")
        
        # 2. Кнопка "Хрестик"
        self.close_button = tk.Button(
            self.canvas,
            image=self.close_icon,
            command=self.fade_out,
            bd=0,
            bg=self.opposite_base_color if self.system_theme == "dark" else self.base_color,
            activebackground=self.opposite_base_color if self.system_theme == "dark" else self.base_color,
            relief="solid"
        )
        self.close_button.image = self.close_icon
        
        self.canvas.create_window(
            self.notification_width - 25, 25, window=self.close_button, anchor="center"
        )

        # 3. Текст сповіщення
        self.message_label = tk.Label(
            self.canvas,
            text=f"Сповіщення з'явилося плавно (fade-in)!\nТема: {self.system_theme.upper()}.\nПозиція: {int(self.x_end)}, {int(self.y_end)}",
            fg=self.fg_color, bg=self.base_color,
            wraplength=self.notification_width - 40, justify="left", font=("Segoe UI", 10)
        )
        self.canvas.create_window(
            self.notification_width // 2, self.notification_height // 2 + 50,
            window=self.message_label, anchor="center"
        )
        
        # 4. Кастомна кнопка внизу
        button_color = "#0078D4" if self.system_theme == "light" else "#4A90E2"
        self.custom_button = tk.Button(
            self.canvas,
            text="Виконати дію і Закрити",
            command=lambda: self.execute_and_close(self.custom_action),
            bd=0, relief="ridge", bg=button_color, fg="white",
            activebackground="#005A9E", activeforeground="white",
            font=("Segoe UI", 10, "bold"), padx=10, pady=5,
        )
        self.canvas.create_window(
            self.notification_width // 2, self.notification_height - 30,
            window=self.custom_button, anchor="center"
        )
        
    def custom_action(self):
        """Функція, яку виконує кастомна кнопка."""
        print("✅ Кастомна функція виконана!")
        
    def execute_and_close(self, action):
        """Виконує функцію і закриває сповіщення."""
        action()
        self.fade_out()

    # --- Анімація (Оновлено для Fade-In) ---
    
    def fade_in(self):
        """Анімація плавного появи (Fade-in)."""
        current_alpha = self.attributes("-alpha")
        if float(current_alpha) < self.max_alpha:
            new_alpha = float(current_alpha) + FADE_STEP
            # Запобігання перевищенню максимальної прозорості
            if new_alpha > self.max_alpha:
                new_alpha = self.max_alpha
            self.attributes("-alpha", new_alpha)
            self.after(FADE_DELAY, self.fade_in)
        else:
            print("Анімація появи завершена.")


    def fade_out(self):
        """Анімація плавного зникнення (Fade-out)."""
        current_alpha = self.attributes("-alpha")
        if float(current_alpha) > 0.0:
            new_alpha = float(current_alpha) - FADE_STEP
            if new_alpha < 0.0:
                new_alpha = 0.0
            self.attributes("-alpha", new_alpha)
            self.after(FADE_DELAY, self.fade_out)
        else:
            self.destroy()

if __name__ == "__main__":
    # Створення тимчасових заглушок для PIL, якщо вони не існують
    if not os.path.exists("light_header.png"):
        Image.new('RGB', (NOTIFICATION_WIDTH, 60), color="#A8D8F7").save("light_header.png")
    if not os.path.exists("dark_header.png"):
        Image.new('RGB', (NOTIFICATION_WIDTH, 60), color="#4A90E2").save("dark_header.png")

    root = tk.Tk()
    root.withdraw()
    
    notification = CustomNotification(root)
    root.notification = notification

    root.mainloop()
