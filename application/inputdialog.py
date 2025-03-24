import customtkinter as ctk
from typing import Any

class PasswordInputDialog(ctk.CTkToplevel):
    def __init__(self, parent: Any):
        super().__init__(parent)
        self.geometry("300x150")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.title("Master password required")
        
        self.result = None
        
        self.label = ctk.CTkLabel(self, text="Enter your master password:")
        self.label.pack(pady=10)

        self.password_input = ctk.CTkEntry(self, show="*")
        self.password_input.pack(pady=5)
        
        self.submit_button = ctk.CTkButton(self, text="Submit", command=self.handle_password_submit)
        self.submit_button.pack(side="left", padx=5)

        self.cancel_button = ctk.CTkButton(self, text="Cancel", command=self.handle_cancel)
        self.cancel_button.pack(side="left", padx=5)

    def handle_password_submit(self) -> None:
        self.result = self.password_input.get()
        self.destroy()

    def handle_cancel(self) -> None:
        self.result = None
        self.destroy()

    @staticmethod
    def get_input(parent: Any) -> str | None:
        popup = PasswordInputDialog(parent)
        parent.wait_window(popup)
        return popup.result