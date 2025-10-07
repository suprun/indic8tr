import os
import sys
from PIL import Image
from core.Errors import Errors as errors

class ResourceManager:
    def __init__(self):
        self.base_path = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
        self.TRAY_FLAGS_DIR = self.get_resource_path("../images/tray")
        self.OVERLAY_FLAGS_DIR = self.get_resource_path("../images/overlay")
        self.SETTINGS_FILE = self.get_resource_path("../settings.json")
        self.ABOUT_URLS = {
            'about': "https://github.com/suprun/indic8tr",
            'license': "LICENSE.txt",
            'help': "https://github.com/suprun/indic8tr/wiki",
            'icons8': "https://icons8.com",
            'roadui': "https://agentyzmin.github.io/Road-UI-Font/"
        }
        self.ICONS = {
            'favicon': self.get_resource_path("../images/icons/favicon.ico"),
            'licence': self.get_resource_path("../images/icons/licence-16.png"),
            'github': self.get_resource_path("../images/icons/github-16.png"),
            'link': self.get_resource_path("../images/icons/link-16.png"),
            'close': self.get_resource_path("../images/icons/close-16.png"),
        }
        self.IMAGES = {
            'about_header': self.get_resource_path("../images/img/about_header.png"),
            'firstrun_header': self.get_resource_path("../images/img/firstrun_header.png")
        }

    def get_resource_path(self, relative_path):
        """Отримати абсолютний шлях до ресурсу для Nuitka"""
        return os.path.join(self.base_path, relative_path)
    
    
    def load_image_safe(base_dir, filename, size=(32, 32)):
        """Безпечне завантаження зображення з перевіркою існування"""
        full_path = os.path.join(base_dir, filename)
        if not os.path.exists(full_path):
            print(errors().image_not_found.format(path=full_path))
            # Створити placeholder зображення
            return Image.new('RGBA', size, (128, 128, 128, 255))
        try:
            return Image.open(full_path).convert("RGBA").resize(size, Image.Resampling.LANCZOS)
        except Exception as e:
            print(f"Помилка завантаження {full_path}: {e}")
            return Image.new('RGBA', size, (128, 128, 128, 255))