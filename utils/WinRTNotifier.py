import os
from winrt.windows.ui.notifications import ToastNotificationManager, ToastNotification
from winrt.windows.data.xml.dom import XmlDocument

class WinRTNotifier:
    """
    Клас для toast-повідомлень Windows через WinRT (Python).
    Працює без AppID, тому Windows додає короткочасну системну іконку у треї.
    Підтримує кастомну іконку toast.
    """

    def __init__(self, app_name: str = "NDIC8TR"):
        self.app_name = app_name

    def send_toast(self, title: str, message: str, icon_path: str = None):
        """
        Показує toast з кастомною іконкою.
        title : заголовок
        message : текст
        icon_path : шлях до PNG/ICO (опційно)
        """
        if icon_path and not os.path.isabs(icon_path):
            icon_path = os.path.abspath(icon_path)
        icon_xml = f"<image placement='appLogoOverride' src='{icon_path}'/>" if icon_path else ""

        xml_str = f"""
        <toast>
            <visual>
                <binding template='ToastGeneric'>
                    <text>{title}</text>
                    <text>{message}</text>
                    {icon_xml}
                </binding>
            </visual>
        </toast>
        """

        try:
            xml_doc = XmlDocument()
            xml_doc.load_xml(xml_str)

            toast = ToastNotification(xml_doc)

            # Виклик без AppID → працює у Python без помилок
            notifier = ToastNotificationManager.create_toast_notifier()
            notifier.show(toast)
            print(f"[WinRTNotifier] Toast надіслано: {title} — {message}")

        except Exception as e:
            print(f"[WinRTNotifier Error] {e}")


# ====== Приклад використання ======
if __name__ == "__main__":
    notifier = WinRTNotifier()

    # Повідомлення з кастомною іконкою
    notifier.send_toast(
        "Інформація",
        "Програма запущена успішно!",
        icon_path="E:\\onedrive\\pysoft\\!ndic8tr\\images\\icons\\github-16.png"
    )

    notifier.send_toast(
        "Попередження",
        "Будьте обережні!",
        icon_path="E:\\onedrive\\pysoft\\!ndic8tr\\images\\icons\\warning-16.png"
    )
