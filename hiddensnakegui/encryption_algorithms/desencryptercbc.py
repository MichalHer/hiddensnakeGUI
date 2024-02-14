from hiddensnake.encryption_algorithms import DESEncrypterCBC as BaseDES
from tkinter.simpledialog import askstring

class DESEncrypterCBC(BaseDES):
    def display_password_request(self):
        password = askstring("Password", prompt="Enter password", show="*")
        self.set_password(password)