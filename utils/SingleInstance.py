import win32event
import win32api
import winerror

class SingleInstance:
    """Запобігає запуску більше ніж одного екземпляра програми."""

    def __init__(self, name: str):
        self.mutexname = name
        self.handle = win32event.CreateMutex(None, False, self.mutexname)
        self.already_running = (win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS)

    def __del__(self):
        if self.handle:
            win32api.CloseHandle(self.handle)
            self.handle = None