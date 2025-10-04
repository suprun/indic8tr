import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
import webbrowser
import ctypes
from utils.ResourceManager import ResourceManager as resources
from core.Errors import Errors as errors
from utils.SettingsManager import settings


class AboutWindow:
    _instance = None
    def __new__(cls, root, wh, about_url, license_url, help_url, links_urls):
        if cls._instance is None or not tk.Toplevel.winfo_exists(cls._instance.window):
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, root, wh, about_url, license_url, help_url, links_urls):
        
        if hasattr(self, 'window') and tk.Toplevel.winfo_exists(self.window):
            self.window.lift()
            self.window.focus_force()
            return
        
        super().__init__()
        self.root = root
        self.wh = wh
        self.about_url = about_url
        self.icons8_url = links_urls[0]
        self.roadui_url = links_urls[1]
        self.license_url = license_url
        self.help_url = help_url
        self.style = ttk.Style()
        self.style.configure("standart.TButton", padding=(10, 5))
        
        # Встановлюємо власну іконку
        self.root.iconbitmap(resources().ICONS['favicon'])
        # Розмір вікна
        self.WIDTH = wh[0]
        self.HEIGHT = wh[1]
        # Створюємо вікно
        self.window = tk.Toplevel(root)

        self.window.withdraw()

        self.window.title("About Keyboard Layout Indicator")
        self.window.resizable(False, False)

        # Встановлюємо кастомну іконку вікна
        self.set_window_icon()

        # Верхня частина вікна: зображення по ширині вікна
        self.add_header_image()

        # Нижня частина вікна: біла полоса з кнопкою "Close"
        self.add_footer_with_close_button()

        # Текст про програму
        self.add_about_text()

        # Кнопки для документації та ліцензії
        self.add_buttons()

        # Розміщуємо вікно біля курсора або посередині екрану
        self.window.update_idletasks()
        self.position_window()
       
        # Прив'язка закриття
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

    def show(self):
        
        """Показати вікно або підняти його, якщо вже відкрито, без миготіння."""
        
        if not tk.Toplevel.winfo_exists(self.window):
            # Якщо вікно було закрите, створюємо його знову
            AboutWindow._instance = None
            # Новий екземпляр буде правильно позиціонований у своєму __init__
            new_instance = AboutWindow(self.root,self.wh, self.about_url, self.license_url, self.help_url, [self.icons8_url, self.roadui_url])
            new_instance.show()
            return

        # 1. Примусово оновлюємо вікно (наприклад, якщо змінився контент)
        self.window.update_idletasks() 
        
        # 2. Повторно позиціонуємо вікно, поки воно ще приховане.
        # Це запобігає його появі у старому місці.
        self.position_window()
        
        # 3. Робимо його видимим в остаточній позиції
        self.window.deiconify() 
        
        # 4. Піднімаємо нагору та фокусуємо
        self.window.lift()
        self.window.focus_force()


    def on_close(self):
        self.window.destroy()
        AboutWindow._instance = None

    def set_window_icon(self):
        """Встановити кастомну іконку вікна"""
        try:
            # Шлях до файлу іконки
            icon_path = resources().ICONS['favicon']
            if os.path.exists(icon_path):
                self.window.iconbitmap(icon_path)
            else:
                # Якщо іконка відсутня, спробуємо отримати іконку з exe-файлу
                try:
                    myappid = 'mycompany.myapp.1.0'  # ID програми
                    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
                    self.window.iconbitmap(default=icon_path)
                except Exception as e:
                    print(f"Failed to set window icon: {e}")
        except Exception as e:
            print(f"Failed to set window icon: {e}")

    def position_window(self):
        try:
            # Отримуємо розміри екрану
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()

            x = (screen_width - self.WIDTH) // 2
            y = (screen_height - self.HEIGHT) // 2
            self.window.geometry(f"{self.WIDTH}x{self.HEIGHT}+{x}+{y}")
        except Exception as e:
            print(f"Failed to position window: {e}")
            self.window.geometry(f"{self.WIDTH}x{self.HEIGHT}+300+200")

    def add_header_image(self):
        """Додати зображення у верхню частину вікна"""
        try:
            image_path = resources().IMAGES['about_header']
            if os.path.exists(image_path):
                img = Image.open(image_path)
                img = img.resize((self.WIDTH, 150), Image.Resampling.LANCZOS)
                self.tk_img = ImageTk.PhotoImage(img)

                header_frame = tk.Frame(self.window)
                header_frame.pack(fill=tk.X, padx=0, pady=0)

                img_label = tk.Label(header_frame, image=self.tk_img)
                img_label.pack()

        except Exception as e:
            print(f"Failed to load header image: {e}")

    def add_about_text(self):
        """Додати текст про програму"""
        about_text = (
            "Keyboard Layout Indicator\n\n"
            "Version: {version}\n\n"
            "A simple tool to display the current keyboard layout.\n\n"
            "© 2025 Serhiy Suprun.".format(version=settings.version)
        )

        text_frame = tk.Frame(self.window)
        text_frame.pack(fill=tk.X, padx=(70,20), pady=10)

        label = ttk.Label(
            text_frame,
            text=about_text,
            justify=tk.LEFT,
            wraplength=self.WIDTH - 100
        )
        label.pack(anchor="w")

        # Додаємо клікабельне посилання під текстом
        link_frame = tk.Frame(self.window)
        link_frame.pack(fill=tk.X, padx=(65,20), pady=(10,0))

        img = Image.open(resources().ICONS['link'])          # шлях до файлу
        img = img.resize((12, 12))            # опційно змінюємо розмір
        photo = ImageTk.PhotoImage(img)       # перетворюємо у формат tkinter

        link_label = tk.Label(link_frame, text=self.about_url, fg="blue", cursor="hand2", anchor="w", image=photo, compound="right", padx=4)
        link_label.pack(anchor="w")
        link_label.bind("<Button-1>", lambda e: webbrowser.open(self.about_url))
        link_label.image = photo

        link_frame = tk.Frame(self.window)
        link_frame.pack(fill=tk.X, padx=(65,20), pady=(4,0))

        img = Image.open(resources().ICONS['link'])          # шлях до файлу
        img = img.resize((12, 12))            # опційно змінюємо розмір
        photo = ImageTk.PhotoImage(img)

        link_label = tk.Label(link_frame, text="Icons by Icons8 (https://icons8.com)", fg="blue", cursor="hand2", anchor="w", image=photo, compound="right", padx=4)
        link_label.pack(anchor="w")
        link_label.bind("<Button-1>", lambda e: webbrowser.open(self.icons8_url))
        link_label.image = photo

        link_frame = tk.Frame(self.window)
        link_frame.pack(fill=tk.X, padx=(65,20), pady=(4,20))

        img = Image.open(resources().ICONS['link'])          # шлях до файлу
        img = img.resize((12, 12))            # опційно змінюємо розмір
        photo = ImageTk.PhotoImage(img)

        link_label = tk.Label(link_frame, text="Road-UI-Font: CC BY-ND 4.0", fg="blue", cursor="hand2", anchor="w", image=photo, compound="right", padx=4)
        link_label.pack(anchor="w")
        link_label.bind("<Button-1>", lambda e: webbrowser.open(self.icons8_url))
        link_label.image = photo
    
    
    
    def add_buttons(self):
        """Додати кнопки для документації та ліцензії"""
        buttons_frame = ttk.Frame(self.window)
        buttons_frame.pack(fill=tk.X, padx=(70,20), pady=(4, 6))
        
        # Кнопка "Відкрити справку"
        help_buttton_icon = ImageTk.PhotoImage(Image.open(resources().ICONS['github']).resize((16, 16), Image.Resampling.LANCZOS))
        
        help_button = ttk.Button(
            buttons_frame,
            text="Get Help",
            image=help_buttton_icon,
            compound="left",
            command=lambda: webbrowser.open(self.help_url),
            style="standart.TButton"
        )
        help_button.image=help_buttton_icon
        help_button.pack(side="left", padx=0, pady=(4, 6))
        
        # Кнопка "Показати ліцензію" (відкриває текстовий файл)
        licence_buttton_icon = ImageTk.PhotoImage(Image.open(resources().ICONS['licence']).resize((16, 16), Image.Resampling.LANCZOS))

        license_button = ttk.Button(
            buttons_frame,
            text="Show License",
            compound="left",
            image=licence_buttton_icon,
            command=self.open_license_file,
            style="standart.TButton"
        )
        
        license_button.image=licence_buttton_icon
        license_button.pack(side="left", padx=10, pady=(4, 6))

    def add_footer_with_close_button(self):
        """Додати білу полосу внизу з кнопкою 'Close'"""
        footer_frame = tk.Frame(self.window, bg="white", height=72)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM)
        footer_frame.pack_propagate(False)
        self.style.configure("close.TButton", padding=(0, 3))
        # Кнопка "Close" справа
        close_button_icon = ImageTk.PhotoImage(Image.open(resources().ICONS['close']).resize((16, 16), Image.Resampling.LANCZOS))
        close_button = ttk.Button(
            footer_frame,
            text="Close",
            image=close_button_icon,
            compound="left",
            command=self.window.destroy,
            style="close.TButton"
        )
        close_button.image = close_button_icon
        close_button.pack(side="right", padx=50, pady=(0,5))

    def open_license_file(self):
        """Відкрити текстовий файл з ліцензією"""
        if os.path.exists(self.license_url):
            try:
                os.startfile(self.license_url)
            except Exception as e:
                errors.alert(f"Failed to open license file: {e}")
        else:
            errors.alert("License file not found!")
